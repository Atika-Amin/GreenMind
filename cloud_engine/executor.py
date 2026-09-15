"""
CloudExecutor: the piece that actually runs a prompt on Gemini once
GreenMind's WorkloadRouter has decided the task needs cloud execution.

Mirrors local_engine.LocalExecutor's shape on purpose, so the two engines
are interchangeable from the caller's point of view: same .run(prompt,
profile) / .run_from_decision(decision) API, same "typed result object"
pattern.
"""

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional, TYPE_CHECKING

from .exceptions import GeminiConfigError, GeminiGenerationError
from .gemini_client import GeminiClient

if TYPE_CHECKING:
    # Adjust these to match your actual package layout, e.g.:
    #   from backend.prompt_analyzer import PromptComplexityProfile
    #   from backend.workload_router import RoutingDecision
    from prompt_analyzer import PromptComplexityProfile
    from workload_router import RoutingDecision


@dataclass
class CloudExecutionResult:
    success: bool
    model_used: Optional[str]
    response_text: Optional[str]

    # Measured figures from Gemini's own usage_metadata
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    latency_s: Optional[float] = None

    # Gemini's own "why did generation stop" signal - "STOP" is normal
    # completion, "MAX_TOKENS" means it hit the token budget and got cut off.
    finish_reason: Optional[str] = None

    error: Optional[str] = None
    raw_usage: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CloudExecutor:
    def __init__(self, client: Optional[GeminiClient] = None):
        # Building the client can fail (missing API key). We defer that
        # failure to the first .run() call instead of raising at
        # construction time, so instantiating a CloudExecutor never
        # crashes your app - you only see the error when you try to use it.
        self._init_error: Optional[str] = None
        try:
            self.client: Optional[GeminiClient] = client or GeminiClient()
        except GeminiConfigError as exc:
            self.client = None
            self._init_error = str(exc)

    def run(
        self,
        prompt: str,
        prompt_profile: Optional["PromptComplexityProfile"] = None,
        generation_config_override: Optional[Dict[str, Any]] = None,
    ) -> CloudExecutionResult:
        """Core entry point. `prompt_profile` is accepted for symmetry with
        LocalExecutor.run() and future use (e.g. per-tier generation
        settings) but isn't required to make the call.

        `generation_config_override` merges over the client's default
        config for this call only - used by the feedback loop to retry
        with e.g. thinking disabled after a truncated first attempt."""

        if self.client is None:
            return CloudExecutionResult(
                success=False, model_used=None, response_text=None, error=self._init_error
            )

        start = time.perf_counter()
        try:
            response = self.client.generate(prompt, generation_config=generation_config_override)
        except GeminiGenerationError as exc:
            return CloudExecutionResult(
                success=False, model_used=self.client.model, response_text=None, error=str(exc)
            )
        latency_s = time.perf_counter() - start

        return self._build_result(response, latency_s)

    def run_from_decision(
        self, decision: "RoutingDecision", generation_config_override: Optional[Dict[str, Any]] = None
    ) -> CloudExecutionResult:
        """Convenience wrapper around a full workload_router.RoutingDecision.
        Trusts the router: refuses if it already decided local execution
        was fine, so you don't spend Gemini quota on a task that didn't
        need the cloud."""

        if decision.can_execute_locally:
            return CloudExecutionResult(
                success=False,
                model_used=None,
                response_text=None,
                error=(
                    "RoutingDecision says this task can run locally - "
                    "use local_engine.LocalExecutor instead."
                ),
            )

        prompt_profile = decision.prompt_profile
        return self.run(prompt_profile.prompt, prompt_profile, generation_config_override=generation_config_override)

    def _build_result(self, response: Any, latency_s: float) -> CloudExecutionResult:
        usage = getattr(response, "usage_metadata", None)

        prompt_tokens = getattr(usage, "prompt_token_count", None) if usage else None
        completion_tokens = getattr(usage, "candidates_token_count", None) if usage else None
        total_tokens = getattr(usage, "total_token_count", None) if usage else None

        candidates = getattr(response, "candidates", None) or []
        finish_reason = None
        if candidates:
            raw_reason = getattr(candidates[0], "finish_reason", None)
            finish_reason = getattr(raw_reason, "value", raw_reason)  # enum -> plain string

        raw_usage: Dict[str, Any] = {}
        if usage is not None:
            try:
                raw_usage = usage.model_dump()
            except AttributeError:
                raw_usage = {
                    "prompt_token_count": prompt_tokens,
                    "candidates_token_count": completion_tokens,
                    "total_token_count": total_tokens,
                }

        return CloudExecutionResult(
            success=True,
            model_used=self.client.model,
            response_text=getattr(response, "text", None),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_s=round(latency_s, 3),
            finish_reason=finish_reason,
            raw_usage=raw_usage,
        )

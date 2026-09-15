"""
LocalExecutor: the piece that actually runs a prompt on-device once
GreenMind's WorkloadRouter has decided the task belongs locally.

Plugs into your existing backend without changing it. Feed it either:
  - a prompt string + its PromptComplexityProfile, via .run(), or
  - a full RoutingDecision from workload_router.py, via .run_from_decision()

It picks an installed Ollama model matching the tier PromptAnalyzer
assigned, runs the generation, and returns a LocalExecutionResult with
both the model's answer and Ollama's real timing/token metadata.
"""

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional, TYPE_CHECKING

from .config import AUTO_PULL_MISSING_MODELS, DEFAULT_GENERATION_OPTIONS
from .exceptions import LocalGenerationError, OllamaConnectionError
from .model_registry import all_candidate_tags, resolve_model
from .ollama_client import OllamaClient

if TYPE_CHECKING:
    # Adjust these two imports to match your actual package layout, e.g.:
    #   from backend.prompt_analyzer import PromptComplexityProfile
    #   from backend.workload_router import RoutingDecision
    from prompt_analyzer import PromptComplexityProfile
    from workload_router import RoutingDecision


@dataclass
class LocalExecutionResult:
    success: bool
    model_used: Optional[str]
    response_text: Optional[str]

    # Measured (not estimated) figures, straight from Ollama
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_duration_s: Optional[float] = None
    load_duration_s: Optional[float] = None
    eval_duration_s: Optional[float] = None
    tokens_per_second: Optional[float] = None

    # Ollama's own "why did generation stop" signal - "stop" is normal
    # completion, "length" means it hit num_predict and got cut off.
    finish_reason: Optional[str] = None

    error: Optional[str] = None
    raw_ollama_response: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LocalExecutor:
    def __init__(self, client: Optional[OllamaClient] = None, auto_pull: bool = AUTO_PULL_MISSING_MODELS):
        self.client = client or OllamaClient()
        self.auto_pull = auto_pull

    def run(
        self,
        prompt: str,
        prompt_profile: "PromptComplexityProfile",
        options_override: Optional[Dict[str, Any]] = None,
    ) -> LocalExecutionResult:
        """Core entry point: run `prompt` locally using the tier/models
        PromptAnalyzer already assigned to it in `prompt_profile`.

        `options_override` merges over DEFAULT_GENERATION_OPTIONS for this
        call only - used by the feedback loop to retry with e.g. a bigger
        num_predict after a truncated first attempt, without changing the
        default for every other request."""

        try:
            installed = self.client.list_installed_models()
        except OllamaConnectionError as exc:
            return LocalExecutionResult(
                success=False, model_used=None, response_text=None, error=str(exc)
            )

        model_tag = resolve_model(
            prompt_profile.target_model_tier,
            prompt_profile.recommended_models,
            installed,
        )

        if model_tag is None:
            if self.auto_pull:
                model_tag = self._try_pull_any(prompt_profile)
            if model_tag is None:
                candidates = all_candidate_tags(
                    prompt_profile.target_model_tier, prompt_profile.recommended_models
                )
                return LocalExecutionResult(
                    success=False,
                    model_used=None,
                    response_text=None,
                    error=(
                        f"No installed Ollama model matches tier "
                        f"'{prompt_profile.target_model_tier}'. Pull one of: "
                        f"{', '.join(candidates)} (e.g. `ollama pull {candidates[0]}`)."
                    ),
                )

        options = {**DEFAULT_GENERATION_OPTIONS, **(options_override or {})}

        start = time.perf_counter()
        try:
            raw = self.client.generate(
                model=model_tag,
                prompt=prompt,
                options=options,
            )
        except LocalGenerationError as exc:
            return LocalExecutionResult(
                success=False, model_used=model_tag, response_text=None, error=str(exc)
            )
        wall_time = time.perf_counter() - start

        return self._build_result(model_tag, raw, wall_time)

    def run_from_decision(
        self, decision: "RoutingDecision", options_override: Optional[Dict[str, Any]] = None
    ) -> LocalExecutionResult:
        """Convenience wrapper around a full workload_router.RoutingDecision.
        Trusts the router's decision as authoritative - if it already says
        cloud is needed, this refuses rather than second-guessing it."""

        if not decision.can_execute_locally:
            return LocalExecutionResult(
                success=False,
                model_used=None,
                response_text=None,
                error=(
                    "RoutingDecision says cloud execution is required "
                    f"(reasons: {'; '.join(decision.reasons)})."
                ),
            )

        prompt_profile = decision.prompt_profile
        return self.run(prompt_profile.prompt, prompt_profile, options_override=options_override)

    def _try_pull_any(self, prompt_profile: "PromptComplexityProfile") -> Optional[str]:
        candidates = all_candidate_tags(
            prompt_profile.target_model_tier, prompt_profile.recommended_models
        )
        for tag in candidates:
            try:
                self.client.pull_model(tag)
                return tag
            except LocalGenerationError:
                continue  # try the next candidate
        return None

    @staticmethod
    def _build_result(model_tag: str, raw: Dict[str, Any], wall_time_s: float) -> LocalExecutionResult:
        prompt_tokens = raw.get("prompt_eval_count")
        completion_tokens = raw.get("eval_count")

        eval_duration_s = raw.get("eval_duration", 0) / 1e9 if raw.get("eval_duration") else None
        load_duration_s = raw.get("load_duration", 0) / 1e9 if raw.get("load_duration") else None
        total_duration_s = (
            raw.get("total_duration", 0) / 1e9 if raw.get("total_duration") else wall_time_s
        )

        tokens_per_second = None
        if completion_tokens and eval_duration_s:
            tokens_per_second = round(completion_tokens / eval_duration_s, 2)

        return LocalExecutionResult(
            success=True,
            model_used=model_tag,
            response_text=raw.get("response", ""),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_duration_s=round(total_duration_s, 3) if total_duration_s is not None else None,
            load_duration_s=round(load_duration_s, 3) if load_duration_s is not None else None,
            eval_duration_s=round(eval_duration_s, 3) if eval_duration_s is not None else None,
            tokens_per_second=tokens_per_second,
            finish_reason=raw.get("done_reason"),
            raw_ollama_response=raw,
        )

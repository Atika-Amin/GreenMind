"""
Feedback Loop for GreenMind (Phases C + D).

Runs the engine WorkloadRouter picked, verifies the result, and - only if
verification fails - takes one of two bounded actions:
  1. If the failure was truncation: retry the SAME engine once with a
     boosted token budget (Phase C: Response Optimization).
  2. If it's still failing after that (or failed for a non-truncation
     reason): escalate to the OTHER engine, once (Phase D: the actual
     feedback loop).

Local -> Cloud escalation is allowed (cloud is presumed capable of
anything). Cloud -> Local is not - if cloud is failing, a smaller local
model won't fix it, so that result is returned best-effort with a flag
instead. Total executions per request are capped at 2, so nothing can
loop indefinitely no matter how it fails.
"""

from typing import Any, Dict, List, Optional, Tuple

from optimization.quality_verifier import verify

# Retry overrides applied only on the bounded Phase C retry, never on the
# first attempt - keeps default behavior/cost unchanged for the common case.
LOCAL_RETRY_OPTIONS = {"num_predict": 1536}  # roughly 3x the default 512
CLOUD_RETRY_CONFIG = {
    "max_output_tokens": 8192,
    "thinking_config": {"thinking_budget": 0},  # guarantee the budget goes to the visible answer
}


def run_with_feedback(
    decision: Any,
    local_executor: Any,
    cloud_executor: Any,
) -> Tuple[Dict[str, Any], str, List[Dict[str, Any]]]:
    """
    decision: RoutingDecision from WorkloadRouter.route()
    local_executor / cloud_executor: your LocalExecutor / CloudExecutor instances

    Returns (execution_result_dict, engine_used, attempts_log).
    attempts_log records every execution tried, for transparency in the
    API response and as the data Phase E would eventually learn from.
    """
    attempts: List[Dict[str, Any]] = []

    primary_engine = "local" if decision.can_execute_locally else "cloud"
    result = _run_engine(primary_engine, decision, local_executor, cloud_executor)
    result_dict = result.to_dict()
    verdict = verify(result_dict)
    attempts.append({"engine": primary_engine, "verdict": verdict, "retry": False, "escalated": False})

    if verdict["passed"]:
        return result_dict, primary_engine, attempts

    # Phase C: one bounded retry, same engine, only worth trying for
    # truncation - other failure modes (refusal, error) won't be fixed by
    # a bigger token budget.
    if verdict["truncated"]:
        retry_result = _run_engine(
            primary_engine, decision, local_executor, cloud_executor, boosted=True
        )
        retry_dict = retry_result.to_dict()
        retry_verdict = verify(retry_dict)
        attempts.append({"engine": primary_engine, "verdict": retry_verdict, "retry": True, "escalated": False})

        if retry_verdict["passed"]:
            return retry_dict, primary_engine, attempts

        result_dict, verdict = retry_dict, retry_verdict  # carry the better of the two forward

    # Phase D: escalate, but only local -> cloud. A struggling cloud
    # response won't be fixed by falling back to a smaller local model.
    if primary_engine == "local":
        escalated_result = _run_engine("cloud", decision, local_executor, cloud_executor)
        escalated_dict = escalated_result.to_dict()
        escalated_verdict = verify(escalated_dict)
        attempts.append({"engine": "cloud", "verdict": escalated_verdict, "retry": False, "escalated": True})
        return escalated_dict, "cloud", attempts

    # Cloud already failed (and retried, if truncation) - return its best
    # attempt rather than looping into local, which we already know can't
    # meet this task's requirements per the router's own decision.
    return result_dict, primary_engine, attempts


def _run_engine(
    engine: str,
    decision: Any,
    local_executor: Any,
    cloud_executor: Any,
    boosted: bool = False,
) -> Any:
    if engine == "local":
        options = LOCAL_RETRY_OPTIONS if boosted else None
        prompt_profile = decision.prompt_profile
        return local_executor.run(prompt_profile.prompt, prompt_profile, options_override=options)

    config = CLOUD_RETRY_CONFIG if boosted else None
    prompt_profile = decision.prompt_profile
    return cloud_executor.run(prompt_profile.prompt, prompt_profile, generation_config_override=config)

"""
Quality Verification for GreenMind's feedback layer (Phase A).

Deterministic checks on a real execution result - no second model call,
no LLM-as-judge. Looks at signals both engines now expose: whether
execution succeeded at all, whether the response is empty, whether the
model's own "why did I stop" signal indicates truncation, and a short
list of refusal phrases. Returns a verdict the feedback loop can act on.
"""

from typing import Any, Dict, List

# Ollama's done_reason uses "length"; Gemini's finish_reason uses
# "MAX_TOKENS" - both mean the same thing: cut off by the token budget,
# not because the model was actually finished.
TRUNCATION_REASONS = {"length", "MAX_TOKENS"}

# Short, conservative list - only phrases a model uses when declining
# outright, not ordinary hedging language a legitimate answer might contain.
REFUSAL_PHRASES = [
    "i cannot help with that",
    "i can't help with that",
    "i cannot assist with that",
    "i'm not able to help with that",
    "i am not able to help with that",
]


def verify(execution_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    execution_result: dict - the .to_dict() output from whichever engine ran

    Returns:
        {
            "passed": bool,
            "issues": [str, ...],   # human-readable, same style as RoutingDecision.reasons
            "truncated": bool,      # specifically flagged - Phase C cares about this one
        }
    """
    issues: List[str] = []

    if not execution_result.get("success"):
        issues.append(f"Execution failed: {execution_result.get('error')}")
        return {"passed": False, "issues": issues, "truncated": False}

    text = (execution_result.get("response_text") or "").strip()
    finish_reason = execution_result.get("finish_reason")
    truncated = finish_reason in TRUNCATION_REASONS

    if not text:
        issues.append("Empty response")

    if truncated:
        issues.append(f"Response was cut off before finishing (finish_reason: {finish_reason})")

    lowered = text.lower()
    for phrase in REFUSAL_PHRASES:
        if phrase in lowered:
            issues.append("Model declined to answer")
            break

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "truncated": truncated,
    }

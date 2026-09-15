"""
Maps the abstract model names produced by PromptAnalyzer (Task Analysis
Engine) onto real, pullable Ollama model tags.

PromptAnalyzer reasons in terms of tiers ("Standard Local LLM (7B-8B)",
"Compact SLM (1.5B-3.8B)", "Micro SLM") and a short list of recommended
model names per tier. Those names are illustrative labels, not Ollama
tags - this module is the translation layer between the two, and the
only place that mapping lives, so it's easy to update as Ollama's
library changes without touching prompt_analyzer.py.
"""

from typing import Dict, Iterable, List, Optional

# canonical recommended-model-name -> ordered list of Ollama tag candidates
# (most specific/quantized first, most generic fallback last)
MODEL_TAG_CANDIDATES: Dict[str, List[str]] = {
    # --- Standard Local LLM (7B-8B) ---
    "Llama-3.1-8B-Q4": ["llama3.1:8b-instruct-q4_K_M", "llama3.1:8b", "llama3.1"],
    "Mistral-7B-Instruct-Q4": ["mistral:7b-instruct-q4_K_M", "mistral:7b", "mistral"],
    "Qwen2.5-7B-Instruct-Q4": ["qwen2.5:7b-instruct-q4_K_M", "qwen2.5:7b"],

    # --- Compact SLM (1.5B-3.8B) ---
    "Llama-3.2-3B-Q4": ["llama3.2:3b-instruct-q4_K_M", "llama3.2:3b", "llama3.2"],
    "Phi-3.5-mini": ["phi3.5:3.8b-mini-instruct-q4_K_M", "phi3.5"],
    "Qwen2.5-1.5B": ["qwen2.5:1.5b-instruct-q4_K_M", "qwen2.5:1.5b"],

    # --- Micro SLM ---
    # SmolLM2 is the closest real generative model to the paper's "SmolLM".
    "SmolLM": ["smollm2:1.7b", "smollm2:360m", "smollm2"],
    # NOTE: TinyBERT is an encoder-only classification/distillation model -
    # it has no generative/chat variant, so it literally cannot serve a
    # prompt. We substitute the smallest sensible generative model so the
    # pipeline still runs; worth flagging as a known limitation of the
    # Micro SLM tier in the paper rather than implying TinyBERT wrote text.
    "TinyBERT": ["qwen2.5:0.5b", "smollm2:135m"],
}

# Generic fallback per tier, used only if every recommended-model lookup
# for that tier misses (nothing from the list is pulled at all). This lets
# the engine degrade to *something* runnable instead of hard-failing.
TIER_FALLBACKS: Dict[str, List[str]] = {
    "Standard Local LLM (7B-8B)": ["llama3.1:8b", "mistral", "qwen2.5:7b"],
    "Compact SLM (1.5B-3.8B)": ["llama3.2:3b", "phi3.5", "qwen2.5:1.5b"],
    "Micro SLM": ["qwen2.5:0.5b", "smollm2:135m"],
}


def resolve_model(
    target_model_tier: str,
    recommended_models: Iterable[str],
    installed_tags: Iterable[str],
) -> Optional[str]:
    """
    Pick the best Ollama tag to serve a prompt, given what's actually
    installed locally.

    Walks `recommended_models` in the order PromptAnalyzer supplied them,
    and for each tries its candidate tags in order, returning the first
    one that's installed. Falls back to the tier's generic list if none
    of the recommended models are present. Returns None if nothing in
    the tier is available at all.
    """
    installed = set(installed_tags)

    for canonical_name in recommended_models:
        for tag in MODEL_TAG_CANDIDATES.get(canonical_name, []):
            if tag in installed:
                return tag

    for tag in TIER_FALLBACKS.get(target_model_tier, []):
        if tag in installed:
            return tag

    return None


def all_candidate_tags(target_model_tier: str, recommended_models: Iterable[str]) -> List[str]:
    """Every tag worth `ollama pull`-ing for a tier - used in error
    messages so the user knows exactly what to fetch."""
    tags: List[str] = []
    for canonical_name in recommended_models:
        tags.extend(MODEL_TAG_CANDIDATES.get(canonical_name, []))
    tags.extend(TIER_FALLBACKS.get(target_model_tier, []))

    seen = set()
    ordered = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            ordered.append(t)
    return ordered

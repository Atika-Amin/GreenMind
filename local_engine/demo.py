"""
Standalone smoke test for the Local Engine.

Deliberately doesn't need device_profiler or workload_router wired up -
just prompt_analyzer.py (Task Analysis Engine) and a running Ollama.
Good for checking local_engine works before you plug it into the router.

Prereqs:
    1. `ollama serve` running (or the Ollama desktop app open)
    2. At least one model pulled, e.g.: ollama pull llama3.2:3b

Run from your project root:
    python -m local_engine.demo
"""

import os
import sys

# Make sure your existing modules are importable regardless of where this
# is run from. Adjust the import below if prompt_analyzer.py lives in a
# subpackage (e.g. `from backend.prompt_analyzer import PromptAnalyzer`).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from prompt_analyzer import PromptAnalyzer
except ImportError as exc:
    raise ImportError(
        "Could not import PromptAnalyzer. Edit the import in local_engine/demo.py "
        "to match where prompt_analyzer.py actually lives in your project."
    ) from exc

from local_engine import LocalExecutor


def main() -> None:
    analyzer = PromptAnalyzer()
    executor = LocalExecutor()

    prompt = "Explain how binary search works, step by step."
    profile = analyzer.analyze(prompt)

    print(f"Task category : {profile.task_category}")
    print(f"Target tier   : {profile.target_model_tier}")
    print(f"S_required    : {profile.s_required}")
    print(f"Recommended   : {profile.recommended_models}")
    print("-" * 60)

    result = executor.run(prompt, profile)

    if not result.success:
        print(f"Local execution failed: {result.error}")
        return

    preview = (result.response_text or "")[:300]
    print(f"Model used         : {result.model_used}")
    print(f"Response (preview) : {preview}...")
    print(f"Prompt tokens      : {result.prompt_tokens}")
    print(f"Completion tokens  : {result.completion_tokens}")
    print(f"Total duration (s) : {result.total_duration_s}")
    print(f"Tokens/sec         : {result.tokens_per_second}")


if __name__ == "__main__":
    main()

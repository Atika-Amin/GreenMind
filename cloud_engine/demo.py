"""
Standalone smoke test for the Cloud Engine.

Deliberately doesn't need device_profiler or workload_router wired up -
just prompt_analyzer.py (Task Analysis Engine) and a Gemini API key.

Prereqs:
    1. pip install google-genai
    2. export GEMINI_API_KEY=your_key_here   (free key: https://aistudio.google.com/apikey)

Run from your project root:
    python -m cloud_engine.demo
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
        "Could not import PromptAnalyzer. Edit the import in cloud_engine/demo.py "
        "to match where prompt_analyzer.py actually lives in your project."
    ) from exc

from cloud_engine import CloudExecutor


def main() -> None:
    analyzer = PromptAnalyzer()
    executor = CloudExecutor()

    prompt = (
        "Design a distributed system architecture for a real-time "
        "ride-sharing platform, with tradeoffs explained step by step."
    )
    profile = analyzer.analyze(prompt)

    print(f"Task category : {profile.task_category}")
    print(f"Target tier   : {profile.target_model_tier}")
    print(f"S_required    : {profile.s_required}")
    print("-" * 60)

    result = executor.run(prompt, profile)

    if not result.success:
        print(f"Cloud execution failed: {result.error}")
        return

    preview = (result.response_text or "")[:300]
    print(f"Model used         : {result.model_used}")
    print(f"Response (preview) : {preview}...")
    print(f"Prompt tokens      : {result.prompt_tokens}")
    print(f"Completion tokens  : {result.completion_tokens}")
    print(f"Total tokens       : {result.total_tokens}")
    print(f"Latency (s)        : {result.latency_s}")


if __name__ == "__main__":
    main()

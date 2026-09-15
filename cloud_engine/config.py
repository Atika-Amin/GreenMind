"""
Configuration for the GreenMind Cloud Engine (Gemini integration).
"""

import os
from typing import Optional

# Get a free key at https://aistudio.google.com/apikey and set it as an
# environment variable rather than hardcoding it here.
GEMINI_API_KEY: Optional[str] = os.environ.get("GEMINI_API_KEY")

# Override with GEMINI_MODEL env var if you ever want to swap models
# without touching code.
MODEL_NAME: str = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# Request timeout in milliseconds (the SDK's HttpOptions.timeout is in ms).
REQUEST_TIMEOUT_MS: int = 60_000

# Passed straight into types.GenerateContentConfig(**this) for every call.
DEFAULT_GENERATION_CONFIG: dict = {
    "temperature": 0.7,
    "max_output_tokens": 8192,
}

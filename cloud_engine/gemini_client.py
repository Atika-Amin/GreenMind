"""
Thin wrapper around Google's Gen AI SDK for Gemini.

Requires:  pip install google-genai
API key:   set the GEMINI_API_KEY environment variable
           (get a free one at https://aistudio.google.com/apikey)
"""

from typing import Any, Dict, Optional

from .config import DEFAULT_GENERATION_CONFIG, GEMINI_API_KEY, MODEL_NAME, REQUEST_TIMEOUT_MS
from .exceptions import GeminiConfigError, GeminiGenerationError

try:
    from google import genai
    from google.genai import types
except ImportError as exc:
    raise ImportError(
        "google-genai isn't installed. Run: pip install google-genai"
    ) from exc


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model: str = MODEL_NAME):
        key = api_key or GEMINI_API_KEY
        if not key:
            raise GeminiConfigError(
                "No Gemini API key found. Set the GEMINI_API_KEY environment "
                "variable (get a free key at https://aistudio.google.com/apikey)."
            )

        self.model = model
        self._client = genai.Client(
            api_key=key,
            http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS),
        )

    def generate(self, prompt: str, generation_config: Optional[Dict[str, Any]] = None) -> Any:
        """Returns the raw google-genai response object (has .text and
        .usage_metadata) so the executor can pull real token counts out
        of it."""
        config = {**DEFAULT_GENERATION_CONFIG, **(generation_config or {})}

        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(**config),
            )
        except Exception as exc:
            # The SDK raises several distinct error types (auth, quota,
            # network, safety blocks) - collapsing to one is fine here
            # since the message is preserved and callers just need pass/fail.
            raise GeminiGenerationError(f"Gemini request failed: {exc}") from exc

        return response

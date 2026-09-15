"""Custom exceptions for the GreenMind Cloud Engine."""


class GeminiConfigError(Exception):
    """Raised when the client can't be built - typically a missing API key."""


class GeminiGenerationError(Exception):
    """Raised when the Gemini API call itself fails (network, auth, quota,
    safety block, etc.)."""

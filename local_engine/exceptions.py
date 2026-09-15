"""Custom exceptions for the GreenMind Local Engine."""


class OllamaConnectionError(Exception):
    """Raised when the local Ollama server cannot be reached at all."""


class ModelNotAvailableError(Exception):
    """Raised when none of the candidate models for a tier are installed
    in the local Ollama instance and auto-pull is disabled or failed."""


class LocalGenerationError(Exception):
    """Raised when Ollama itself errors out while pulling or generating."""

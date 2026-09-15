"""
Configuration for the GreenMind Local Engine (Ollama integration).
Adjust these values to match your local Ollama installation and hardware.
"""

import os

# Ollama server location (default local install)
OLLAMA_HOST: str = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# Network timeouts (seconds)
CONNECT_TIMEOUT: float = 5.0
GENERATE_TIMEOUT: float = 120.0

# If True, the executor will attempt `ollama pull <model>` automatically
# when the selected model isn't present locally yet. Keep this False on a
# constrained/offline edge device and pull models manually ahead of time -
# an unplanned multi-GB pull in the middle of a "local execution" defeats
# the point of the green/edge comparison in the paper.
AUTO_PULL_MISSING_MODELS: bool = False

# Default generation options passed to Ollama for every request.
# num_predict caps output length so local runs stay fast/comparable on
# constrained edge hardware - raise it if your device can afford longer
# generations.
DEFAULT_GENERATION_OPTIONS: dict = {
    "temperature": 0.7,
    "num_predict": 512,
}

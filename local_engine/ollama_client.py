"""
Thin REST client for a local Ollama server.

Talks to the standard Ollama HTTP API (default http://localhost:11434).
No extra Ollama SDK dependency - just `requests`.
"""

from typing import Any, Dict, List, Optional

import requests

from .config import CONNECT_TIMEOUT, GENERATE_TIMEOUT, OLLAMA_HOST
from .exceptions import LocalGenerationError, OllamaConnectionError


class OllamaClient:
    def __init__(self, host: str = OLLAMA_HOST):
        self.host = host.rstrip("/")

    def is_reachable(self) -> bool:
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=CONNECT_TIMEOUT)
            return resp.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def list_installed_models(self) -> List[str]:
        """Tags of every model currently pulled into this Ollama instance."""
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=CONNECT_TIMEOUT)
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            raise OllamaConnectionError(
                f"Could not reach Ollama at {self.host}. "
                f"Is `ollama serve` running? ({exc})"
            ) from exc

        data = resp.json()
        return [m["name"] for m in data.get("models", [])]

    def pull_model(self, tag: str) -> None:
        """Blocking pull - can take minutes on first run of a new model."""
        try:
            resp = requests.post(
                f"{self.host}/api/pull",
                json={"name": tag, "stream": False},
                timeout=None,  # pulling can legitimately take a long time
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            raise LocalGenerationError(f"Failed to pull model '{tag}': {exc}") from exc

    def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Calls Ollama's /api/generate (stream=False) and returns the raw
        JSON, which includes the generated text plus Ollama's own
        timing/token metadata:
          - response                : generated text
          - total_duration          : ns, full request wall time
          - load_duration           : ns, time spent loading the model
          - prompt_eval_count       : tokens in the prompt
          - prompt_eval_duration    : ns
          - eval_count              : tokens generated
          - eval_duration           : ns, time spent generating

        These are *measured* figures - useful to compare against
        energy_decision.py's *estimated* local_energy for the paper.
        """
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system
        if options:
            payload["options"] = options

        try:
            resp = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=GENERATE_TIMEOUT,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            raise LocalGenerationError(
                f"Ollama generation failed for model '{model}': {exc}"
            ) from exc

        return resp.json()

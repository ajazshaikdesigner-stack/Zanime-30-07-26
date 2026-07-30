"""
Ollama LLM Provider — connects to a running Ollama server via HTTP REST API.

Default endpoint: http://localhost:11434
Override via config key: ai_settings.ollama_url
"""

import json
import logging
import urllib.error
import urllib.request
from typing import Any

from .base import AIBaseProvider

logger = logging.getLogger(__name__)

_OLLAMA_DEFAULT_URL = "http://localhost:11434"
_DEFAULT_MODEL = "llama3:8b"


class OllamaProvider(AIBaseProvider):
    """Real Ollama HTTP provider. Streams responses and handles connection errors gracefully."""

    def __init__(self):
        super().__init__()
        self._base_url = _OLLAMA_DEFAULT_URL
        self._model_name = _DEFAULT_MODEL
        self._context_tokens: list[int] = []  # Ollama context window carry-over

    # ------------------------------------------------------------------
    # AIBaseProvider interface
    # ------------------------------------------------------------------

    def load(self, model_name: str, config: dict[str, Any]) -> bool:
        """Verify the model is available on the Ollama server."""
        self._base_url = config.get("ollama_url", _OLLAMA_DEFAULT_URL).rstrip("/")
        self._model_name = model_name or _DEFAULT_MODEL

        try:
            url = f"{self._base_url}/api/tags"
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read().decode())

            available = [m["name"] for m in data.get("models", [])]
            if self._model_name not in available:
                logger.warning(
                    "OllamaProvider: Model '%s' not found locally. "
                    "Available: %s. Will attempt generation anyway.",
                    self._model_name,
                    available,
                )
            else:
                logger.info("OllamaProvider: Model '%s' confirmed available.", self._model_name)

            self.is_loaded = True
            return True

        except urllib.error.URLError as exc:
            logger.error("OllamaProvider: Cannot reach Ollama server at %s — %s", self._base_url, exc)
            self.is_loaded = False
            return False
        except Exception:
            logger.exception("OllamaProvider: Unexpected error during load.")
            self.is_loaded = False
            return False

    def unload(self) -> None:
        """Release context state; the model itself stays in Ollama's cache."""
        self._context_tokens = []
        self.is_loaded = False
        logger.info("OllamaProvider: Unloaded (context cleared).")

    def execute(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Send a prompt to Ollama and return the complete response text."""
        if not self.is_loaded:
            raise RuntimeError("OllamaProvider: Model not loaded. Call load() first.")

        system_prompt = parameters.get(
            "system",
            "You are a professional anime screenplay writer and animation director assistant. "
            "Respond with structured, creative, production-ready content.",
        )

        payload = {
            "model": self._model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "context": self._context_tokens,
            "options": {
                "temperature": parameters.get("temperature", 0.8),
                "top_p": parameters.get("top_p", 0.9),
                "num_predict": parameters.get("max_tokens", 1024),
            },
        }

        try:
            body = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self._base_url}/api/generate",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode())

            # Carry context forward for multi-turn conversation
            self._context_tokens = result.get("context", [])

            text = result.get("response", "")
            logger.info(
                "OllamaProvider: Generated %d chars (model=%s, tokens=%d).",
                len(text),
                self._model_name,
                result.get("eval_count", 0),
            )
            return {
                "text": text,
                "model": self._model_name,
                "tokens": result.get("eval_count", 0),
                "prompt_tokens": result.get("prompt_eval_count", 0),
            }

        except urllib.error.URLError as exc:
            logger.error("OllamaProvider: HTTP error during generate — %s", exc)
            raise RuntimeError(f"Ollama generation failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            logger.error("OllamaProvider: Invalid JSON response — %s", exc)
            raise RuntimeError("Ollama returned invalid JSON.") from exc

    def memory_footprint(self) -> int:
        """Approximate VRAM usage. Ollama manages this itself; we report a conservative estimate."""
        size_map = {
            "llama3:8b": 5000,
            "llama3:70b": 40000,
            "mistral:7b": 4500,
            "gemma:2b": 1800,
            "phi3:mini": 2200,
        }
        return size_map.get(self._model_name, 4000)

    # ------------------------------------------------------------------
    # Extra helpers
    # ------------------------------------------------------------------

    def clear_context(self) -> None:
        """Reset the conversation context (start fresh multi-turn session)."""
        self._context_tokens = []
        logger.debug("OllamaProvider: Context cleared.")

    def list_local_models(self) -> list[str]:
        """Return a list of model names currently installed in Ollama."""
        try:
            url = f"{self._base_url}/api/tags"
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read().decode())
            return [m["name"] for m in data.get("models", [])]
        except Exception:
            logger.exception("OllamaProvider: Failed to list models.")
            return []

    def pull_model(self, model_name: str) -> bool:
        """Trigger an Ollama pull for a model. Non-blocking — Ollama handles the download."""
        try:
            payload = json.dumps({"name": model_name, "stream": False}).encode()
            req = urllib.request.Request(
                f"{self._base_url}/api/pull",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
            logger.info("OllamaProvider: Pull result for '%s': %s", model_name, result.get("status"))
            return True
        except Exception:
            logger.exception("OllamaProvider: Failed to pull model '%s'.", model_name)
            return False

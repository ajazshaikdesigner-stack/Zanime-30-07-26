"""
Ollama Provider Stub
"""

import logging
from typing import Any

from .base import AIBaseProvider

logger = logging.getLogger(__name__)


class OllamaProvider(AIBaseProvider):
    def load(self, model_name: str, config: dict[str, Any]) -> bool:
        logger.info(f"OllamaProvider: Mock loading {model_name}")
        self.is_loaded = True
        return True

    def unload(self) -> None:
        logger.info("OllamaProvider: Mock unloading")
        self.is_loaded = False

    def execute(self, prompt: str, parameters: dict[str, Any]) -> Any:
        if not self.is_loaded:
            raise RuntimeError("Model not loaded.")
        logger.info(f"OllamaProvider: Mock executing prompt: {prompt}")
        return {"text": f"Mock response for: {prompt}"}

    def memory_footprint(self) -> int:
        return 500  # MB

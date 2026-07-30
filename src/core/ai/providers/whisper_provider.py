"""
Whisper Provider Stub
"""

import logging
from typing import Any

from .base import AIBaseProvider

logger = logging.getLogger(__name__)


class WhisperProvider(AIBaseProvider):
    def load(self, model_name: str, config: dict[str, Any]) -> bool:
        logger.info(f"WhisperProvider: Mock loading {model_name}")
        self.is_loaded = True
        return True

    def unload(self) -> None:
        logger.info("WhisperProvider: Mock unloading")
        self.is_loaded = False

    def execute(self, audio_path: str, parameters: dict[str, Any]) -> Any:
        if not self.is_loaded:
            raise RuntimeError("Model not loaded.")
        logger.info(f"WhisperProvider: Mock transcribing: {audio_path}")
        return {"text": "Mock transcription."}

    def memory_footprint(self) -> int:
        return 1000  # MB

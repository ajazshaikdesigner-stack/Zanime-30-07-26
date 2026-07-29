"""
Piper Provider Stub
"""
import logging
from typing import Dict, Any
from .base import AIBaseProvider

logger = logging.getLogger(__name__)

class PiperProvider(AIBaseProvider):
    def load(self, model_name: str, config: Dict[str, Any]) -> bool:
        logger.info(f"PiperProvider: Mock loading {model_name}")
        self.is_loaded = True
        return True
        
    def unload(self) -> None:
        logger.info("PiperProvider: Mock unloading")
        self.is_loaded = False
        
    def execute(self, text: str, parameters: Dict[str, Any]) -> Any:
        if not self.is_loaded:
            raise RuntimeError("Model not loaded.")
        logger.info(f"PiperProvider: Mock TTS: {text}")
        return {"audio_path": "mock_tts.wav"}
        
    def memory_footprint(self) -> int:
        return 500 # MB

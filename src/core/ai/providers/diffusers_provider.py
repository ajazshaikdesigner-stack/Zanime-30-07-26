"""
Diffusers Provider Stub
"""
import logging
from typing import Dict, Any
from .base import AIBaseProvider

logger = logging.getLogger(__name__)

class DiffusersProvider(AIBaseProvider):
    def load(self, model_name: str, config: Dict[str, Any]) -> bool:
        logger.info(f"DiffusersProvider: Mock loading {model_name}")
        self.is_loaded = True
        return True
        
    def unload(self) -> None:
        logger.info("DiffusersProvider: Mock unloading")
        self.is_loaded = False
        
    def execute(self, prompt: str, parameters: Dict[str, Any]) -> Any:
        if not self.is_loaded:
            raise RuntimeError("Model not loaded.")
        logger.info(f"DiffusersProvider: Mock executing image gen: {prompt}")
        return {"image_path": "mock_image.png"}
        
    def memory_footprint(self) -> int:
        return 2000 # MB

"""
Base interface for all AI Providers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class AIBaseProvider(ABC):
    def __init__(self):
        self.is_loaded = False
        
    @abstractmethod
    def load(self, model_name: str, config: Dict[str, Any]) -> bool:
        """Load the model into memory. Returns True if successful."""
        pass
        
    @abstractmethod
    def unload(self) -> None:
        """Unload the model from memory."""
        pass
        
    @abstractmethod
    def execute(self, prompt: str, parameters: Dict[str, Any]) -> Any:
        """Execute a generation task."""
        pass
        
    @abstractmethod
    def memory_footprint(self) -> int:
        """Return the estimated VRAM footprint in MB."""
        pass

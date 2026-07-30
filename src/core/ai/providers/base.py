"""
Base interface for all AI Providers.
"""

from abc import ABC, abstractmethod
from typing import Any


class AIBaseProvider(ABC):
    def __init__(self):
        self.is_loaded = False

    @abstractmethod
    def load(self, model_name: str, config: dict[str, Any]) -> bool:
        """Load the model into memory. Returns True if successful."""

    @abstractmethod
    def unload(self) -> None:
        """Unload the model from memory."""

    @abstractmethod
    def execute(self, prompt: str, parameters: dict[str, Any]) -> Any:
        """Execute a generation task."""

    @abstractmethod
    def memory_footprint(self) -> int:
        """Return the estimated VRAM footprint in MB."""

"""
Base interfaces for background services (Render, AI).
"""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class IService(ABC):
    """Interface for heavy, asynchronous background services."""

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

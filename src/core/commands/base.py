"""
Base definitions for the Command Pattern.
"""
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class ICommand(ABC):
    """Interface for all undoable commands in ZANIME."""

    @abstractmethod
    def execute(self) -> None:
        """Executes the command."""
        pass

    @abstractmethod
    def undo(self) -> None:
        """Reverts the execution of the command."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns a user-friendly name for the command (e.g., 'Move Layer')."""
        pass

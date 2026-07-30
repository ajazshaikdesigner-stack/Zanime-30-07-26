"""
Command Manager for Undo/Redo tracking.
"""

import logging

from src.core.commands.base import ICommand
from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event

logger = logging.getLogger(__name__)


class CommandManager:
    def __init__(self, event_bus: EventBus, max_history: int = 50):
        self.event_bus = event_bus
        self.max_history = max_history
        self._undo_stack: list[ICommand] = []
        self._redo_stack: list[ICommand] = []

    def execute(self, command: ICommand) -> None:
        """Executes a command and pushes it to the undo stack."""
        try:
            command.execute()
            self._undo_stack.append(command)
            self._redo_stack.clear()  # Clear redo stack on new action

            # Enforce max history to save RAM
            if len(self._undo_stack) > self.max_history:
                self._undo_stack.pop(0)

            logger.debug(f"Executed command: {command.name}")
        except Exception as e:
            logger.error(f"Failed to execute command {command.name}: {e}")

    def undo(self) -> None:
        """Pops the last command, undoes it, and pushes to redo stack."""
        if not self._undo_stack:
            return

        command = self._undo_stack.pop()
        try:
            command.undo()
            self._redo_stack.append(command)
            logger.debug(f"Undid command: {command.name}")
            self.event_bus.publish(Event.UNDO_EXECUTED)
        except Exception as e:
            logger.error(f"Failed to undo command {command.name}: {e}")

    def redo(self) -> None:
        """Pops the last undone command, executes it, and pushes to undo stack."""
        if not self._redo_stack:
            return

        command = self._redo_stack.pop()
        try:
            command.execute()
            self._undo_stack.append(command)
            logger.debug(f"Redid command: {command.name}")
            self.event_bus.publish(Event.REDO_EXECUTED)
        except Exception as e:
            logger.error(f"Failed to redo command {command.name}: {e}")

"""
Shortcut Manager for keybindings.
"""

import logging
from collections.abc import Callable

from src.core.events.event_bus import EventBus
from src.core.managers.configuration_manager import ConfigurationManager

logger = logging.getLogger(__name__)


class ShortcutManager:
    def __init__(self, event_bus: EventBus, config_manager: ConfigurationManager):
        self.event_bus = event_bus
        self.config_manager = config_manager
        self._shortcuts: dict[str, Callable] = {}
        self._bindings = self.config_manager.get("shortcuts", {})

    def register(
        self, action_name: str, default_chord: str, callback: Callable
    ) -> None:
        """Registers an action and its callback, using user config if available."""
        chord = self._bindings.get(action_name, default_chord)
        self._shortcuts[chord] = callback
        logger.debug(f"Registered shortcut: {action_name} -> {chord}")

    def rebind(self, action_name: str, new_chord: str) -> None:
        self._bindings[action_name] = new_chord
        self.config_manager.set_user("shortcuts", self._bindings)

    def handle_key(self, chord: str) -> bool:
        """Handles a key press and executes the callback if registered."""
        if chord in self._shortcuts:
            try:
                self._shortcuts[chord]()
                return True
            except Exception as e:  # noqa: BLE001
                logger.error(f"Error executing shortcut {chord}: {e}")
        return False

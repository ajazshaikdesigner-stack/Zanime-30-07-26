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
        self._qshortcuts = []
        self._bindings = self.config_manager.get("shortcuts", {})
        self.main_window = None

    def set_main_window(self, main_window) -> None:
        """Sets the main window context for QShortcut attachment and rebuilds existing bindings."""
        self.main_window = main_window
        self._rebuild_qshortcuts()

    def register(
        self, action_name: str, default_chord: str, callback: Callable
    ) -> None:
        """Registers an action and its callback, using user config if available."""
        chord = self._bindings.get(action_name, default_chord)
        self._shortcuts[chord] = callback
        logger.debug(f"Registered shortcut: {action_name} -> {chord}")
        if self.main_window:
            self._create_qshortcut(chord, callback)

    def _create_qshortcut(self, chord: str, callback: Callable):
        from PySide6.QtGui import QKeySequence, QShortcut
        from PySide6.QtCore import Qt
        
        shortcut = QShortcut(QKeySequence(chord), self.main_window)
        # We use ApplicationShortcut so it triggers regardless of focus
        shortcut.setContext(Qt.ApplicationShortcut)
        shortcut.activated.connect(callback)
        self._qshortcuts.append(shortcut)

    def _rebuild_qshortcuts(self):
        if not self.main_window:
            return
        # Clear old shortcuts
        for shortcut in self._qshortcuts:
            shortcut.setParent(None)
        self._qshortcuts.clear()
        
        for chord, callback in self._shortcuts.items():
            self._create_qshortcut(chord, callback)

    def rebind(self, action_name: str, new_chord: str) -> None:
        self._bindings[action_name] = new_chord
        self.config_manager.set_user("shortcuts", self._bindings)
        # Note: In a real rebind, we'd need to track which callback goes to which action.
        # For phase 2 simplicity, we'll assume a restart or reload is required for now.

    def handle_key(self, chord: str) -> bool:
        """Fallback for manual key handling."""
        if chord in self._shortcuts:
            try:
                self._shortcuts[chord]()
                return True
            except Exception as e:  # noqa: BLE001
                logger.error(f"Error executing shortcut {chord}: {e}")
        return False

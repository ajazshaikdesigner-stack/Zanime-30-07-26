"""
Selection Manager for tracking active UI selection.
"""

import logging
from typing import Any

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event

logger = logging.getLogger(__name__)


class SelectionManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._selected_items: list[Any] = []

    def set_selection(self, items: list[Any]) -> None:
        """Sets the current selection and broadcasts."""
        self._selected_items = items
        logger.debug(f"Selection changed: {len(self._selected_items)} items")
        self.event_bus.publish(Event.SELECTION_CHANGED, self._selected_items)

    def get_selection(self) -> list[Any]:
        return self._selected_items

    def clear_selection(self) -> None:
        if self._selected_items:
            self.set_selection([])

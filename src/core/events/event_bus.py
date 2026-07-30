"""
Centralized publisher-subscriber event bus.
"""

import logging
from collections.abc import Callable

from .event_types import Event

logger = logging.getLogger(__name__)


class EventBus:
    """Handles decoupling of components by routing events."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers: dict[Event, list[Callable]] = {}
        return cls._instance

    def subscribe(self, event_type: Event, callback: Callable) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: Event, callback: Callable) -> None:
        if (
            event_type in self._subscribers
            and callback in self._subscribers[event_type]
        ):
            self._subscribers[event_type].remove(callback)

    def publish(self, event_type: Event, *args, **kwargs) -> None:
        logger.debug("EventBus publishing: %s", event_type.name)
        if event_type in self._subscribers:
            # Iterate a snapshot so unsubscribe-during-dispatch is safe
            for callback in list(self._subscribers[event_type]):
                try:
                    callback(*args, **kwargs)
                except Exception:
                    logger.exception(
                        "Error in subscriber %s for %s",
                        callback.__name__,
                        event_type.name,
                    )

    @classmethod
    def reset(cls) -> None:
        """Clears the singleton instance. Used in shutdown and test teardown."""
        if cls._instance is not None:
            cls._instance._subscribers.clear()
        cls._instance = None

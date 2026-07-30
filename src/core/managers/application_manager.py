"""
Global Application Manager for lifecycle orchestration.
"""

import logging

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event

logger = logging.getLogger(__name__)


class ApplicationManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.is_running = False

    def startup(self):
        """Called after all managers are initialized."""
        logger.info("ApplicationManager: Orchestrating startup.")
        self.is_running = True
        self.event_bus.publish(Event.APP_STARTED)

    def shutdown(self):
        """Called before the application exits."""
        logger.info("ApplicationManager: Orchestrating shutdown.")
        self.event_bus.publish(Event.APP_SHUTDOWN)
        self.is_running = False

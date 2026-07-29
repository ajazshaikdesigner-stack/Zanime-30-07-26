"""
Notification Manager for non-blocking UI toasts.
"""
import logging
from src.core.events.event_bus import EventBus

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def show_info(self, message: str) -> None:
        logger.info(f"Notification (Info): {message}")
        # In a real UI, this would trigger a Toast overlay widget

    def show_warning(self, message: str) -> None:
        logger.warning(f"Notification (Warning): {message}")
        
    def show_error(self, message: str) -> None:
        logger.error(f"Notification (Error): {message}")

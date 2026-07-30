"""
AI Console Dock for viewing active AI task progress.
"""

from PySide6.QtWidgets import QListWidget, QVBoxLayout

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.sdk.base_dock import BaseDock
from src.core.services.service_registry import registry


class AIConsoleDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("AI Console", parent)

        layout = QVBoxLayout(self.container)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.app = parent.app if hasattr(parent, "app") else None
        if self.app:
            registry.get(EventBus).subscribe(Event.AI_TASK_STARTED, self._on_started)
            registry.get(EventBus).subscribe(Event.AI_TASK_PROGRESS, self._on_progress)
            registry.get(EventBus).subscribe(
                Event.AI_TASK_COMPLETED, self._on_completed
            )
            registry.get(EventBus).subscribe(Event.AI_TASK_FAILED, self._on_failed)

        # Initial mock item to show it's working
        self.list_widget.addItem("AI Framework Initialized. VRAM Limit: 3.5GB")

    def _on_started(self, task_id: str):
        self.list_widget.addItem(f"[STARTED] Task {task_id[-6:]}")

    def _on_progress(self, data: dict):
        # Update could be complex, for now we just append
        # self.list_widget.addItem(f"[PROGRESS] {data['id'][-6:]}: {data['progress']}% - {data['msg']}")
        pass  # Too spammy for a QListWidget

    def _on_completed(self, data: dict):
        self.list_widget.addItem(f"[SUCCESS] Task {data['id'][-6:]}")

    def _on_failed(self, data: dict):
        self.list_widget.addItem(f"[ERROR] Task {data['id'][-6:]}: {data['error']}")

"""
AI History Dock for viewing past jobs.
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.sdk.base_dock import BaseDock
from src.core.services.service_registry import registry


class AIHistoryDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("AI History", parent)

        layout = QVBoxLayout(self.container)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Task ID", "Status", "Duration"])
        layout.addWidget(self.table)

        self.app = parent.app if hasattr(parent, "app") else None
        if self.app:
            registry.get(EventBus).subscribe(
                Event.AI_TASK_COMPLETED, self._on_completed
            )
            registry.get(EventBus).subscribe(Event.AI_TASK_FAILED, self._on_failed)

    def _add_row(self, task_id: str, status: str):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(task_id[-6:]))
        self.table.setItem(row, 1, QTableWidgetItem(status))
        self.table.setItem(row, 2, QTableWidgetItem("N/A"))

    def _on_completed(self, data: dict):
        self._add_row(data["id"], "Success")

    def _on_failed(self, data: dict):
        self._add_row(data["id"], "Failed")

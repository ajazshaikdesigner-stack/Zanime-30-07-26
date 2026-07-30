"""
Story History Dock for viewing generated versions.
"""

import datetime

from PySide6.QtWidgets import QListWidget, QVBoxLayout

from src.core.sdk.base_dock import BaseDock


class StoryHistoryDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Story History", parent)

        layout = QVBoxLayout(self.container)
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)

    def update_history(self, history):
        self.history_list.clear()
        for ver in reversed(history):
            time_str = datetime.datetime.fromtimestamp(ver.timestamp, tz=datetime.timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            self.history_list.addItem(f"{time_str} - {ver.ai_model}")

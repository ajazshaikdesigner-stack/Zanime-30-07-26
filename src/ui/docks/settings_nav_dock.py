"""
Settings Navigation Dock
"""

from PySide6.QtWidgets import QListWidget, QVBoxLayout

from src.core.sdk.base_dock import BaseDock


class SettingsNavDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Categories", parent)

        layout = QVBoxLayout(self.container)
        self.list = QListWidget()
        self.list.addItems(
            [
                "General",
                "Backup & Recovery",
                "Diagnostics & Crash Reports",
                "Updates",
                "License & About",
            ]
        )
        layout.addWidget(self.list)

"""
Diagnostics Navigation Dock
"""

from PySide6.QtWidgets import QListWidget, QVBoxLayout

from src.core.sdk.base_dock import BaseDock


class DiagnosticsNavDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Diagnostics", parent)

        layout = QVBoxLayout(self.container)
        self.list = QListWidget()
        self.list.addItems(
            [
                "System Overview",
                "Memory Profiler",
                "GPU Profiler",
                "AI Queue",
                "Cache Explorer",
            ]
        )
        layout.addWidget(self.list)

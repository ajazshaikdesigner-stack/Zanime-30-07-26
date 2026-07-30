"""
Cache Log Dock
"""

from PySide6.QtWidgets import QTextEdit, QVBoxLayout

from src.core.sdk.base_dock import BaseDock


class CacheLogDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Cache & AI Queue Log", parent)

        layout = QVBoxLayout(self.container)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet(
            "background: #111; color: #4CAF50; font-family: monospace;"
        )
        self.log.append("Background Tasks Idle.")

        layout.addWidget(self.log)

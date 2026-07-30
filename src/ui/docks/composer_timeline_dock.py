"""
Composer Timeline
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout

from src.core.sdk.base_dock import BaseDock


class ComposerTimelineDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Timeline", parent)
        layout = QVBoxLayout(self.container)

        self.lbl = QLabel("Multi-Track Timeline Area (Mock)")
        self.lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl)

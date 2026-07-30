"""
Dialogue Timeline Dock
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from src.core.sdk.base_dock import BaseDock


class DialogueTimelineDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Dialogue Timeline", parent)
        layout = QVBoxLayout(self.container)

        controls = QHBoxLayout()
        self.play_btn = QPushButton("Play Audio")
        self.stop_btn = QPushButton("Stop")
        controls.addWidget(self.play_btn)
        controls.addWidget(self.stop_btn)
        layout.addLayout(controls)

        self.lbl = QLabel("Dialogue & Audio Tracks (Mock)")
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setStyleSheet(
            "border: 1px solid #444; background: #1a1a2e; min-height: 100px;"
        )
        layout.addWidget(self.lbl)

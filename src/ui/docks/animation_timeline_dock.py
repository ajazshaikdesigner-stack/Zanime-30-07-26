"""
Animation Timeline Dock
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from src.core.sdk.base_dock import BaseDock


class AnimationTimelineDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Timeline", parent)
        layout = QVBoxLayout(self.container)

        controls = QHBoxLayout()
        self.play_btn = QPushButton("Play")
        self.pause_btn = QPushButton("Pause")
        self.stop_btn = QPushButton("Stop")
        controls.addWidget(self.play_btn)
        controls.addWidget(self.pause_btn)
        controls.addWidget(self.stop_btn)
        layout.addLayout(controls)

        self.lbl = QLabel("Multi-Track Animation Area (Mock)")
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setStyleSheet(
            "border: 1px solid #444; background: #222; min-height: 100px;"
        )
        layout.addWidget(self.lbl)

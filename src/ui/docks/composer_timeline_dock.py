"""
Composer Timeline
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class ComposerTimelineDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Timeline", parent)
        layout = QVBoxLayout(self.container)
        
        self.lbl = QLabel("Multi-Track Timeline Area (Mock)")
        self.lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl)

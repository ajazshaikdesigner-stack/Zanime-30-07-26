"""
Camera Timeline Dock
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class CameraTimelineDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Camera Timeline", parent)
        layout = QVBoxLayout(self.container)
        
        self.lbl = QLabel("Camera Cuts and Transitions Track (Mock)")
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setStyleSheet("border: 1px solid #444; background: #2a2a2a; min-height: 80px;")
        layout.addWidget(self.lbl)

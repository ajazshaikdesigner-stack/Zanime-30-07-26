"""
Preview Dock
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class PreviewDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Preview", parent)
        
        layout = QVBoxLayout(self.container)
        
        self.preview_label = QLabel("No active preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #111; color: #555; border: 1px dashed #333;")
        
        layout.addWidget(self.preview_label)

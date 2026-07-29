"""
Render Queue Dock
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QListWidget, QHBoxLayout, QPushButton

class RenderQueueDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Render Queue", parent)
        
        layout = QVBoxLayout(self.container)
        
        self.list = QListWidget()
        layout.addWidget(self.list)
        
        controls = QHBoxLayout()
        self.pause_btn = QPushButton("Pause")
        self.resume_btn = QPushButton("Resume")
        self.cancel_btn = QPushButton("Cancel")
        controls.addWidget(self.pause_btn)
        controls.addWidget(self.resume_btn)
        controls.addWidget(self.cancel_btn)
        
        layout.addLayout(controls)

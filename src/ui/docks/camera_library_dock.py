"""
Camera Library Dock
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QListWidget, QComboBox

class CameraLibraryDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Camera Library", parent)
        
        layout = QVBoxLayout(self.container)
        
        self.category = QComboBox()
        self.category.addItems(["Shot Types", "Movements", "Presets"])
        layout.addWidget(self.category)
        
        self.list = QListWidget()
        self.list.addItems(["Extreme Wide Shot", "Medium Close Up", "Whip Pan", "Dolly Zoom (Vertigo)", "Handheld Shake"])
        layout.addWidget(self.list)

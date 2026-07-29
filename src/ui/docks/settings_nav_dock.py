"""
Settings Navigation Dock
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QListWidget

class SettingsNavDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Categories", parent)
        
        layout = QVBoxLayout(self.container)
        self.list = QListWidget()
        self.list.addItems([
            "General", 
            "Backup & Recovery", 
            "Diagnostics & Crash Reports", 
            "Updates", 
            "License & About"
        ])
        layout.addWidget(self.list)

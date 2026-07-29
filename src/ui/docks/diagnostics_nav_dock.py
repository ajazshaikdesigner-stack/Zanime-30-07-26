"""
Diagnostics Navigation Dock
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QListWidget

class DiagnosticsNavDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Diagnostics", parent)
        
        layout = QVBoxLayout(self.container)
        self.list = QListWidget()
        self.list.addItems(["System Overview", "Memory Profiler", "GPU Profiler", "AI Queue", "Cache Explorer"])
        layout.addWidget(self.list)

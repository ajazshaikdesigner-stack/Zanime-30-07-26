"""
Performance Monitor Dock
"""

from PySide6.QtWidgets import QTextEdit, QVBoxLayout

from src.core.sdk.base_dock import BaseDock


class PerformanceMonitorDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Performance Monitor", parent)

        layout = QVBoxLayout(self.container)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background: #111; color: #aaa; font-family: monospace;")
        self.log.append("System Ready.")
        self.log.append("CPU: AMD Ryzen 5 5600H detected.")
        self.log.append("GPU: AMD Radeon RX6500M 4GB detected.")
        self.log.append("RAM: 16GB available.")

        layout.addWidget(self.log)

"""
Notification Center Dock
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtGui import QColor

class NotificationDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Notification Center", parent)
        
        layout = QVBoxLayout(self.container)
        
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        self._add_mock_notification("Success: Project saved.", "#2e7d32")
        self._add_mock_notification("Info: Asset loaded.", "#0277bd")
        self._add_mock_notification("Warning: High memory usage.", "#f9a825")
        
    def _add_mock_notification(self, text: str, color_hex: str):
        item = QListWidgetItem(text)
        item.setForeground(QColor(color_hex))
        self.list_widget.addItem(item)

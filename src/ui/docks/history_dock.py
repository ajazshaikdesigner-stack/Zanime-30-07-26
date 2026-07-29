"""
History Dock (Undo/Redo visualizer)
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtGui import QFont

class HistoryDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("History", parent)
        
        layout = QVBoxLayout(self.container)
        
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        # Mock commands
        self.list_widget.addItem("Create Project")
        self.list_widget.addItem("Add Layer")
        self.list_widget.addItem("Move Object")
        
        # Current state indicator
        current_item = QListWidgetItem("Change Color (Current)")
        font = current_item.font()
        font.setBold(True)
        current_item.setFont(font)
        self.list_widget.addItem(current_item)
        
        self.list_widget.addItem("Delete Object (Undone)")

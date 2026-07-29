"""
Asset Browser Widget - Grid View.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLineEdit
from src.models.asset_model import AssetMetadata
from typing import List

class AssetBrowserWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search assets by name or tag...")
        layout.addWidget(self.search_bar)
        
        # Using QListWidget for the grid mock
        self.grid = QListWidget()
        self.grid.setViewMode(QListWidget.IconMode)
        self.grid.setResizeMode(QListWidget.Adjust)
        self.grid.setSpacing(10)
        layout.addWidget(self.grid)
        
    def populate(self, assets: List[AssetMetadata]):
        self.grid.clear()
        for a in assets:
            self.grid.addItem(f"{a.name}\n({a.asset_type.value})")

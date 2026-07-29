"""
Asset Preview Dock - Visualizes the selected asset.
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class AssetPreviewDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Preview", parent)
        
        layout = QVBoxLayout(self.container)
        
        self.preview_lbl = QLabel("Select an asset to preview")
        self.preview_lbl.setAlignment(Qt.AlignCenter)
        self.preview_lbl.setStyleSheet("background: #111; color: #888; border: 1px solid #333; min-height: 200px;")
        layout.addWidget(self.preview_lbl)
        
    def set_preview(self, name: str):
        self.preview_lbl.setText(f"[ Preview of {name} ]")

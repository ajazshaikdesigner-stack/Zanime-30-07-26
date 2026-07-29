"""
Asset Information Dock - Displays metadata.
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QLabel, QFormLayout
from src.models.asset_model import AssetMetadata

class AssetInformationDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Asset Information", parent)
        
        layout = QVBoxLayout(self.container)
        
        self.form = QFormLayout()
        self.name_lbl = QLabel()
        self.type_lbl = QLabel()
        self.author_lbl = QLabel()
        self.tags_lbl = QLabel()
        
        self.form.addRow("Name:", self.name_lbl)
        self.form.addRow("Type:", self.type_lbl)
        self.form.addRow("Author:", self.author_lbl)
        self.form.addRow("Tags:", self.tags_lbl)
        
        layout.addLayout(self.form)
        layout.addStretch()
        
    def set_asset(self, asset: AssetMetadata):
        self.name_lbl.setText(asset.name)
        self.type_lbl.setText(asset.asset_type.value)
        self.author_lbl.setText(asset.author)
        self.tags_lbl.setText(", ".join(asset.tags))

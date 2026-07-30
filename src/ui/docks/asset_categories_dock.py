"""
Asset Categories Dock - Tree view for filtering.
"""

from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout

from src.core.sdk.base_dock import BaseDock
from src.models.asset_model import AssetType


class AssetCategoriesDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Categories", parent)

        layout = QVBoxLayout(self.container)
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        layout.addWidget(self.tree)

        self.populate()

    def populate(self):
        # Collections
        collections_root = QTreeWidgetItem(self.tree, ["Collections"])
        QTreeWidgetItem(collections_root, ["Favorites"])
        QTreeWidgetItem(collections_root, ["Recently Used"])

        # Types
        types_root = QTreeWidgetItem(self.tree, ["Asset Types"])
        for t in AssetType:
            QTreeWidgetItem(types_root, [t.value])

        self.tree.expandAll()

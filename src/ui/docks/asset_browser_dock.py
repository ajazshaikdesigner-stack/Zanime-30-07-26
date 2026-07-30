"""
Asset Browser Dock
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from src.core.sdk.base_dock import BaseDock


class AssetBrowserDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Asset Browser", parent)

        layout = QVBoxLayout(self.container)

        # Search & Toolbar
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLineEdit(placeholderText="Search assets..."))
        toolbar.addWidget(QPushButton("Grid"))
        toolbar.addWidget(QPushButton("List"))
        layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Horizontal)

        # Categories Tree
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderHidden(True)
        root = QTreeWidgetItem(["Assets"])
        QTreeWidgetItem(root, ["Favorites"])
        QTreeWidgetItem(root, ["Characters"])
        QTreeWidgetItem(root, ["Backgrounds"])
        QTreeWidgetItem(root, ["Props"])
        self.category_tree.addTopLevelItem(root)
        self.category_tree.expandAll()
        splitter.addWidget(self.category_tree)

        # Asset List/Grid (Mock)
        self.asset_view = QListWidget()
        self.asset_view.addItems(["Asset 1", "Asset 2", "Asset 3"])
        self.asset_view.setDragEnabled(True)
        splitter.addWidget(self.asset_view)

        layout.addWidget(splitter)

"""
Project explorer for managing project assets and files.
"""

from PySide6.QtCore import QDir
from PySide6.QtWidgets import QFileSystemModel, QTreeView, QVBoxLayout

from src.core.sdk.base_dock import BaseDock


class ProjectExplorerDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Project Explorer", parent)

        layout = QVBoxLayout(self.container)
        self.tree_view = QTreeView()

        self.file_model = QFileSystemModel()
        # Filters can be adjusted later depending on the app's need
        self.file_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
        self.tree_view.setModel(self.file_model)

        # Hide standard columns like size, type, date modified for a cleaner look
        for i in range(1, 4):
            self.tree_view.hideColumn(i)

        layout.addWidget(self.tree_view)

    def set_project_path(self, extract_path: str):
        """Called when a project is loaded to show the internal temp extraction dir."""
        self.file_model.setRootPath(extract_path)
        self.tree_view.setRootIndex(self.file_model.index(extract_path))

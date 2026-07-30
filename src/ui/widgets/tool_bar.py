"""
Main Toolbar component.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QToolBar

from src.core.managers.asset_manager import AssetManager
from src.core.managers.command_manager import CommandManager
from src.core.managers.project_manager import ProjectManager
from src.core.services.service_registry import registry


class ZanimeToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)
        self.app = parent.app if hasattr(parent, "app") else None
        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self._setup_tools()

    def _setup_tools(self):
        if self.app:
            new_icon = registry.get(AssetManager).get_icon("new")
            save_icon = registry.get(AssetManager).get_icon("save")
            undo_icon = registry.get(AssetManager).get_icon("undo")
            redo_icon = registry.get(AssetManager).get_icon("redo")
        else:
            new_icon, save_icon, undo_icon, redo_icon = None, None, None, None

        self.new_action = self.addAction("New")
        if new_icon and not new_icon.isNull():
            self.new_action.setIcon(new_icon)

        self.save_action = self.addAction("Save")
        if save_icon and not save_icon.isNull():
            self.save_action.setIcon(save_icon)
        self.save_action.triggered.connect(self._on_save)

        self.addSeparator()

        self.undo_action = self.addAction("Undo")
        if undo_icon and not undo_icon.isNull():
            self.undo_action.setIcon(undo_icon)
        self.undo_action.triggered.connect(self._on_undo)

        self.redo_action = self.addAction("Redo")
        if redo_icon and not redo_icon.isNull():
            self.redo_action.setIcon(redo_icon)
        self.redo_action.triggered.connect(self._on_redo)

    def _on_save(self):
        if self.app:
            registry.get(ProjectManager).save_project()

    def _on_undo(self):
        if self.app:
            registry.get(CommandManager).undo()

    def _on_redo(self):
        if self.app:
            registry.get(CommandManager).redo()

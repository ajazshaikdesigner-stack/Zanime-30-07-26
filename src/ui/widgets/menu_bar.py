"""
Main Menu Bar component.
"""

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QMenuBar, QFileDialog

from src.core.managers.command_manager import CommandManager
from src.core.managers.configuration_manager import ConfigurationManager
from src.core.managers.project_manager import ProjectManager
from src.core.managers.workspace_manager import WorkspaceManager
from src.core.services.service_registry import registry


class ZanimeMenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent.app if hasattr(parent, "app") else None
        self._setup_menus()

    def _setup_menus(self):
        # File Menu
        self.file_menu = QMenu("File", self)

        self.new_action = QAction("New Project...", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self._on_new_project)

        self.open_action = QAction("Open Project...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self._on_open_project)

        self.save_action = QAction("Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self._on_save_project)

        self.settings_action = QAction("Project Settings...", self)
        self.settings_action.triggered.connect(self._on_project_settings)

        self.export_action = QAction("Export Story to TXT/MD...", self)
        self.export_action.triggered.connect(self._on_export_story)

        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self._on_exit)

        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.settings_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        self.addMenu(self.file_menu)

        # Edit Menu
        self.edit_menu = QMenu("Edit", self)
        # Add Preferences action to Edit menu
        self.action_preferences = QAction("Preferences...", self)
        self.action_preferences.setShortcut("Ctrl+,")
        self.edit_menu.addAction(self.action_preferences)

        self.action_ai_settings = QAction("AI Settings...", self)
        self.action_ai_settings.triggered.connect(self._on_ai_settings)
        self.edit_menu.addAction(self.action_ai_settings)

        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self._on_undo)

        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self._on_redo)

        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)
        self.addMenu(self.edit_menu)

        # View Menu
        self.view_menu = QMenu("View", self)
        self.addMenu(self.view_menu)

        # Help Menu
        self.help_menu = QMenu("Help", self)
        self.about_action = QAction("About ZANIME", self)
        self.help_menu.addAction(self.about_action)
        self.addMenu(self.help_menu)

    def _on_new_project(self):
        if self.app:
            from src.ui.wizards.new_project_wizard import NewProjectWizard

            wizard = NewProjectWizard(registry.get(ProjectManager), self)
            wizard.exec()

    def _on_open_project(self):
        if self.app:
            from src.ui.welcome_screen import WelcomeScreen

            ws = WelcomeScreen(self.app)
            ws._on_open_project()  # direct trigger for simplicity

    def _on_save_project(self):
        if self.app:
            registry.get(ProjectManager).save_project()

    def _on_project_settings(self):
        if self.app and registry.get(ProjectManager).current_project_path:
            from src.ui.dialogs.project_settings_dialog import ProjectSettingsDialog

            dlg = ProjectSettingsDialog(registry.get(ProjectManager), self)
            dlg.exec()

    def _on_ai_settings(self):
        if self.app:
            from src.ui.dialogs.ai_settings_dialog import AISettingsDialog

            dlg = AISettingsDialog(registry.get(ConfigurationManager), self)
            dlg.exec()

    def _on_export_story(self):
        if self.app:
            # Check if active workspace is Story
            wm = registry.get(WorkspaceManager)
            if wm.active_workspace == "Story":
                story_ws = self.parent().workspaces.get("Story")
                if story_ws:
                    path, _ = QFileDialog.getSaveFileName(
                        self,
                        "Export Story",
                        "",
                        "Text Files (*.txt);;Markdown Files (*.md)",
                    )
                    if path:
                        try:
                            with open(path, "w", encoding="utf-8") as f:
                                f.write(story_ws.story_model.content)
                        except Exception:
                            pass

    def _on_undo(self):
        if self.app:
            registry.get(CommandManager).undo()

    def _on_redo(self):
        if self.app:
            registry.get(CommandManager).redo()

    def _on_exit(self):
        if self.parent():
            self.parent().close()

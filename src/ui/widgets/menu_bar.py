"""
Main Menu Bar component.
"""

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QMenu, QMenuBar, QMessageBox

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
        self._build_file_menu()
        self._build_edit_menu()
        self._build_view_menu()
        self._build_help_menu()

    # ─────────────────────────────── FILE ────────────────────────────────
    def _build_file_menu(self):
        self.file_menu = QMenu("File", self)

        self.new_action = QAction("⊕  New Project...", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self._on_new_project)

        self.open_action = QAction("📂  Open Project...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self._on_open_project)

        self.save_action = QAction("💾  Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self._on_save_project)

        self.save_as_action = QAction("Save As...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self._on_save_as)

        self.settings_action = QAction("⚙  Project Settings...", self)
        self.settings_action.triggered.connect(self._on_project_settings)

        self.export_action = QAction("📤  Export Story to TXT/MD...", self)
        self.export_action.triggered.connect(self._on_export_story)

        self.exit_action = QAction("✕  Exit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self._on_exit)

        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.settings_action)
        self.file_menu.addAction(self.export_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        self.addMenu(self.file_menu)

    # ─────────────────────────────── EDIT ────────────────────────────────
    def _build_edit_menu(self):
        self.edit_menu = QMenu("Edit", self)

        self.undo_action = QAction("↩  Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self._on_undo)

        self.redo_action = QAction("↪  Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self._on_redo)

        self.action_ai_settings = QAction("🤖  AI Settings...", self)
        self.action_ai_settings.triggered.connect(self._on_ai_settings)

        self.action_preferences = QAction("⚙  Preferences...", self)
        self.action_preferences.setShortcut("Ctrl+,")
        self.action_preferences.triggered.connect(self._on_preferences)

        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_ai_settings)
        self.edit_menu.addAction(self.action_preferences)
        self.addMenu(self.edit_menu)

    # ─────────────────────────────── VIEW ────────────────────────────────
    def _build_view_menu(self):
        self.view_menu = QMenu("View", self)

        # Dock toggles — populated after window is fully set up
        dock_names = [
            ("Properties", "Properties Panel"),
            ("Timeline", "Timeline"),
            ("ProjectExplorer", "Project Explorer"),
            ("Console", "Console"),
            ("AssetBrowser", "Asset Browser"),
            ("NotificationCenter", "Notification Center"),
            ("History", "History"),
            ("Preview", "Preview"),
        ]

        self.dock_actions = {}
        for dock_id, dock_label in dock_names:
            action = QAction(dock_label, self)
            action.setCheckable(True)
            action.triggered.connect(
                lambda checked, d=dock_id: self._toggle_dock(d, checked)
            )
            self.view_menu.addAction(action)
            self.dock_actions[dock_id] = action

        self.view_menu.addSeparator()

        sidebar_action = QAction("Sidebar", self)
        sidebar_action.setCheckable(True)
        sidebar_action.setChecked(True)
        sidebar_action.triggered.connect(self._toggle_sidebar)
        self.view_menu.addAction(sidebar_action)

        self.view_menu.addSeparator()

        fullscreen_action = QAction("Full Screen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        self.view_menu.addAction(fullscreen_action)

        self.addMenu(self.view_menu)

    # ─────────────────────────────── HELP ────────────────────────────────
    def _build_help_menu(self):
        self.help_menu = QMenu("Help", self)

        self.about_action = QAction("ℹ  About ZANIME", self)
        self.about_action.triggered.connect(self._on_about)

        self.shortcuts_action = QAction("⌨  Keyboard Shortcuts", self)
        self.shortcuts_action.setShortcut("Ctrl+/")
        self.shortcuts_action.triggered.connect(self._on_shortcuts)

        self.docs_action = QAction("📖  Documentation", self)
        self.docs_action.triggered.connect(self._on_docs)

        self.help_menu.addAction(self.about_action)
        self.help_menu.addAction(self.shortcuts_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.docs_action)
        self.addMenu(self.help_menu)

    # ─────────────────────── HANDLERS ────────────────────────────────────
    def _on_new_project(self):
        if self.app:
            from src.ui.wizards.new_project_wizard import NewProjectWizard
            wizard = NewProjectWizard(registry.get(ProjectManager), self)
            wizard.exec()

    def _on_open_project(self):
        path = QFileDialog.getExistingDirectory(self, "Open ZANIME Project Folder", "")
        if path:
            try:
                registry.get(ProjectManager).open_project(path)
            except Exception as e:
                QMessageBox.warning(self, "Open Project", f"Could not open project:\n{e}")

    def _on_save_project(self):
        if self.app:
            try:
                registry.get(ProjectManager).save_project()
            except Exception as e:
                QMessageBox.warning(self, "Save", f"Could not save project:\n{e}")

    def _on_save_as(self):
        path = QFileDialog.getExistingDirectory(self, "Save Project To...", "")
        if path:
            try:
                registry.get(ProjectManager).save_project(path)
            except Exception as e:
                QMessageBox.warning(self, "Save As", f"Could not save project:\n{e}")

    def _on_project_settings(self):
        if self.app:
            pm = registry.get(ProjectManager)
            if pm.current_project_path:
                from src.ui.dialogs.project_settings_dialog import ProjectSettingsDialog
                dlg = ProjectSettingsDialog(pm, self)
                dlg.exec()
            else:
                QMessageBox.information(
                    self, "Project Settings",
                    "No project is currently open.\n\nCreate or open a project first."
                )

    def _on_ai_settings(self):
        if self.app:
            from src.ui.dialogs.ai_settings_dialog import AISettingsDialog
            dlg = AISettingsDialog(registry.get(ConfigurationManager), self)
            dlg.exec()

    def _on_preferences(self):
        if self.app:
            registry.get(WorkspaceManager).set_workspace("Settings")

    def _on_export_story(self):
        if self.app:
            wm = registry.get(WorkspaceManager)
            if wm.active_workspace != "Story":
                QMessageBox.information(
                    self, "Export Story",
                    "Please switch to the Story workspace first to export."
                )
                return
            path, _ = QFileDialog.getSaveFileName(
                self, "Export Story", "",
                "Text Files (*.txt);;Markdown Files (*.md)"
            )
            if path:
                try:
                    from src.ui.workspace_factory import WorkspaceFactory
                    # Try to get content from current story workspace via registry
                    main_win = self.parent()
                    ws_widget = None
                    if hasattr(main_win, "workspace_factory"):
                        ws_widget = main_win.workspace_factory.get_workspace("Story", main_win.app, main_win)
                    if ws_widget and hasattr(ws_widget, "story_model"):
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(ws_widget.story_model.content)
                        QMessageBox.information(self, "Export Complete", f"Story exported to:\n{path}")
                    else:
                        QMessageBox.warning(self, "Export", "Could not access story content.")
                except Exception as e:
                    QMessageBox.warning(self, "Export Error", str(e))

    def _on_undo(self):
        if self.app:
            registry.get(CommandManager).undo()

    def _on_redo(self):
        if self.app:
            registry.get(CommandManager).redo()

    def _on_exit(self):
        if self.parent():
            self.parent().close()

    def _on_about(self):
        QMessageBox.about(
            self, "About ZANIME",
            "<h2>ZANIME v2</h2>"
            "<p><b>Professional AI-Powered 2D Animation Studio</b></p>"
            "<p>Version 2.0.0 — Genesis Release</p>"
            "<hr>"
            "<p>Craft compelling animated stories with AI-assisted tools for "
            "storytelling, character design, scene composition, and rendering.</p>"
            "<p style='color:#888;font-size:9pt;'>© 2026 ZANIME Studio. All rights reserved.</p>"
        )

    def _on_shortcuts(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Keyboard Shortcuts")
        msg.setText(
            "<b>ZANIME Keyboard Shortcuts</b><br><br>"
            "<table cellspacing='6'>"
            "<tr><td><b>Ctrl+N</b></td><td>New Project</td></tr>"
            "<tr><td><b>Ctrl+O</b></td><td>Open Project</td></tr>"
            "<tr><td><b>Ctrl+S</b></td><td>Save</td></tr>"
            "<tr><td><b>Ctrl+Z</b></td><td>Undo</td></tr>"
            "<tr><td><b>Ctrl+Y</b></td><td>Redo</td></tr>"
            "<tr><td><b>Ctrl+,</b></td><td>Preferences</td></tr>"
            "<tr><td><b>Ctrl+/</b></td><td>Keyboard Shortcuts</td></tr>"
            "<tr><td><b>Ctrl+Q</b></td><td>Exit</td></tr>"
            "<tr><td><b>F11</b></td><td>Toggle Full Screen</td></tr>"
            "</table>"
        )
        msg.exec()

    def _on_docs(self):
        import webbrowser
        webbrowser.open("https://github.com/zanime/docs")

    def _toggle_dock(self, dock_id: str, checked: bool):
        main_win = self.parent()
        if hasattr(main_win, "docks") and dock_id in main_win.docks:
            dock = main_win.docks[dock_id]
            dock.show() if checked else dock.hide()

    def _toggle_sidebar(self, checked: bool):
        main_win = self.parent()
        for toolbar in main_win.findChildren(__import__("PySide6.QtWidgets", fromlist=["QToolBar"]).QToolBar):
            if toolbar.windowTitle() == "Sidebar":
                toolbar.setVisible(checked)
                break

    def _toggle_fullscreen(self):
        main_win = self.parent()
        if main_win.isFullScreen():
            main_win.showNormal()
        else:
            main_win.showFullScreen()

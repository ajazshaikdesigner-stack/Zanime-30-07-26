"""
Main Toolbar component — premium styled.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QToolBar, QToolButton, QWidget

from src.core.managers.command_manager import CommandManager
from src.core.managers.project_manager import ProjectManager
from src.core.managers.workspace_manager import WorkspaceManager
from src.core.services.service_registry import registry

_STYLE = """
QToolBar#MainToolbar {
    background-color: #13151f;
    border-bottom: 1px solid #1e2235;
    padding: 4px 8px;
    spacing: 2px;
}

QToolButton#TbBtn {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 5px 12px;
    color: #94a3b8;
    font-size: 9pt;
    min-width: 32px;
}

QToolButton#TbBtn:hover {
    background-color: #22253a;
    border-color: #2d3154;
    color: #e2e8f0;
}

QToolButton#TbBtn:pressed {
    background-color: #7c3aed;
    color: #ffffff;
    border-color: #7c3aed;
}

QToolButton#TbBtnAccent {
    background-color: #7c3aed;
    border: none;
    border-radius: 6px;
    padding: 5px 16px;
    color: #ffffff;
    font-size: 9pt;
    font-weight: bold;
    min-width: 80px;
}

QToolButton#TbBtnAccent:hover {
    background-color: #6d28d9;
}

QToolButton#TbBtnAccent:pressed {
    background-color: #5b21b6;
}

QLabel#TbSep {
    color: #1e2235;
    background-color: #1e2235;
    min-width: 1px;
    max-width: 1px;
    min-height: 20px;
    max-height: 20px;
    margin: 0 6px;
}

QLabel#TbProjectName {
    color: #475569;
    font-size: 8pt;
    padding-left: 8px;
}
"""


def _make_btn(label, tooltip, object_name="TbBtn"):
    btn = QToolButton()
    btn.setText(label)
    btn.setObjectName(object_name)
    btn.setToolTip(tooltip)
    btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
    return btn


def _make_sep():
    sep = QLabel()
    sep.setObjectName("TbSep")
    sep.setFixedSize(1, 22)
    return sep


class ZanimeToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)
        self.app = parent.app if hasattr(parent, "app") else None
        self.setObjectName("MainToolbar")
        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.setStyleSheet(_STYLE)
        self._setup_tools()

    def _setup_tools(self):
        # New Project (accent)
        self.new_btn = _make_btn("⊕  New", "New Project  Ctrl+N", "TbBtnAccent")
        self.new_btn.clicked.connect(self._on_new)
        self.addWidget(self.new_btn)

        self.addWidget(_make_sep())

        # Open
        self.open_btn = _make_btn("📂  Open", "Open Project  Ctrl+O")
        self.open_btn.clicked.connect(self._on_open)
        self.addWidget(self.open_btn)

        # Save
        self.save_btn = _make_btn("💾  Save", "Save  Ctrl+S")
        self.save_btn.clicked.connect(self._on_save)
        self.addWidget(self.save_btn)

        self.addWidget(_make_sep())

        # Undo / Redo pill group
        self.undo_btn = _make_btn("↩  Undo", "Undo  Ctrl+Z")
        self.undo_btn.clicked.connect(self._on_undo)
        self.addWidget(self.undo_btn)

        self.redo_btn = _make_btn("↪  Redo", "Redo  Ctrl+Y")
        self.redo_btn.clicked.connect(self._on_redo)
        self.addWidget(self.redo_btn)

        self.addWidget(_make_sep())

        # Render shortcut
        self.render_btn = _make_btn("🎬  Render", "Go to Render workspace")
        self.render_btn.clicked.connect(self._on_render)
        self.addWidget(self.render_btn)

        # Spacer to push project name right
        spacer = QWidget()
        spacer.setSizePolicy(
            __import__("PySide6.QtWidgets", fromlist=["QSizePolicy"]).QSizePolicy.Expanding,
            __import__("PySide6.QtWidgets", fromlist=["QSizePolicy"]).QSizePolicy.Preferred
        )
        spacer.setStyleSheet("background: transparent;")
        self.addWidget(spacer)

        # Project name indicator
        self.project_lbl = QLabel("No Project Open")
        self.project_lbl.setObjectName("TbProjectName")
        self.addWidget(self.project_lbl)

        self.addWidget(_make_sep())
        self._setup_events()

    def _setup_events(self):
        import os

        from src.core.events.event_bus import EventBus
        from src.core.events.event_types import Event

        try:
            registry.get(EventBus).subscribe(
                Event.PROJECT_OPENED,
                lambda path: self.update_project_name(
                    os.path.basename(path).replace(".zanime", "")
                ),
            )
        except KeyError:
            pass

    # ── Handlers ──────────────────────────────────────────────────────────
    def _on_new(self):
        if self.app:
            from src.ui.wizards.new_project_wizard import NewProjectWizard
            wizard = NewProjectWizard(registry.get(ProjectManager), self)
            if wizard.exec():
                wm = registry.get(WorkspaceManager)
                if wm.active_workspace == "Welcome":
                    wm.set_workspace("Home")

    def _on_open(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        path, _ = QFileDialog.getOpenFileName(
            self, "Open ZANIME Project", "", "Zanime Projects (*.zanime);;All Files (*)"
        )
        if path:
            try:
                registry.get(ProjectManager).open_project(path)
                wm = registry.get(WorkspaceManager)
                if wm.active_workspace == "Welcome":
                    wm.set_workspace("Home")
            except Exception as e:
                QMessageBox.warning(self, "Open Project", f"Could not open project:\n{e}")

    def _on_save(self):
        if self.app:
            try:
                registry.get(ProjectManager).save_project()
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Save", f"Could not save:\n{e}")

    def _on_undo(self):
        if self.app:
            registry.get(CommandManager).undo()

    def _on_redo(self):
        if self.app:
            registry.get(CommandManager).redo()

    def _on_render(self):
        if self.app:
            registry.get(WorkspaceManager).set_workspace("Render")

    def update_project_name(self, name: str):
        self.project_lbl.setText(f"📁  {name}")

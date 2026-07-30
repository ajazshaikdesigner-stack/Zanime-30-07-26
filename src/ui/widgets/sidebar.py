"""
Premium vertical sidebar for switching workspaces.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QLabel,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from src.core.managers.workspace_manager import WorkspaceManager
from src.core.services.service_registry import registry

# Sidebar color tokens (match palette.json dark theme)
_STYLE = """
QToolBar#Sidebar {
    background-color: #13151f;
    border-right: 1px solid #1e2235;
    padding: 0px;
    spacing: 0px;
}

/* Section label */
QLabel#SidebarSection {
    color: #475569;
    font-size: 7.5pt;
    font-weight: bold;
    letter-spacing: 1.5px;
    padding: 12px 18px 4px 18px;
    background: transparent;
    text-transform: uppercase;
}

/* Nav buttons - aligned cleanly to left */
QPushButton#SidebarBtn {
    border: none;
    border-radius: 8px;
    padding-left: 18px;
    margin: 2px 8px;
    font-size: 9.5pt;
    font-weight: 500;
    color: #94a3b8;
    text-align: left;
    background-color: transparent;
}

QPushButton#SidebarBtn:hover {
    background-color: #22253a;
    color: #e2e8f0;
}

QPushButton#SidebarBtn:checked {
    background-color: #1e1633;
    color: #a78bfa;
    border-left: 3px solid #7c3aed;
    padding-left: 15px;
    font-weight: bold;
}

QPushButton#SidebarBtn:checked:hover {
    background-color: #251e3d;
}

/* Separator line */
QFrame#SidebarSep {
    color: #1e2235;
    margin: 6px 16px;
}
"""


WORKSPACES = [
    # (section_label, [(workspace_id, display_label, emoji)])
    ("Create", [
        ("Story",       "Story",         "📝"),
        ("Script",      "Script",        "🎭"),
        ("Characters",  "Characters",    "👤"),
        ("Backgrounds", "Backgrounds",   "🌄"),
        ("Props",       "Props",         "📦"),
    ]),
    ("Produce", [
        ("Storyboard",     "Storyboard",     "🎬"),
        ("SceneComposer",  "Scene Composer", "🎞"),
        ("Animation",      "Animation",      "✨"),
        ("Voice",          "Voice",          "🎤"),
        ("Music",          "Music",          "🎵"),
    ]),
    ("Output", [
        ("Render",  "Render",  "📤"),
    ]),
    ("System", [
        ("Home",     "Home",     "🏠"),
        ("Library",  "Library",  "📚"),
        ("Settings", "Settings", "⚙"),
    ]),
]


class _SidebarButton(QPushButton):
    def __init__(self, ws_id, label, emoji, parent=None):
        super().__init__(parent)
        self.ws_id = ws_id
        self.setText(f"{emoji}   {label}")
        self.setCheckable(True)
        self.setObjectName("SidebarBtn")
        self.setFixedHeight(38)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(label)


class ZanimeSidebar(QToolBar):
    def __init__(self, parent=None):
        super().__init__("Sidebar", parent)
        self.app = parent.app if hasattr(parent, "app") else None
        self.setObjectName("Sidebar")
        self.setMovable(False)
        self.setOrientation(Qt.Vertical)
        self.setStyleSheet(_STYLE)
        self.setFixedWidth(210)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self._buttons = {}

        self._build()

    def _build(self):
        # App logo at top
        logo_widget = QWidget()
        logo_widget.setObjectName("SidebarLogo")
        logo_widget.setStyleSheet("background: transparent;")
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(18, 16, 18, 8)
        logo_lbl = QLabel("ZANIME")
        logo_lbl.setStyleSheet(
            "font-size: 16pt; font-weight: 900; color: #7c3aed; "
            "letter-spacing: 2px; background: transparent;"
        )
        sub_lbl = QLabel("Animation Studio")
        sub_lbl.setStyleSheet(
            "font-size: 7.5pt; color: #475569; letter-spacing: 1px; background: transparent;"
        )
        logo_layout.addWidget(logo_lbl)
        logo_layout.addWidget(sub_lbl)
        self.addWidget(logo_widget)

        # Divider
        self._add_separator()

        for section_name, items in WORKSPACES:
            # Section label
            sec_lbl = QLabel(section_name)
            sec_lbl.setObjectName("SidebarSection")
            self.addWidget(sec_lbl)

            for ws_id, label, emoji in items:
                btn = _SidebarButton(ws_id, label, emoji)
                self.addWidget(btn)
                self.button_group.addButton(btn)
                self._buttons[ws_id] = btn
                btn.clicked.connect(
                    lambda checked=False, w=ws_id: self._on_click(w)
                )

            self._add_separator()

    def _add_separator(self):
        sep = QFrame()
        sep.setObjectName("SidebarSep")
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        self.addWidget(sep)

    def _on_click(self, workspace_name: str):
        registry.get(WorkspaceManager).set_workspace(workspace_name)

    def set_active(self, workspace_name: str):
        """Programmatically check the button for the given workspace."""
        if workspace_name in self._buttons:
            btn = self._buttons[workspace_name]
            if not btn.isChecked():
                btn.blockSignals(True)
                btn.setChecked(True)
                btn.blockSignals(False)

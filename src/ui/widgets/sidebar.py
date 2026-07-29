"""
Vertical toolbar for switching workspaces.
"""
from PySide6.QtWidgets import QToolBar, QButtonGroup, QToolButton
from PySide6.QtCore import Qt
from src.core.services.service_registry import registry
from src.core.managers.workspace_manager import WorkspaceManager

class ZanimeSidebar(QToolBar):
    def __init__(self, parent=None):
        super().__init__("Sidebar", parent)
        self.app = parent.app if hasattr(parent, 'app') else None
        self.setMovable(False)
        self.setOrientation(Qt.Vertical)
        self.setStyleSheet("""
            QToolBar {
                border-right: 1px solid #3f3f46;
                padding-top: 10px;
            }
            QToolButton {
                border: none;
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 5px;
                font-size: 14pt;
                text-align: left;
            }
            QToolButton:checked {
                background-color: #007acc;
                color: #ffffff;
            }
            QToolButton:hover:!checked {
                background-color: #3e3e42;
            }
        """)
        
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        self._setup_workspaces()

    def _setup_workspaces(self):
        workspaces = [
            ("Home", "🏠 Home"),
            ("Story", "📝 Story"),
            ("Script", "🎭 Script"),
            ("Characters", "👧 Characters"),
            ("Backgrounds", "🌳 Backgrounds"),
            ("Props", "📦 Props"),
            ("Storyboard", "🎬 Storyboard"),
            ("SceneComposer", "🎞 Scene Composer"),
            ("Animation", "🎥 Animation"),
            ("Voice", "🎤 Voice"),
            ("Music", "🎵 Music"),
            ("Render", "📤 Render"),
            ("Library", "📚 Library"),
            ("Settings", "⚙ Settings")
        ]
        
        for ws_id, ws_label in workspaces:
            btn = QToolButton()
            btn.setText(ws_label)
            btn.setCheckable(True)
            # Use text beside icon if we had real icons, but since emoji is in text, just use text
            btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
            
            if ws_id == "Home":
                btn.setChecked(True)
                
            self.addWidget(btn)
            self.button_group.addButton(btn)
            
            # Connect the click event, capturing the workspace id
            btn.clicked.connect(lambda checked=False, w=ws_id: self._on_workspace_clicked(w))
            
    def _on_workspace_clicked(self, workspace_name):
        if self.app:
            registry.get(WorkspaceManager).set_workspace(workspace_name)

"""
Home workspace for welcome and recent projects.
"""
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from src.core.sdk.base_workspace import BaseWorkspace
from src.core.services.service_registry import registry
from src.core.managers.workspace_manager import WorkspaceManager

class HomeWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__(app, parent)
        from PySide6.QtWidgets import QWidget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("ZANIME - Home")
        title.setStyleSheet("font-size: 24pt; font-weight: bold;")
        
        btn_anim = QPushButton("Go to Animation Workspace")
        btn_anim.clicked.connect(lambda: registry.get(WorkspaceManager).set_workspace("Animation"))
        
        layout.addWidget(title)
        layout.addWidget(btn_anim)

    def get_required_docks(self):
        return []
        
    def get_hidden_docks(self):
        return ["Properties", "Timeline"]

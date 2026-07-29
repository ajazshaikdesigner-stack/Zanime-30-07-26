"""
Music workspace.
"""
from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from src.core.sdk.base_workspace import BaseWorkspace

class MusicWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__(app, parent)
        from PySide6.QtWidgets import QWidget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("Music Workspace")
        title.setStyleSheet("font-size: 24pt; color: #777;")
        layout.addWidget(title)

    def get_required_docks(self):
        return []
        
    def get_hidden_docks(self):
        return ["Properties", "Timeline", "ProjectExplorer", "Console"]

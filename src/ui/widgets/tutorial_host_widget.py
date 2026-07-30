"""
Tutorial Host Widget - Uses QStackedWidget to cycle through workspaces.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QStackedWidget, QVBoxLayout, QWidget


class TutorialHostWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # We will mock the workspaces here to prove the concept.
        # In full production, we'd inject the actual Workspace objects from MainWindow.
        self.workspaces = {}

    def add_mock_workspace(self, name: str):
        w = QLabel(f"--- {name} WORKSPACE ---")
        w.setAlignment(Qt.AlignCenter)
        w.setStyleSheet("font-size: 24px; color: #555;")
        self.stack.addWidget(w)
        self.workspaces[name] = w

    def switch_to(self, name: str):
        if name in self.workspaces:
            self.stack.setCurrentWidget(self.workspaces[name])

"""
Base Workspace SDK.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow


class BaseWorkspace(QMainWindow):
    def __init__(self, title_or_app=None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Widget)
        if isinstance(title_or_app, str):
            self.setWindowTitle(title_or_app)
            self.app = None
        else:
            self.app = title_or_app

    def get_required_docks(self) -> list[str]:
        """Returns a list of dock names this workspace needs."""
        return []

    def get_hidden_docks(self) -> list[str]:
        """Returns a list of dock names this workspace explicitly hides."""
        return []

    def on_enter(self) -> None:
        """Hook called when the workspace is switched to."""

    def on_exit(self) -> None:
        """Hook called when the workspace is switched away from."""

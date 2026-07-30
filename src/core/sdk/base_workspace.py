"""
Base Workspace SDK.
"""

from PySide6.QtWidgets import QMainWindow


class BaseWorkspace(QMainWindow):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app

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

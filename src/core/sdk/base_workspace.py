"""
Base Workspace SDK.
"""
from PySide6.QtWidgets import QMainWindow
from typing import List

class BaseWorkspace(QMainWindow):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        
    def get_required_docks(self) -> List[str]:
        """Returns a list of dock names this workspace needs."""
        return []

    def get_hidden_docks(self) -> List[str]:
        """Returns a list of dock names this workspace explicitly hides."""
        return []

    def on_enter(self) -> None:
        """Hook called when the workspace is switched to."""
        pass

    def on_exit(self) -> None:
        """Hook called when the workspace is switched away from."""
        pass

"""
Base Editor SDK.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from typing import Optional

class BaseEditor(QWidget):
    """
    Base Editor class that every future module editor should inherit from.
    Handles composition of toolbars, properties, and the main canvas.
    """
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
    def get_selection(self) -> list:
        return []

    def handle_command(self, command) -> None:
        if self.app:
            self.app.command_manager.execute(command)

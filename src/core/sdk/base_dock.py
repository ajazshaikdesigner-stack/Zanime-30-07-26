"""
Base Dock SDK.
"""
from PySide6.QtWidgets import QDockWidget, QWidget
from PySide6.QtCore import Qt

class BaseDock(QDockWidget):
    """
    Reusable Dock Widget base class.
    """
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.container = QWidget()
        self.setWidget(self.container)
        
    def get_id(self) -> str:
        return self.windowTitle().replace(" ", "")

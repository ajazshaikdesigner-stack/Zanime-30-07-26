"""
UI Component SDK interfaces (Panels, Toolbars).
"""
from PySide6.QtWidgets import QWidget, QToolBar, QVBoxLayout

class BaseToolbar(QToolBar):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)

class BasePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

class BaseInspector(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        
class BaseTimeline(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)

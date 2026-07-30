"""
Render Preview Widget
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget


class RenderPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.viewport_mock = QLabel("Production Frame Buffer Preview")
        self.viewport_mock.setAlignment(Qt.AlignCenter)
        self.viewport_mock.setStyleSheet(
            "border: 2px solid #333; background: #000; min-height: 400px;"
        )
        layout.addWidget(self.viewport_mock)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_lbl = QLabel("Ready")
        layout.addWidget(self.status_lbl)

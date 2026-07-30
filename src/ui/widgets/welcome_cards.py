"""
Custom widgets for the Welcome Screen.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


class QuickActionButton(QPushButton):
    def __init__(self, text, icon_str=None, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(40)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 20px;
                border: none;
                border-radius: 5px;
                background-color: transparent;
                font-size: 14px;
                color: #ddd;
            }
            QPushButton:hover {
                background-color: #3a3f4b;
                color: #fff;
            }
            QPushButton:pressed {
                background-color: #2b2d36;
            }
        """)


class ProjectCard(QFrame):
    clicked = Signal(dict)

    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.setFrameShape(QFrame.StyledPanel)

        self.setStyleSheet("""
            ProjectCard {
                background-color: #2b2d36;
                border-radius: 8px;
                border: 1px solid #1e1e24;
            }
            ProjectCard:hover {
                background-color: #32353f;
                border: 1px solid #4CAF50;
            }
            ProjectCard:focus {
                border: 1px solid #4CAF50;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        # Thumbnail placeholder
        thumb = QLabel()
        thumb.setFixedSize(60, 45)
        thumb.setStyleSheet("background-color: #1a1b20; border-radius: 4px;")

        # Details
        details = QVBoxLayout()
        name = QLabel(project_data.get("name", "Unknown Project"))
        name.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: #eee; background: transparent;"
        )

        modified = project_data.get("modified", "Unknown")
        version = project_data.get("version", "1.0")
        size = project_data.get("size", "0MB")
        meta = QLabel(f"{modified} • v{version} • {size}")
        meta.setStyleSheet("font-size: 11px; color: #888; background: transparent;")

        details.addWidget(name)
        details.addWidget(meta)

        layout.addWidget(thumb)
        layout.addLayout(details)
        layout.addStretch()

        # Pin icon placeholder
        if project_data.get("pinned", False):
            pin = QLabel("📌")
            pin.setStyleSheet("background: transparent;")
            layout.addWidget(pin)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.project_data)
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.clicked.emit(self.project_data)
        super().keyPressEvent(event)


class DemoProjectCard(QFrame):
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet("""
            DemoProjectCard {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a2933, stop:1 #111a21);
                border-radius: 12px;
                border: 1px solid #243c4f;
            }
            DemoProjectCard:hover {
                border: 1px solid #4CAF50;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1f313e, stop:1 #15212a);
            }
            DemoProjectCard:focus {
                border: 1px solid #4CAF50;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("The Crystal Forest")
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #4CAF50; background: transparent;"
        )

        desc = QLabel(
            "Explore a fully rigged, composited 2D scene demonstrating advanced ZANIME capabilities."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(
            "color: #ccc; background: transparent; font-size: 13px; line-height: 1.4;"
        )

        meta = QLabel("Estimated Load: 250MB • Coming Soon")
        meta.setStyleSheet(
            "color: #888; font-size: 11px; background: transparent; margin-top: 10px;"
        )

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addWidget(meta)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.clicked.emit()
        super().keyPressEvent(event)

"""
Premium Welcome Cards for ZANIME's Welcome Workspace.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class QuickActionButton(QPushButton):
    """A card-style quick action button with icon + label."""

    def __init__(self, emoji: str, text: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(64)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(14)

        icon_lbl = QLabel(emoji)
        icon_lbl.setStyleSheet(
            "font-size: 20pt; background: transparent; color: inherit;"
        )
        icon_lbl.setFixedWidth(32)
        icon_lbl.setAlignment(Qt.AlignCenter)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        title_lbl = QLabel(text)
        title_lbl.setStyleSheet(
            "font-size: 10pt; font-weight: bold; color: #e2e8f0; background: transparent;"
        )
        text_layout.addWidget(title_lbl)
        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setStyleSheet(
                "font-size: 8pt; color: #64748b; background: transparent;"
            )
            text_layout.addWidget(sub_lbl)

        layout.addWidget(icon_lbl)
        layout.addLayout(text_layout)
        layout.addStretch()

        arrow = QLabel("›")
        arrow.setStyleSheet("font-size: 14pt; color: #334155; background: transparent;")
        layout.addWidget(arrow)

        self.setStyleSheet("""
            QPushButton {
                background-color: #13151f;
                border: 1px solid #1e2235;
                border-radius: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1a1d2e;
                border-color: #7c3aed;
            }
            QPushButton:pressed {
                background-color: #22253a;
            }
        """)


class ProjectCard(QFrame):
    """A rich project card with thumbnail placeholder and metadata."""
    clicked = Signal(dict)

    def __init__(self, project_data: dict, parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(72)

        self.setStyleSheet("""
            ProjectCard {
                background-color: #13151f;
                border-radius: 10px;
                border: 1px solid #1e2235;
            }
            ProjectCard:hover {
                background-color: #1a1d2e;
                border: 1px solid #7c3aed;
            }
            ProjectCard:focus {
                border: 1px solid #a78bfa;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(14)

        # Gradient thumbnail placeholder
        thumb = QLabel()
        thumb.setFixedSize(70, 48)
        thumb.setAlignment(Qt.AlignCenter)
        # Pick gradient color based on name hash
        colors = [
            ("qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #4c1d95,stop:1 #7c3aed)", "🎬"),
            ("qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #065f46,stop:1 #059669)", "🌄"),
            ("qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #1e3a5f,stop:1 #0369a1)", "✨"),
            ("qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #7c2d12,stop:1 #dc2626)", "🎭"),
            ("qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #1e1b4b,stop:1 #4f46e5)", "📝"),
        ]
        idx = hash(project_data.get("name", "")) % len(colors)
        grad, icon = colors[idx]
        thumb.setStyleSheet(
            f"background: {grad}; border-radius: 6px; font-size: 18pt;"
        )
        thumb.setText(icon)

        # Text details
        text_col = QVBoxLayout()
        text_col.setSpacing(3)

        name_row = QHBoxLayout()
        name_lbl = QLabel(project_data.get("name", "Unknown"))
        name_lbl.setStyleSheet(
            "font-weight: bold; font-size: 10pt; color: #e2e8f0; background: transparent;"
        )
        name_row.addWidget(name_lbl)
        if project_data.get("pinned"):
            pin = QLabel("📌")
            pin.setStyleSheet("font-size: 9pt; background: transparent;")
            name_row.addWidget(pin)
        name_row.addStretch()
        text_col.addLayout(name_row)

        modified = project_data.get("modified", "")
        version = project_data.get("version", "")
        size = project_data.get("size", "")
        meta_lbl = QLabel(f"{modified}  ·  v{version}  ·  {size}")
        meta_lbl.setStyleSheet(
            "font-size: 8pt; color: #475569; background: transparent;"
        )
        text_col.addWidget(meta_lbl)

        layout.addWidget(thumb)
        layout.addLayout(text_col)
        layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.project_data)
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.clicked.emit(self.project_data)
        super().keyPressEvent(event)


class DemoProjectCard(QFrame):
    """A highlighted demo project card with gradient background."""
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(110)

        self.setStyleSheet("""
            DemoProjectCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e1040, stop:0.5 #2d1b69, stop:1 #1e1040);
                border-radius: 12px;
                border: 1px solid #4c1d95;
            }
            DemoProjectCard:hover {
                border: 1px solid #7c3aed;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #251345, stop:0.5 #352175, stop:1 #251345);
            }
            DemoProjectCard:focus {
                border: 2px solid #a78bfa;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        header = QHBoxLayout()
        badge = QLabel("DEMO")
        badge.setStyleSheet(
            "background-color: #7c3aed; color: #ffffff; font-size: 7pt; "
            "font-weight: bold; border-radius: 3px; padding: 2px 6px; letter-spacing: 1px;"
        )
        badge.setFixedHeight(18)
        header.addWidget(badge)
        header.addStretch()
        header.addWidget(QLabel("🌲"))
        layout.addLayout(header)

        title = QLabel("The Crystal Forest")
        title.setStyleSheet(
            "font-size: 13pt; font-weight: bold; color: #a78bfa; background: transparent;"
        )
        layout.addWidget(title)

        desc = QLabel("A fully rigged 2D scene showcasing ZANIME's animation capabilities.")
        desc.setStyleSheet("color: #94a3b8; font-size: 8pt; background: transparent;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.clicked.emit()
        super().keyPressEvent(event)

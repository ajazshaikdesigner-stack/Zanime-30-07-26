"""
Tutorial Progress Dock - Visualizes completion and achievements.
"""

from PySide6.QtWidgets import QProgressBar, QTextEdit, QVBoxLayout

from src.core.sdk.base_dock import BaseDock
from src.models.tutorial_model import Achievement


class TutorialProgressDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Progress & Achievements", parent)

        layout = QVBoxLayout(self.container)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        self.achievements_log = QTextEdit()
        self.achievements_log.setReadOnly(True)
        self.achievements_log.setStyleSheet("background: #1e1e1e; color: gold;")
        layout.addWidget(self.achievements_log)

    def update_progress(self, current: int, total: int):
        percent = int((current / total) * 100)
        self.progress_bar.setValue(percent)

    def log_achievement(self, ach: Achievement):
        self.achievements_log.append(
            f"🏆 ACHIEVEMENT UNLOCKED: {ach.name}\n  - {ach.description}"
        )

"""
Storyboard Canvas
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QScrollArea, QVBoxLayout, QWidget


class StoryboardCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.content = QWidget()
        self.grid = QGridLayout(self.content)

        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll)

    def render_board(self, storyboard_model):
        # Clear grid
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

        row = 0
        col = 0
        for scene in storyboard_model.scenes:
            for shot in scene.shots:
                lbl = QLabel(
                    f"<b>Scene {scene.number}</b> - Shot {shot.number}<br>{shot.shot_type}<br>{shot.duration}s"
                )
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setStyleSheet(
                    "border: 2px solid #555; background-color: #333; padding: 10px;"
                )
                lbl.setFixedSize(200, 150)

                self.grid.addWidget(lbl, row, col)
                col += 1
                if col > 3:
                    col = 0
                    row += 1

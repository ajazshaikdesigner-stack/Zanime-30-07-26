"""
Animation Library Dock - Presets and Search
"""

from PySide6.QtWidgets import QComboBox, QLineEdit, QListWidget, QVBoxLayout

from src.core.sdk.base_dock import BaseDock


class AnimationLibraryDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Animation Library", parent)

        layout = QVBoxLayout(self.container)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search animations...")
        layout.addWidget(self.search)

        self.category = QComboBox()
        self.category.addItems(
            ["All", "Walk Cycles", "Facial Expressions", "Hand Gestures", "Presets"]
        )
        layout.addWidget(self.category)

        self.list = QListWidget()
        self.list.addItems(
            ["Walk_Normal", "Run_Fast", "Laugh_01", "Wave_Hand", "Preset: Anime Fight"]
        )
        layout.addWidget(self.list)

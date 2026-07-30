"""
Character Library Dock
"""

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QVBoxLayout,
)

from src.core.sdk.base_dock import BaseDock


class CharacterLibraryDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Character Library", parent)

        layout = QVBoxLayout(self.container)

        # Search & Filter
        filter_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search characters...")

        self.category_combo = QComboBox()
        self.category_combo.addItems(
            [
                "All",
                "Kids",
                "Adults",
                "Animals",
                "Fantasy",
                "Villains",
                "Robots",
                "Aliens",
                "Historical",
                "Mythology",
                "Crowd",
            ]
        )

        filter_layout.addWidget(self.search_edit)
        filter_layout.addWidget(self.category_combo)
        layout.addLayout(filter_layout)

        # List
        self.library_list = QListWidget()
        layout.addWidget(self.library_list)

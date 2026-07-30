"""
Voice Library Dock - Manages characters and available voice profiles.
"""

from PySide6.QtWidgets import QComboBox, QLineEdit, QListWidget, QVBoxLayout

from src.core.sdk.base_dock import BaseDock


class VoiceLibraryDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Voice Library", parent)

        layout = QVBoxLayout(self.container)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search voices...")
        layout.addWidget(self.search)

        self.category = QComboBox()
        self.category.addItems(
            ["All Voices", "English", "Japanese", "Hero", "Villain", "Narrator"]
        )
        layout.addWidget(self.category)

        self.list = QListWidget()
        self.list.addItems(
            [
                "Hero_Eng_Adult_M",
                "Villain_Jap_Elder_M",
                "Narrator_Eng_F",
                "Child_Happy_Eng",
            ]
        )
        layout.addWidget(self.list)

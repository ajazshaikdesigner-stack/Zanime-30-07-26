"""
Settings Dock for configuring Story AI parameters.
"""

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from src.core.sdk.base_dock import BaseDock


class StorySettingsDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Story Settings", parent)

        layout = QVBoxLayout(self.container)
        form = QFormLayout()

        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter your story idea...")
        self.prompt_edit.setMaximumHeight(100)
        form.addRow("Prompt:", self.prompt_edit)

        self.genre_combo = QComboBox()
        self.genre_combo.addItems(
            [
                "Adventure",
                "Fantasy",
                "Comedy",
                "Drama",
                "Action",
                "Sci-Fi",
                "Mystery",
                "Educational",
                "Kids",
                "Horror",
                "Romance",
                "Custom",
            ]
        )
        form.addRow("Genre:", self.genre_combo)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(
            ["English", "Telugu", "Hindi", "Tamil", "Kannada", "Malayalam", "Japanese"]
        )
        form.addRow("Language:", self.lang_combo)

        self.duration_combo = QComboBox()
        self.duration_combo.addItems(
            ["Short (5 mins)", "Medium (15 mins)", "Long (30+ mins)"]
        )
        form.addRow("Duration:", self.duration_combo)

        self.audience_combo = QComboBox()
        self.audience_combo.addItems(["Kids", "Teens", "Adults", "Everyone"])
        form.addRow("Audience:", self.audience_combo)

        self.art_combo = QComboBox()
        self.art_combo.addItems(["Anime", "Cartoon", "Storybook", "Manga", "Custom"])
        form.addRow("Art Style:", self.art_combo)

        self.movie_combo = QComboBox()
        self.movie_combo.addItems(["Feature Film", "Series Episode", "Short Film"])
        form.addRow("Movie Style:", self.movie_combo)

        layout.addLayout(form)

        self.generate_btn = QPushButton("Generate Story")
        layout.addWidget(self.generate_btn)

        self.lock_btn = QPushButton("Lock Story")
        layout.addWidget(self.lock_btn)

        layout.addStretch()

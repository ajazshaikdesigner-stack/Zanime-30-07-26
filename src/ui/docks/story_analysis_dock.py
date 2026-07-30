"""
Story Analysis Dock for displaying extracted data, validation warnings, and AI scene breakdowns.
"""

import json

from PySide6.QtWidgets import QLabel, QListWidget, QTabWidget, QVBoxLayout

from src.core.sdk.base_dock import BaseDock


class StoryAnalysisDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Story Analysis", parent)

        layout = QVBoxLayout(self.container)

        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(
            "QTabWidget::pane { border: none; } "
            "QTabBar::tab { background:#1e1e2e; color:#888; padding: 4px 10px; border:none; } "
            "QTabBar::tab:selected { color:#ddd; border-bottom: 2px solid #007acc; }"
        )
        layout.addWidget(self._tabs)

        # Tab 1: Validation
        val_widget = QVBoxLayout()
        val_container = __import__("PySide6.QtWidgets", fromlist=["QWidget"]).QWidget()
        val_container.setLayout(val_widget)
        val_widget.addWidget(QLabel("<b>Validation Warnings</b>"))
        self.warnings_list = QListWidget()
        val_widget.addWidget(self.warnings_list)
        val_widget.addWidget(QLabel("<b>Characters Found</b>"))
        self.characters_list = QListWidget()
        val_widget.addWidget(self.characters_list)
        val_widget.addWidget(QLabel("<b>Locations</b>"))
        self.locations_list = QListWidget()
        val_widget.addWidget(self.locations_list)
        val_widget.addWidget(QLabel("<b>Metadata</b>"))
        self.metadata_lbl = QLabel("Duration: 00:00:00\nRating: G\nKeywords: None")
        val_widget.addWidget(self.metadata_lbl)
        self._tabs.addTab(val_container, "Validation")

        # Tab 2: Scene Breakdown (populated by AI)
        breakdown_container = __import__("PySide6.QtWidgets", fromlist=["QWidget"]).QWidget()
        bd_layout = QVBoxLayout(breakdown_container)
        bd_layout.addWidget(QLabel("<b>AI Scene Breakdown</b>"))
        self.breakdown_list = QListWidget()
        bd_layout.addWidget(self.breakdown_list)
        self._tabs.addTab(breakdown_container, "Scenes")

    def update_analysis(self, model, warnings):
        self.warnings_list.clear()
        if warnings:
            self.warnings_list.addItems(warnings)
        else:
            self.warnings_list.addItem("✅ All checks passed")

        self.characters_list.clear()
        self.characters_list.addItems(
            model.characters if model.characters else ["None"]
        )

        self.locations_list.clear()
        self.locations_list.addItems(model.locations if model.locations else ["None"])

        self.metadata_lbl.setText(
            f"Duration: {model.duration_est}\nRating: {model.rating}\nKeywords: {', '.join(model.keywords)}"
        )

    def update_breakdown(self, text: str):
        """Display AI scene breakdown JSON in the Scenes tab."""
        self.breakdown_list.clear()
        self._tabs.setCurrentIndex(1)

        # Try parsing JSON scenes from AI text
        import re
        scenes = []
        match = re.search(r'\[.*?\]', text, re.DOTALL)
        if match:
            try:
                scenes = json.loads(match.group())
            except json.JSONDecodeError:
                pass

        if scenes:
            for s in scenes:
                name = s.get("name", f"Scene {s.get('scene_number', '?')}")
                loc = s.get("location", "Unknown")
                mood = s.get("mood", "")
                chars = ", ".join(s.get("characters", []))
                shots = len(s.get("shots", []))
                self.breakdown_list.addItem(
                    f"🎬 {name} @ {loc} | {mood} | {chars} | {shots} shots"
                )
        else:
            # Show raw text lines
            for line in text.splitlines():
                line = line.strip()
                if line:
                    self.breakdown_list.addItem(line)

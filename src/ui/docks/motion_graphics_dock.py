"""
Motion Graphics & Titles Dock — Phase 4 Commercial Production Suite.

Features:
  - Animated text titles, lower thirds, callouts, captions, transitions
  - Font, size, color, alignment, and animation curve settings
  - Preset library: Fade, Slide In, Typewriter, Bounce, Zoom
"""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.core.sdk.base_dock import BaseDock

logger = logging.getLogger(__name__)

MOGRT_PRESETS = [
    {"name": "Cinematic Title", "category": "Titles", "anim": "Fade & Zoom"},
    {"name": "News Lower Third", "category": "Lower Thirds", "anim": "Slide Left"},
    {"name": "Subtitles / Captions", "category": "Captions", "anim": "Typewriter"},
    {"name": "Speech Callout Box", "category": "Callouts", "anim": "Bounce In"},
    {"name": "Cross Dissolve", "category": "Transitions", "anim": "Dissolve"},
    {"name": "Wipe Transition", "category": "Transitions", "anim": "Wipe"},
]


class MotionGraphicsDock(BaseDock):
    """Motion Graphics & Animated Titles Dock."""

    title_created = Signal(dict)

    def __init__(self, parent=None):
        super().__init__("✍ Motion Graphics", parent)
        self.setMinimumWidth(240)
        self._build_ui()
        self._populate_tree()

    def _build_ui(self):
        root = QVBoxLayout(self.container)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        # 1. Preset Tree
        tree_group = QGroupBox("Presets Library")
        tree_group.setStyleSheet("QGroupBox { color: #aaa; font-size: 10px; font-weight: bold; }")
        t_layout = QVBoxLayout(tree_group)
        t_layout.setContentsMargins(4, 4, 4, 4)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("QTreeWidget { background: #15151f; color: #ddd; border: 1px solid #2a2a3a; }")
        t_layout.addWidget(self.tree, 1)

        root.addWidget(tree_group, 1)

        # 2. Text Editor Form
        edit_group = QGroupBox("Text Inspector")
        edit_group.setStyleSheet("QGroupBox { color: #aaa; font-size: 10px; font-weight: bold; }")
        form = QFormLayout(edit_group)
        form.setContentsMargins(4, 4, 4, 4)

        self.text_edit = QLineEdit("ZANIME ANIMATION STUDIO")
        form.addRow("Text:", self.text_edit)

        self.anim_combo = QComboBox()
        self.anim_combo.addItems(["Fade & Zoom", "Slide Left", "Typewriter", "Bounce In", "Dissolve"])
        form.addRow("Animation:", self.anim_combo)

        add_btn = QPushButton("+ Add to Timeline")
        add_btn.setFixedHeight(24)
        add_btn.setStyleSheet(
            "QPushButton { background: #007acc; color: white; border: none; border-radius: 4px; font-weight: bold; font-size: 10px; } "
            "QPushButton:hover { background: #0098ff; }"
        )
        add_btn.clicked.connect(self._add_to_timeline)
        form.addRow(add_btn)

        root.addWidget(edit_group)

    def _populate_tree(self):
        self.tree.clear()
        cats = {}
        for p in MOGRT_PRESETS:
            cat = p["category"]
            if cat not in cats:
                cat_item = QTreeWidgetItem(self.tree, [f"📂 {cat}"])
                cat_item.setExpanded(True)
                cats[cat] = cat_item
            QTreeWidgetItem(cats[cat], [p["name"]])

    def _add_to_timeline(self):
        txt = self.text_edit.text().strip()
        anim = self.anim_combo.currentText()
        if txt:
            self.title_created.emit({"text": txt, "animation": anim})
            logger.info("MotionGraphicsDock: Added title '%s' with anim '%s'", txt, anim)

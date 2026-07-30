"""
AI History Dock — browsable gallery of all past generations.

Features:
  - Thumbnail grid of past generations (image/text/audio)
  - Filter tabs by type (All / Image / Text / Audio / Music)
  - Click to open detailed entry (prompt, seed, model, output path)
  - Favorite toggle (★)
  - Re-run generation from history entry
  - Subscribes to AI_HISTORY_ENTRY_ADDED for live updates
"""

import logging
import os
import time

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTabBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.sdk.base_dock import BaseDock
from src.core.services.service_registry import registry
from src.models.ai_history_model import AIHistoryEntry, AITaskType

logger = logging.getLogger(__name__)


class HistoryCard(QWidget):
    """Card for a single history entry."""

    clicked = Signal(object)   # Emits the AIHistoryEntry

    def __init__(self, entry: AIHistoryEntry, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.setFixedSize(120, 140)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        # Thumbnail
        self._thumb = QLabel()
        self._thumb.setFixedSize(112, 80)
        self._thumb.setAlignment(Qt.AlignCenter)
        self._thumb.setStyleSheet(
            "background: #1a1a2e; border-radius: 4px; border: 1px solid #333;"
        )

        if entry.task_type == AITaskType.IMAGE.value and entry.output_path:
            if os.path.isfile(entry.output_path):
                pix = QPixmap(entry.output_path).scaled(
                    112, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self._thumb.setPixmap(pix)
            else:
                self._thumb.setText("🖼")
        elif entry.task_type == AITaskType.TEXT.value:
            preview = (entry.prompt[:40] + "…") if len(entry.prompt) > 40 else entry.prompt
            self._thumb.setText(f"💬\n{preview}")
            self._thumb.setWordWrap(True)
            self._thumb.setStyleSheet(
                "background: #0a1a3a; border-radius: 4px; border: 1px solid #333; "
                "color: #7ab; font-size: 9px; padding: 4px;"
            )
        elif entry.task_type in (AITaskType.AUDIO.value, AITaskType.MUSIC.value):
            self._thumb.setText("🎵")
            self._thumb.setStyleSheet(
                "background: #1a2a1a; border-radius: 4px; border: 1px solid #333; "
                "color: #7e7; font-size: 24px;"
            )
        else:
            self._thumb.setText("⚙")

        layout.addWidget(self._thumb)

        # Type label
        type_lbl = QLabel(entry.task_type.title())
        type_lbl.setStyleSheet("color: #888; font-size: 9px;")
        type_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(type_lbl)

        # Model
        model_lbl = QLabel(entry.model_name[:16] if entry.model_name else "—")
        model_lbl.setStyleSheet("color: #666; font-size: 9px;")
        model_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(model_lbl)

        # Favorite button
        self._fav_btn = QPushButton("☆" if not entry.is_favorite else "★")
        self._fav_btn.setFixedSize(20, 16)
        self._fav_btn.setStyleSheet(
            "QPushButton { background:none; border:none; color:#f90; font-size:12px; } "
            "QPushButton:hover { color:#fc0; }"
        )
        self._fav_btn.clicked.connect(self._toggle_fav)
        layout.addWidget(self._fav_btn, 0, Qt.AlignCenter)

        self.setStyleSheet(
            "QWidget { background: #1e1e2e; border: 1px solid #2a2a3a; border-radius: 6px; } "
            "QWidget:hover { border: 1px solid #007acc; }"
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.entry)

    def _toggle_fav(self):
        try:
            from src.core.ai.history_manager import AIHistoryManager
            mgr = registry.get(AIHistoryManager)
            is_fav = mgr.toggle_favorite(self.entry.entry_id)
            self.entry.is_favorite = is_fav
            self._fav_btn.setText("★" if is_fav else "☆")
        except Exception:
            pass


class AIHistoryDock(BaseDock):
    """Scrollable gallery dock for AI generation history."""

    def __init__(self, parent=None):
        super().__init__("🕐 AI History", parent)
        self.setMinimumWidth(280)
        self._cards: list[HistoryCard] = []
        self._build_ui()
        self._connect_events()

    def _build_ui(self):
        root = QVBoxLayout(self.container)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(4)

        # Filter tabs
        self._tabs = QTabBar()
        for tab in ["All", "Image", "Text", "Audio", "Music"]:
            self._tabs.addTab(tab)
        self._tabs.currentChanged.connect(self._apply_filter)
        root.addWidget(self._tabs)

        # Scroll area → wrapping grid layout
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.setStyleSheet("background: #15151f;")

        self._grid_container = QWidget()
        self._grid_container.setStyleSheet("background: #15151f;")
        self._grid_layout = _FlowLayout(self._grid_container, spacing=6)
        self._scroll.setWidget(self._grid_container)
        root.addWidget(self._scroll, 1)

        # Empty state
        self._empty_lbl = QLabel("No generations yet.\nStart creating to build history!")
        self._empty_lbl.setAlignment(Qt.AlignCenter)
        self._empty_lbl.setStyleSheet("color: #555; font-size: 12px; padding: 20px;")
        root.addWidget(self._empty_lbl)

    def _connect_events(self):
        try:
            registry.get(EventBus).subscribe(
                Event.AI_HISTORY_ENTRY_ADDED, self._on_entry_added
            )
        except KeyError:
            pass

    def _on_entry_added(self, entry: AIHistoryEntry):
        self._empty_lbl.hide()
        card = HistoryCard(entry)
        card.clicked.connect(self._on_card_clicked)
        self._cards.append(card)
        self._grid_layout.addWidget(card)
        self._scroll.verticalScrollBar().setValue(0)  # Scroll to top (newest first)

    def _apply_filter(self, idx: int):
        filter_map = {0: None, 1: "image", 2: "text", 3: "audio", 4: "music"}
        f = filter_map.get(idx)
        for card in self._cards:
            card.setVisible(f is None or card.entry.task_type == f)

    def _on_card_clicked(self, entry: AIHistoryEntry):
        # Show a tooltip / mini dialog with full entry details
        from PySide6.QtWidgets import QMessageBox
        msg = (
            f"Type: {entry.task_type}\n"
            f"Model: {entry.model_name}\n"
            f"Seed: {entry.seed}\n"
            f"Prompt: {entry.prompt[:200]}\n"
            f"Output: {entry.output_path}\n"
            f"Time: {time.strftime('%Y-%m-%d %H:%M', time.localtime(entry.timestamp))}"
        )
        QMessageBox.information(self, "Generation Details", msg)

    def load_history(self, entries: list[AIHistoryEntry]):
        """Bulk-load history entries (e.g. after project open)."""
        for entry in reversed(entries):  # Newest first
            self._on_entry_added(entry)


class _FlowLayout(QVBoxLayout):
    """
    Simple row-wrapping layout for cards.
    Uses nested HBoxLayouts to simulate a flow layout without a custom layout engine.
    """

    def __init__(self, parent: QWidget, spacing: int = 6):
        super().__init__(parent)
        self.setSpacing(spacing)
        self.setAlignment(Qt.AlignTop)
        self._spacing = spacing
        self._current_row: QHBoxLayout | None = None
        self._row_count = 0

    def addWidget(self, widget: QWidget):
        if self._current_row is None or self._row_count >= 2:
            row_container = QWidget()
            self._current_row = QHBoxLayout(row_container)
            self._current_row.setSpacing(self._spacing)
            self._current_row.setContentsMargins(0, 0, 0, 0)
            self._current_row.setAlignment(Qt.AlignLeft)
            super().addWidget(row_container)
            self._row_count = 0

        self._current_row.addWidget(widget)
        self._row_count += 1

"""
VFX & Compositing Workspace — Phase 4 Visual Effects Studio.

Features:
  - Particle Physics Simulation (Snow, Rain, Fire, Dust)
  - Color Grading Dock integration (.cube LUTs, Exposure, WB)
  - VFX Layer Stack & 12 Effect Presets
  - Real-time simulation playback loop
"""

import logging

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.core.sdk.base_dock import BaseDock
from src.core.sdk.base_workspace import BaseWorkspace
from src.core.services.particle_engine import ParticleEmitter, ParticlePreset
from src.core.services.vfx_engine import VFXEngine, VFXType
from src.ui.docks.color_grading_dock import ColorGradingDock

logger = logging.getLogger(__name__)


class VFXViewport(QWidget):
    """Real-time preview canvas for particle effects and color grading."""

    def __init__(self, emitter: ParticleEmitter, parent=None):
        super().__init__(parent)
        self.emitter = emitter
        self.setBackgroundRole(QWidget.NoRole)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Canvas background
        painter.fillRect(0, 0, w, h, QColor("#0d0d16"))

        # Render particles
        self.emitter.x = w / 2.0
        self.emitter.y = h / 2.0

        for p in self.emitter.particles:
            c = QColor(p.color)
            c.setAlphaF(p.alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(c))
            painter.drawEllipse(QPointF(p.x, p.y), p.size, p.size)


class VFXLayersDock(BaseDock):
    """Left dock listing active VFX layers & particle preset picker."""

    def __init__(self, parent=None):
        super().__init__("✨ VFX Layers", parent)
        self.setMinimumWidth(220)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self.container)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        # Particle Preset Picker
        part_group = QGroupBox("Particle Preset")
        part_group.setStyleSheet("QGroupBox { color: #aaa; font-size: 10px; font-weight: bold; }")
        part_layout = QVBoxLayout(part_group)
        part_layout.setContentsMargins(4, 4, 4, 4)

        self.preset_combo = QComboBox()
        for p in ParticlePreset:
            self.preset_combo.addItem(p.value)
        part_layout.addWidget(self.preset_combo)

        root.addWidget(part_group)

        # VFX Layers List
        layers_group = QGroupBox("Active VFX Stack")
        layers_group.setStyleSheet("QGroupBox { color: #aaa; font-size: 10px; font-weight: bold; }")
        lay_layout = QVBoxLayout(layers_group)
        lay_layout.setContentsMargins(4, 4, 4, 4)

        self.effect_combo = QComboBox()
        for v in VFXType:
            self.effect_combo.addItem(v.value)
        lay_layout.addWidget(self.effect_combo)

        add_btn = QPushButton("+ Add Effect")
        add_btn.setFixedHeight(22)
        add_btn.setStyleSheet(
            "QPushButton { background: #007acc; color: white; border: none; border-radius: 3px; font-size: 10px; } "
            "QPushButton:hover { background: #0098ff; }"
        )
        lay_layout.addWidget(add_btn)

        self.layers_list = QListWidget()
        self.layers_list.setStyleSheet("QListWidget { background: #15151f; color: #ddd; border: 1px solid #2a2a3a; }")
        lay_layout.addWidget(self.layers_list, 1)

        root.addWidget(layers_group, 1)


class VFXWorkspace(BaseWorkspace):
    """VFX Studio Workspace combining physics particles, visual effects, and color grading."""

    def __init__(self, app, parent=None):
        super().__init__("VFX Studio", parent)
        self.app = app

        self.vfx_engine = VFXEngine()
        self.emitter = ParticleEmitter(ParticlePreset.SNOW.value)

        # Viewport
        self.viewport = VFXViewport(self.emitter, self)
        self.setCentralWidget(self.viewport)

        # Docks
        self.layers_dock = VFXLayersDock(self)
        self.color_dock = ColorGradingDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.layers_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.color_dock)

        # Connect particle preset change
        self.layers_dock.preset_combo.currentTextChanged.connect(self._on_preset_changed)

        # Simulation Loop Timer
        self.sim_timer = QTimer(self)
        self.sim_timer.setInterval(33)  # ~30 fps
        self.sim_timer.timeout.connect(self._sim_tick)
        self.sim_timer.start()

    def _on_preset_changed(self, preset_name: str):
        self.emitter = ParticleEmitter(preset_name)
        self.viewport.emitter = self.emitter
        logger.info("VFXWorkspace: Switched particle preset to '%s'", preset_name)

    def _sim_tick(self):
        self.emitter.update(0.033)
        self.viewport.update()

    def get_required_docks(self):
        return []

    def get_hidden_docks(self):
        return [
            "Properties",
            "Timeline",
            "ProjectExplorer",
            "Console",
            "AssetBrowser",
            "NotificationCenter",
            "History",
            "Preview",
        ]

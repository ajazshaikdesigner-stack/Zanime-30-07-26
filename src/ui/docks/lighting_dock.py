"""
Lighting & Environment Engine Dock — Phase 4 Commercial Production Suite.

Features:
  - Sun (Directional), Point, Spot, Area, HDRI Environment lights
  - Light intensity, color, and shadow quality controls
  - Volumetric lighting scattering slider
  - Ambient Occlusion (AO) radius and intensity settings
"""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from src.core.sdk.base_dock import BaseDock

logger = logging.getLogger(__name__)


class LightingDock(BaseDock):
    """Lighting Engine & Shadow Control Dock."""

    lighting_changed = Signal()

    def __init__(self, parent=None):
        super().__init__("💡 Lighting Engine", parent)
        self.setMinimumWidth(240)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self.container)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        # 1. Light Source Selector
        light_group = QGroupBox("Light Rig")
        light_group.setStyleSheet("QGroupBox { color: #aaa; font-size: 10px; font-weight: bold; }")
        l_form = QFormLayout(light_group)
        l_form.setContentsMargins(4, 4, 4, 4)

        self.light_type_combo = QComboBox()
        self.light_type_combo.addItems(["Sun (Directional)", "Point Light", "Spot Light", "Area Light", "HDRI Environment Map"])
        l_form.addRow("Type:", self.light_type_combo)

        self.intensity_spin = QDoubleSpinBox()
        self.intensity_spin.setRange(0.0, 100.0)
        self.intensity_spin.setValue(1.0)
        self.intensity_spin.valueChanged.connect(lambda: self.lighting_changed.emit())
        l_form.addRow("Intensity:", self.intensity_spin)

        self.shadow_combo = QComboBox()
        self.shadow_combo.addItems(["Soft Shadows (PCSS)", "Hard Shadows", "Off"])
        l_form.addRow("Shadows:", self.shadow_combo)

        root.addWidget(light_group)

        # 2. Environment & Volumetrics
        env_group = QGroupBox("Environment & Volumetrics")
        env_group.setStyleSheet("QGroupBox { color: #aaa; font-size: 10px; font-weight: bold; }")
        e_form = QFormLayout(env_group)
        e_form.setContentsMargins(4, 4, 4, 4)

        self.volumetric_slider = QSlider(Qt.Horizontal)
        self.volumetric_slider.setRange(0, 100)
        self.volumetric_slider.setValue(20)
        e_form.addRow("Volumetric Fog:", self.volumetric_slider)

        self.ao_slider = QSlider(Qt.Horizontal)
        self.ao_slider.setRange(0, 100)
        self.ao_slider.setValue(50)
        e_form.addRow("Ambient Occl. (AO):", self.ao_slider)

        root.addWidget(env_group)
        root.addStretch()

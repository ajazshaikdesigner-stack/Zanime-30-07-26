"""
Color Grading Dock — Phase 4 Commercial Production Suite.

Features:
  - 3D LUT loader (.cube files)
  - Brightness, Contrast, Saturation, Exposure controls
  - White Balance (Temperature & Tint)
  - Tone Mapping presets (Linear, Reinhard, ACES Film, Filmic)
  - Split Toning (Shadow / Highlight Tints)
"""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
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


class ColorGradingDock(BaseDock):
    """Color Grading & LUT adjustment dock."""

    grading_changed = Signal()

    def __init__(self, parent=None):
        super().__init__("🎨 Color Grading", parent)
        self.setMinimumWidth(260)
        self.lut_path = ""
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self.container)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        # 1. 3D LUT Section
        lut_group = QGroupBox("3D LUT")
        lut_group.setStyleSheet("QGroupBox { color: #aaa; font-size: 10px; font-weight: bold; }")
        lut_layout = QHBoxLayout(lut_group)
        lut_layout.setContentsMargins(4, 4, 4, 4)

        self.lut_lbl = QLabel("No LUT Loaded")
        self.lut_lbl.setStyleSheet("color: #777; font-size: 10px;")
        lut_layout.addWidget(self.lut_lbl, 1)

        load_lut_btn = QPushButton("Browse .cube")
        load_lut_btn.setFixedHeight(22)
        load_lut_btn.setStyleSheet(
            "QPushButton { background: #007acc; color: white; border: none; border-radius: 3px; font-size: 10px; padding: 0 8px; } "
            "QPushButton:hover { background: #0098ff; }"
        )
        load_lut_btn.clicked.connect(self._browse_lut)
        lut_layout.addWidget(load_lut_btn)

        root.addWidget(lut_group)

        # 2. Basic Adjustments
        basic_group = QGroupBox("Basic Color")
        basic_group.setStyleSheet("QGroupBox { color: #aaa; font-size: 10px; font-weight: bold; }")
        form = QFormLayout(basic_group)
        form.setContentsMargins(4, 4, 4, 4)

        self.exp_slider = self._create_slider(form, "Exposure:", -100, 100, 0)
        self.bright_slider = self._create_slider(form, "Brightness:", -100, 100, 0)
        self.contrast_slider = self._create_slider(form, "Contrast:", -100, 100, 0)
        self.sat_slider = self._create_slider(form, "Saturation:", -100, 100, 0)

        root.addWidget(basic_group)

        # 3. White Balance & Tone Mapping
        tone_group = QGroupBox("Tone Mapping & WB")
        tone_group.setStyleSheet("QGroupBox { color: #aaa; font-size: 10px; font-weight: bold; }")
        tone_form = QFormLayout(tone_group)
        tone_form.setContentsMargins(4, 4, 4, 4)

        self.temp_slider = self._create_slider(tone_form, "Temp (K):", -50, 50, 0)
        self.tint_slider = self._create_slider(tone_form, "Tint:", -50, 50, 0)

        self.tone_combo = QComboBox()
        self.tone_combo.addItems(["Linear", "Reinhard", "ACES Film", "Filmic", "AgX"])
        tone_form.addRow("Tone Curve:", self.tone_combo)

        root.addWidget(tone_group)

        # Reset Button
        reset_btn = QPushButton("Reset All Adjustments")
        reset_btn.setFixedHeight(24)
        reset_btn.setStyleSheet(
            "QPushButton { background: #2a2a3a; color: #aaa; border: 1px solid #444; border-radius: 4px; font-size: 10px; } "
            "QPushButton:hover { background: #444; color: white; }"
        )
        reset_btn.clicked.connect(self.reset_all)
        root.addWidget(reset_btn)

        root.addStretch()

    def _create_slider(self, form: QFormLayout, label: str, min_v: int, max_v: int, default_v: int) -> QSlider:
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_v, max_v)
        slider.setValue(default_v)
        slider.valueChanged.connect(lambda: self.grading_changed.emit())
        form.addRow(label, slider)
        return slider

    def _browse_lut(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select 3D LUT", "", "Cube LUT Files (*.cube);;All Files (*)"
        )
        if file_path:
            self.lut_path = file_path
            import os
            self.lut_lbl.setText(os.path.basename(file_path))
            self.lut_lbl.setStyleSheet("color: #7ec97e; font-size: 10px; font-weight: bold;")
            self.grading_changed.emit()

    def reset_all(self):
        self.exp_slider.setValue(0)
        self.bright_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.sat_slider.setValue(0)
        self.temp_slider.setValue(0)
        self.tint_slider.setValue(0)
        self.lut_path = ""
        self.lut_lbl.setText("No LUT Loaded")
        self.lut_lbl.setStyleSheet("color: #777; font-size: 10px;")
        self.grading_changed.emit()

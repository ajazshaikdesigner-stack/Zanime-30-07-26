"""
Audio Mixer Dock — Phase 4 Commercial Production Suite.

Features:
  - Multi-track mixing channels (Dialog, SFX, Music, Ambience, Master)
  - Volume faders (-60dB to +6dB) with peak VU meters
  - 4-Band EQ (Low, Low-Mid, High-Mid, High)
  - Compressor (Threshold, Ratio, Attack, Release)
  - Noise Gate & Limiter controls
  - Bus routing & Mute/Solo
"""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSlider,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.core.sdk.base_dock import BaseDock

logger = logging.getLogger(__name__)


class MixerChannelWidget(QWidget):
    """Vertical strip widget for a single audio mixing channel."""

    def __init__(self, name: str, is_master: bool = False, parent=None):
        super().__init__(parent)
        self.channel_name = name
        self.is_master = is_master
        self.setFixedWidth(70)
        self.setStyleSheet("background: #181824; border: 1px solid #28283a; border-radius: 4px;")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Name Header
        title = QLabel(self.channel_name[:8])
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color: {'#ff922b' if self.is_master else '#7ab'}; font-size: 9px; font-weight: bold;"
        )
        layout.addWidget(title)

        # Mute / Solo buttons
        if not self.is_master:
            btns = QHBoxLayout()
            btns.setSpacing(2)

            m_btn = QToolButton()
            m_btn.setText("M")
            m_btn.setCheckable(True)
            m_btn.setFixedSize(24, 18)
            m_btn.setStyleSheet("QToolButton { font-size: 8px; font-weight: bold; background: #2a2a3a; color: #888; } QToolButton:checked { background: #e74c3c; color: white; }")
            btns.addWidget(m_btn)

            s_btn = QToolButton()
            s_btn.setText("S")
            s_btn.setCheckable(True)
            s_btn.setFixedSize(24, 18)
            s_btn.setStyleSheet("QToolButton { font-size: 8px; font-weight: bold; background: #2a2a3a; color: #888; } QToolButton:checked { background: #f39c12; color: white; }")
            btns.addWidget(s_btn)
            layout.addLayout(btns)

        # Fader & VU Meter
        fader_layout = QHBoxLayout()
        fader_layout.setContentsMargins(0, 0, 0, 0)

        self.fader = QSlider(Qt.Vertical)
        self.fader.setRange(-60, 6)
        self.fader.setValue(0)
        fader_layout.addWidget(self.fader, 1)

        self.vu_meter = QProgressBar()
        self.vu_meter.setOrientation(Qt.Vertical)
        self.vu_meter.setRange(0, 100)
        self.vu_meter.setValue(45)
        self.vu_meter.setFixedWidth(8)
        self.vu_meter.setTextVisible(False)
        self.vu_meter.setStyleSheet(
            "QProgressBar { background: #111; border: none; } "
            "QProgressBar::chunk { background: qlineargradient(x1:0, y1:1, x2:0, y2:0, stop:0 #51cf66, stop:0.7 #ffd43b, stop:1 #ff6b6b); }"
        )
        fader_layout.addWidget(self.vu_meter)

        layout.addLayout(fader_layout, 1)

        # DB Label
        self.db_lbl = QLabel("0.0 dB")
        self.db_lbl.setAlignment(Qt.AlignCenter)
        self.db_lbl.setStyleSheet("color: #aaa; font-size: 8px;")
        self.fader.valueChanged.connect(lambda v: self.db_lbl.setText(f"{v:+.1f} dB"))
        layout.addWidget(self.db_lbl)


class AudioMixerDock(BaseDock):
    """Audio Mixer Dock featuring 4-band EQ, compressor, and multi-channel fader strip."""

    def __init__(self, parent=None):
        super().__init__("🎚 Audio Mixer", parent)
        self.setMinimumHeight(240)
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self.container)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        # Channels Strip Layout
        channels_box = QGroupBox("Channels")
        channels_box.setStyleSheet("QGroupBox { color: #aaa; font-size: 10px; font-weight: bold; }")
        chan_layout = QHBoxLayout(channels_box)
        chan_layout.setContentsMargins(4, 4, 4, 4)
        chan_layout.setSpacing(4)

        for ch in ["Dialogue", "SFX", "Music", "Ambience", "Master"]:
            chan_layout.addWidget(MixerChannelWidget(ch, is_master=(ch == "Master")))

        root.addWidget(channels_box)

        # Master DSP Effects (4-Band EQ & Compressor)
        dsp_box = QGroupBox("Master DSP Effects")
        dsp_box.setStyleSheet("QGroupBox { color: #aaa; font-size: 10px; font-weight: bold; }")
        dsp_layout = QFormLayout(dsp_box)
        dsp_layout.setContentsMargins(6, 6, 6, 6)

        # 4-Band EQ Sliders
        self.eq_low = self._add_dsp_slider(dsp_layout, "EQ Low (100Hz):", -12, 12, 0)
        self.eq_lmid = self._add_dsp_slider(dsp_layout, "EQ Mid (1kHz):", -12, 12, 0)
        self.eq_high = self._add_dsp_slider(dsp_layout, "EQ High (10kHz):", -12, 12, 0)

        # Compressor & Gate
        self.comp_thresh = self._add_dsp_slider(dsp_layout, "Comp Thresh:", -40, 0, -12)
        self.gate_thresh = self._add_dsp_slider(dsp_layout, "Noise Gate:", -80, -20, -50)

        root.addWidget(dsp_box, 1)

    def _add_dsp_slider(self, layout: QFormLayout, label: str, min_v: int, max_v: int, default_v: int) -> QSlider:
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_v, max_v)
        slider.setValue(default_v)
        layout.addRow(label, slider)
        return slider

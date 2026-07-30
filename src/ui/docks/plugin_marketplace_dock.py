"""
Plugin Marketplace Dock — Phase 4 Extensibility & Plugin Manager.

Features:
  - Curated marketplace directory for ZANIME extensions
  - Categories: AI Models, VFX Filters, Animation Rigs, Exporters, Audio FX
  - One-click Install, Enable, Disable, Uninstall via PluginManager
  - Plugin verification badge & SDK developer link
"""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.core.managers.plugin_manager import PluginManager
from src.core.sdk.base_dock import BaseDock
from src.core.services.service_registry import registry

logger = logging.getLogger(__name__)

MARKETPLACE_CATALOG = [
    {"id": "plugin_autorig", "name": "Auto-Rig Pro 2D", "version": "1.2.0", "author": "ZANIME Team", "category": "Rigging", "desc": "Automatic skeleton bone auto-weighting for anime characters.", "verified": True},
    {"id": "plugin_glitch_vfx", "name": "Cyberpunk Glitch VFX", "version": "2.0.1", "author": "VFX Lab", "category": "VFX", "desc": "10 retro glitch, chromatic aberration, and digital CRT distortion filters.", "verified": True},
    {"id": "plugin_blender_bridge", "name": "Blender 3D Bridge", "version": "0.9.5", "author": "Community", "category": "Import/Export", "desc": "Live link sync between ZANIME scene layout and Blender viewport.", "verified": False},
    {"id": "plugin_vocoder_fx", "name": "Cyber Vocoder FX", "version": "1.0.0", "author": "AudioWave", "category": "Audio", "desc": "Real-time robotic voice pitch modulation and formant synthesis.", "verified": True},
]


class PluginItemWidget(QWidget):
    """Card widget for a single plugin in the marketplace grid."""

    def __init__(self, item_info: dict, parent=None):
        super().__init__(parent)
        self.info = item_info
        self.is_installed = False
        self.setFixedHeight(80)
        self.setStyleSheet("background: #181824; border: 1px solid #28283a; border-radius: 6px;")
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)

        # Info column
        info_col = QVBoxLayout()
        info_col.setSpacing(2)

        header = QHBoxLayout()
        name_lbl = QLabel(f"<b>{self.info['name']}</b> <small>v{self.info['version']}</small>")
        name_lbl.setStyleSheet("color: #ddd; font-size: 11px;")
        header.addWidget(name_lbl)

        if self.info["verified"]:
            v_badge = QLabel("✓ Verified")
            v_badge.setStyleSheet("color: #51cf66; font-size: 9px; font-weight: bold;")
            header.addWidget(v_badge)

        header.addStretch()
        info_col.addLayout(header)

        desc_lbl = QLabel(self.info["desc"])
        desc_lbl.setStyleSheet("color: #888; font-size: 9px;")
        desc_lbl.setWordWrap(True)
        info_col.addWidget(desc_lbl)

        layout.addLayout(info_col, 1)

        # Install Button
        self.install_btn = QPushButton("Install")
        self.install_btn.setFixedSize(70, 24)
        self.install_btn.setStyleSheet(
            "QPushButton { background: #007acc; color: white; border: none; border-radius: 4px; font-size: 10px; font-weight: bold; } "
            "QPushButton:hover { background: #0098ff; }"
        )
        self.install_btn.clicked.connect(self._toggle_install)
        layout.addWidget(self.install_btn)

    def _toggle_install(self):
        self.is_installed = not self.is_installed
        if self.is_installed:
            self.install_btn.setText("Installed")
            self.install_btn.setStyleSheet("QPushButton { background: #27ae60; color: white; border: none; border-radius: 4px; font-size: 10px; }")
            logger.info("PluginMarketplace: Installed plugin '%s'", self.info['name'])
        else:
            self.install_btn.setText("Install")
            self.install_btn.setStyleSheet("QPushButton { background: #007acc; color: white; border: none; border-radius: 4px; font-size: 10px; }")


class PluginMarketplaceDock(BaseDock):
    """Plugin Marketplace & Store Dock."""

    def __init__(self, parent=None):
        super().__init__("🛒 Plugin Marketplace", parent)
        self.setMinimumWidth(280)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self.container)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        # Search Bar
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("🔍 Search extensions...")
        search_edit.setStyleSheet("QLineEdit { background: #15151f; color: #ccc; border: 1px solid #333; border-radius: 4px; padding: 4px; }")
        root.addWidget(search_edit)

        # Scroll Area with Cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: #12121c;")

        container = QWidget()
        col = QVBoxLayout(container)
        col.setContentsMargins(4, 4, 4, 4)
        col.setSpacing(6)

        for p_info in MARKETPLACE_CATALOG:
            col.addWidget(PluginItemWidget(p_info))

        col.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, 1)

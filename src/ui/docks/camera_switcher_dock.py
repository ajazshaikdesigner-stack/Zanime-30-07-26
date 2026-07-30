"""
Camera Switcher Dock — Live multi-camera switching panel.

Features:
  - List all cameras in the active CameraRig
  - Thumbnail preview card per camera (shows live viewport state)
  - ONE-CLICK live cut: instantly switches active camera
  - Add / Remove / Rename cameras
  - Record a camera switch event to the timeline (frame stamped)
  - Color-coded camera badges (matching timeline track colors)
  - Keyboard shortcut display (Cam 1-9 via number keys)
"""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.sdk.base_dock import BaseDock
from src.core.services.service_registry import registry
from src.models.camera_model import Camera, CameraRig

logger = logging.getLogger(__name__)

# Camera accent colors (cycling)
_CAMERA_COLORS = [
    "#4a9aff", "#ff6b6b", "#51cf66", "#ffd43b",
    "#cc5de8", "#ff922b", "#20c997", "#f06595",
    "#74c0fc", "#a9e34b",
]


class CameraCard(QWidget):
    """Widget representing one camera in the switcher grid."""

    cut_requested = Signal(str)    # camera_uuid
    rename_requested = Signal(str)
    remove_requested = Signal(str)

    def __init__(self, camera: Camera, index: int, parent=None):
        super().__init__(parent)
        self.camera = camera
        self._index = index
        self.setFixedSize(140, 110)
        self.setCursor(Qt.PointingHandCursor)
        self._build_ui()
        self.set_active(camera.is_active)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        # Color badge header
        header = QHBoxLayout()
        self._color_dot = QLabel("●")
        self._color_dot.setFixedWidth(16)
        self._color_dot.setStyleSheet(f"color: {self.camera.color}; font-size: 14px;")
        header.addWidget(self._color_dot)

        self._name_lbl = QLabel(self.camera.name[:16])
        self._name_lbl.setStyleSheet("color: #ddd; font-size: 10px; font-weight: bold;")
        header.addWidget(self._name_lbl, 1)

        # Keyboard shortcut hint
        shortcut = QLabel(f"[{self._index + 1}]" if self._index < 9 else "")
        shortcut.setStyleSheet("color: #555; font-size: 9px;")
        header.addWidget(shortcut)
        layout.addLayout(header)

        # Preview area
        self._preview = QLabel("📷")
        self._preview.setAlignment(Qt.AlignCenter)
        self._preview.setFixedHeight(50)
        self._preview.setStyleSheet(
            "background: #0d0d1a; border: 1px solid #333; border-radius: 4px; "
            "color: #555; font-size: 20px;"
        )
        layout.addWidget(self._preview)

        # CUT button
        self._cut_btn = QPushButton("CUT")
        self._cut_btn.setFixedHeight(20)
        self._cut_btn.setStyleSheet(
            "QPushButton { background: #2a2a3a; border: 1px solid #444; color: #aaa; "
            "border-radius: 3px; font-size: 9px; font-weight: bold; } "
            "QPushButton:hover { background: #007acc; color: white; border-color: #007acc; }"
        )
        self._cut_btn.clicked.connect(lambda: self.cut_requested.emit(self.camera.uuid))
        layout.addWidget(self._cut_btn)

        self.setStyleSheet(
            "QWidget { background: #1e1e2e; border: 1px solid #2a2a3a; border-radius: 6px; }"
        )

        # Context: right-click
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def set_active(self, active: bool):
        border = self.camera.color if active else "#2a2a3a"
        self.setStyleSheet(
            f"QWidget {{ background: #1e1e2e; border: 2px solid {border}; border-radius: 6px; }}"
        )
        self._cut_btn.setText("● LIVE" if active else "CUT")
        self._cut_btn.setStyleSheet(
            f"QPushButton {{ background: {'#1a3a1a' if active else '#2a2a3a'}; "
            f"border: 1px solid {self.camera.color if active else '#444'}; "
            f"color: {'#51cf66' if active else '#aaa'}; "
            "border-radius: 3px; font-size: 9px; font-weight: bold; } "
            "QPushButton:hover { background: #007acc; color: white; }"
        )

    def _show_context_menu(self, pos):
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background: #1e1e2e; border: 1px solid #333; color: #ddd; } "
            "QMenu::item:selected { background: #007acc; }"
        )
        rename = menu.addAction("✏ Rename")
        remove = menu.addAction("✕ Remove")
        action = menu.exec(self.mapToGlobal(pos))
        if action == rename:
            self.rename_requested.emit(self.camera.uuid)
        elif action == remove:
            self.remove_requested.emit(self.camera.uuid)


class CameraSwitcherDock(BaseDock):
    """Live multi-camera switcher panel."""

    camera_switched = Signal(str)  # emits camera_uuid on cut

    def __init__(self, rig: CameraRig, parent=None):
        super().__init__("🎬 Camera Switcher", parent)
        self.rig = rig
        self._cards: dict[str, CameraCard] = {}
        self.setMinimumWidth(320)
        self._build_ui()
        self._refresh_cards()

    def _build_ui(self):
        root = QVBoxLayout(self.container)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        # Toolbar
        toolbar = QHBoxLayout()
        add_btn = QPushButton("+ Add Camera")
        add_btn.setFixedHeight(24)
        add_btn.setStyleSheet(
            "QPushButton { background: #007acc; border: none; border-radius: 4px; "
            "color: white; font-size: 10px; padding: 0 10px; } "
            "QPushButton:hover { background: #0098ff; }"
        )
        add_btn.clicked.connect(self._add_camera)
        toolbar.addWidget(add_btn)
        toolbar.addStretch()

        self._frame_lbl = QLabel("Frame: 0")
        self._frame_lbl.setStyleSheet("color: #555; font-size: 10px;")
        toolbar.addWidget(self._frame_lbl)

        stamp_btn = QPushButton("⏺ Record Switch")
        stamp_btn.setFixedHeight(24)
        stamp_btn.setStyleSheet(
            "QPushButton { background: #3a1a1a; border: 1px solid #6a2a2a; "
            "border-radius: 4px; color: #c97e7e; font-size: 10px; padding: 0 8px; } "
            "QPushButton:hover { background: #6a2a2a; color: white; }"
        )
        stamp_btn.clicked.connect(self._record_switch)
        toolbar.addWidget(stamp_btn)
        root.addLayout(toolbar)

        # Scrollable card grid
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.setStyleSheet("background: #15151f;")

        self._grid_container = QWidget()
        self._grid_container.setStyleSheet("background: #15151f;")
        self._grid_layout = QHBoxLayout(self._grid_container)
        self._grid_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._grid_layout.setSpacing(8)
        self._grid_layout.setContentsMargins(4, 4, 4, 4)
        self._scroll.setWidget(self._grid_container)
        root.addWidget(self._scroll, 1)

        # Active camera info bar
        self._info_bar = QLabel("Active: —")
        self._info_bar.setStyleSheet(
            "background: #1a2a3a; color: #7ab; padding: 4px 8px; "
            "border-radius: 4px; font-size: 10px;"
        )
        root.addWidget(self._info_bar)

    def _refresh_cards(self):
        # Remove old cards
        for card in self._cards.values():
            self._grid_layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()

        for i, cam in enumerate(self.rig.cameras):
            cam.color = _CAMERA_COLORS[i % len(_CAMERA_COLORS)]
            card = CameraCard(cam, i)
            card.cut_requested.connect(self._on_cut)
            card.rename_requested.connect(self._on_rename)
            card.remove_requested.connect(self._on_remove)
            self._cards[cam.uuid] = card
            self._grid_layout.addWidget(card)

        self._update_info_bar()

    def _on_cut(self, camera_uuid: str):
        self.rig.switch_to(camera_uuid)
        for uuid, card in self._cards.items():
            card.set_active(uuid == camera_uuid)
        self._update_info_bar()
        self.camera_switched.emit(camera_uuid)

        # Publish to event bus
        try:
            registry.get(EventBus).publish(Event.CAMERA_SWITCHED, {
                "camera_uuid": camera_uuid,
                "camera_name": self.rig.get_active().name if self.rig.get_active() else "",
            })
        except Exception:
            pass

    def _on_rename(self, camera_uuid: str):
        cam = next((c for c in self.rig.cameras if c.uuid == camera_uuid), None)
        if not cam:
            return
        new_name, ok = QInputDialog.getText(self, "Rename Camera", "Camera name:", text=cam.name)
        if ok and new_name.strip():
            cam.name = new_name.strip()
            self._cards[camera_uuid]._name_lbl.setText(cam.name[:16])

    def _on_remove(self, camera_uuid: str):
        if len(self.rig.cameras) <= 1:
            QMessageBox.warning(self, "Cannot Remove", "Must have at least one camera.")
            return
        self.rig.cameras = [c for c in self.rig.cameras if c.uuid != camera_uuid]
        if self.rig.active_camera_uuid == camera_uuid:
            self.rig.active_camera_uuid = self.rig.cameras[0].uuid
            self.rig.cameras[0].is_active = True
        self._refresh_cards()

    def _add_camera(self):
        name, ok = QInputDialog.getText(
            self, "Add Camera", "Camera name:",
            text=f"Camera {len(self.rig.cameras) + 1}"
        )
        if ok and name.strip():
            self.rig.add_camera(name.strip())
            self._refresh_cards()

    def _record_switch(self):
        try:
            from src.core.events.event_types import Event
            registry.get(EventBus).publish(Event.CAMERA_SWITCH_RECORDED, {
                "camera_uuid": self.rig.active_camera_uuid,
                "camera_name": self.rig.get_active().name if self.rig.get_active() else "",
            })
        except Exception:
            pass

    def _update_info_bar(self):
        active = self.rig.get_active()
        if active:
            self._info_bar.setText(
                f"Active: {active.name}  |  Zoom: {active.zoom:.2f}×  |  "
                f"Lens: {active.lens_type}  |  Ratio: {active.aspect_ratio}"
            )
        else:
            self._info_bar.setText("Active: —")

    def set_frame(self, frame: int):
        self._frame_lbl.setText(f"Frame: {frame}")

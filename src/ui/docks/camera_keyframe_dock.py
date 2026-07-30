"""
Camera Keyframe & Movement Presets Dock — Phase 4 Multi-Camera System.

Features:
  - Add / edit / delete keyframes for active camera (X, Y, Zoom, Rotation, Focus)
  - Keyframe list with frame number, property, value, and easing curve
  - One-click Movement Presets (Pan Left/Right, Tilt Up/Down, Zoom In/Out, Dolly, Orbit, Crane, Handheld Shake)
  - Live keyframe value preview & curve selection (Linear, Ease In/Out, Bezier)
"""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.sdk.base_dock import BaseDock
from src.core.services.service_registry import registry
from src.models.camera_model import (
    PRESET_KEYFRAMES,
    CameraAnimationTrack,
    CameraKeyframe,
    CameraMovementPreset,
    CameraRig,
    EasingType,
)

logger = logging.getLogger(__name__)


class CameraKeyframeDock(BaseDock):
    """Dock for camera keyframe animation control and movement presets."""

    keyframe_changed = Signal()

    def __init__(self, rig: CameraRig, parent=None):
        super().__init__("📹 Camera Animation", parent)
        self.rig = rig
        self._current_frame = 0
        self.setMinimumWidth(300)
        self._build_ui()
        self._refresh_keyframe_table()

    def _build_ui(self):
        root = QVBoxLayout(self.container)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        # Preset Buttons Group
        preset_group = QGroupBox("Movement Presets")
        preset_group.setStyleSheet("QGroupBox { color: #aaa; font-size: 10px; font-weight: bold; }")
        preset_layout = QVBoxLayout(preset_group)
        preset_layout.setContentsMargins(4, 4, 4, 4)

        preset_grid = QHBoxLayout()
        self._preset_combo = QComboBox()
        for preset in CameraMovementPreset:
            self._preset_combo.addItem(preset.value)
        preset_grid.addWidget(self._preset_combo, 1)

        apply_preset_btn = QPushButton("Apply Preset")
        apply_preset_btn.setFixedHeight(24)
        apply_preset_btn.setStyleSheet(
            "QPushButton { background: #007acc; border: none; border-radius: 4px; color: white; font-size: 10px; } "
            "QPushButton:hover { background: #0098ff; }"
        )
        apply_preset_btn.clicked.connect(self._apply_selected_preset)
        preset_grid.addWidget(apply_preset_btn)
        preset_layout.addLayout(preset_grid)

        root.addWidget(preset_group)

        # Keyframe Editor Form
        editor_group = QGroupBox("Add Keyframe")
        editor_group.setStyleSheet("QGroupBox { color: #aaa; font-size: 10px; font-weight: bold; }")
        form = QFormLayout(editor_group)
        form.setContentsMargins(4, 4, 4, 4)

        self._prop_combo = QComboBox()
        self._prop_combo.addItems(["x", "y", "zoom", "rotation", "focus_distance"])
        form.addRow("Property:", self._prop_combo)

        self._frame_spin = QSpinBox()
        self._frame_spin.setRange(0, 9999)
        self._frame_spin.setValue(self._current_frame)
        form.addRow("Frame:", self._frame_spin)

        self._val_spin = QDoubleSpinBox()
        self._val_spin.setRange(-9999.0, 9999.0)
        self._val_spin.setSingleStep(0.1)
        form.addRow("Value:", self._val_spin)

        self._easing_combo = QComboBox()
        for e in EasingType:
            self._easing_combo.addItem(e.value)
        form.addRow("Easing:", self._easing_combo)

        add_kf_btn = QPushButton("+ Set Keyframe")
        add_kf_btn.setFixedHeight(24)
        add_kf_btn.setStyleSheet(
            "QPushButton { background: #2a3a2a; border: 1px solid #4a6a4a; border-radius: 4px; color: #7ec97e; font-size: 10px; } "
            "QPushButton:hover { background: #3a5a3a; color: white; }"
        )
        add_kf_btn.clicked.connect(self._add_keyframe)
        form.addRow(add_kf_btn)

        root.addWidget(editor_group)

        # Keyframes Table
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Frame", "Property", "Value", "Easing"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setStyleSheet(
            "QTableWidget { background: #15151f; color: #ccc; border: 1px solid #2a2a3a; gridline-color: #222; } "
            "QHeaderView::section { background: #1e1e2e; color: #888; font-size: 9px; border: none; }"
        )
        root.addWidget(self._table, 1)

        # Bottom Actions
        actions = QHBoxLayout()
        del_btn = QPushButton("Delete Selected")
        del_btn.setFixedHeight(22)
        del_btn.setStyleSheet(
            "QPushButton { background: #3a1a1a; border: 1px solid #5a2a2a; color: #e77; border-radius: 3px; font-size: 10px; } "
            "QPushButton:hover { background: #5a2a2a; color: white; }"
        )
        del_btn.clicked.connect(self._delete_selected_keyframe)
        actions.addWidget(del_btn)

        clear_btn = QPushButton("Clear All Tracks")
        clear_btn.setFixedHeight(22)
        clear_btn.setStyleSheet(
            "QPushButton { background: #2a2a3a; border: 1px solid #444; color: #aaa; border-radius: 3px; font-size: 10px; } "
            "QPushButton:hover { background: #444; color: white; }"
        )
        clear_btn.clicked.connect(self._clear_all_tracks)
        actions.addWidget(clear_btn)

        root.addLayout(actions)

    def set_current_frame(self, frame: int):
        self._current_frame = frame
        self._frame_spin.setValue(frame)

    def _add_keyframe(self):
        cam = self.rig.get_active()
        if not cam:
            return

        prop_name = self._prop_combo.currentText()
        frame = self._frame_spin.value()
        val = self._val_spin.value()
        easing = self._easing_combo.currentText()

        # Find or create track for this property & camera
        track = next(
            (t for t in self.rig.animation_tracks if t.camera_uuid == cam.uuid and t.property_name == prop_name),
            None,
        )
        if not track:
            track = CameraAnimationTrack(property_name=prop_name, camera_uuid=cam.uuid)
            self.rig.animation_tracks.append(track)

        # Upsert keyframe
        kf = next((k for k in track.keyframes if k.frame == frame), None)
        if kf:
            kf.value = val
            kf.easing = easing
        else:
            track.keyframes.append(CameraKeyframe(frame=frame, value=val, easing=easing))

        self._refresh_keyframe_table()
        self.keyframe_changed.emit()

        try:
            registry.get(EventBus).publish(Event.CAMERA_KEYFRAME_ADDED, {
                "camera_uuid": cam.uuid,
                "property": prop_name,
                "frame": frame,
                "value": val,
            })
        except Exception:
            pass

    def _apply_selected_preset(self):
        cam = self.rig.get_active()
        if not cam:
            return

        preset_name = self._preset_combo.currentText()
        kf_specs = PRESET_KEYFRAMES.get(preset_name, [])

        start_frame = self._current_frame
        for kf_data in kf_specs:
            prop_name = kf_data["prop"]
            target_frame = start_frame + kf_data["frame"]
            val = kf_data["value"]

            track = next(
                (t for t in self.rig.animation_tracks if t.camera_uuid == cam.uuid and t.property_name == prop_name),
                None,
            )
            if not track:
                track = CameraAnimationTrack(property_name=prop_name, camera_uuid=cam.uuid)
                self.rig.animation_tracks.append(track)

            kf = next((k for k in track.keyframes if k.frame == target_frame), None)
            if kf:
                kf.value = val
            else:
                track.keyframes.append(CameraKeyframe(frame=target_frame, value=val))

        self._refresh_keyframe_table()
        self.keyframe_changed.emit()
        logger.info("CameraKeyframeDock: Applied preset '%s' starting at frame %d", preset_name, start_frame)

    def _refresh_keyframe_table(self):
        self._table.setRowCount(0)
        cam = self.rig.get_active()
        if not cam:
            return

        tracks = self.rig.get_tracks_for_camera(cam.uuid)
        row_idx = 0
        for track in tracks:
            for kf in sorted(track.keyframes, key=lambda k: k.frame):
                self._table.insertRow(row_idx)
                self._table.setItem(row_idx, 0, QTableWidgetItem(str(kf.frame)))
                self._table.setItem(row_idx, 1, QTableWidgetItem(track.property_name))
                self._table.setItem(row_idx, 2, QTableWidgetItem(f"{kf.value:.2f}"))
                self._table.setItem(row_idx, 3, QTableWidgetItem(kf.easing))
                row_idx += 1

    def _delete_selected_keyframe(self):
        row = self._table.currentRow()
        if row < 0:
            return

        frame_item = self._table.item(row, 0)
        prop_item = self._table.item(row, 1)
        if not frame_item or not prop_item:
            return

        frame = int(frame_item.text())
        prop_name = prop_item.text()
        cam = self.rig.get_active()
        if not cam:
            return

        track = next(
            (t for t in self.rig.animation_tracks if t.camera_uuid == cam.uuid and t.property_name == prop_name),
            None,
        )
        if track:
            track.keyframes = [k for k in track.keyframes if k.frame != frame]
            self._refresh_keyframe_table()
            self.keyframe_changed.emit()

    def _clear_all_tracks(self):
        cam = self.rig.get_active()
        if not cam:
            return

        self.rig.animation_tracks = [t for t in self.rig.animation_tracks if t.camera_uuid != cam.uuid]
        self._refresh_keyframe_table()
        self.keyframe_changed.emit()

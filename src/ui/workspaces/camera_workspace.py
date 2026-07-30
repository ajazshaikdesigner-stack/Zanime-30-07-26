"""
Camera Director Workspace — Phase 4 Multi-Camera Suite.

Features:
  - Multi-Camera Rig management
  - Live Camera Switcher Dock
  - Keyframe & Movement Presets Dock
  - Animated keyframe evaluation on playback timer
  - Real-time viewport update
"""

import logging

from PySide6.QtCore import Qt, QTimer

from src.core.ai import ZanimeAIAPI
from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.sdk.base_workspace import BaseWorkspace
from src.core.services.service_registry import registry
from src.models.camera_model import Camera, CameraRig, CameraTimeline
from src.ui.docks.ai_console_dock import AIConsoleDock
from src.ui.docks.camera_keyframe_dock import CameraKeyframeDock
from src.ui.docks.camera_library_dock import CameraLibraryDock
from src.ui.docks.camera_properties_dock import CameraPropertiesDock
from src.ui.docks.camera_switcher_dock import CameraSwitcherDock
from src.ui.docks.camera_timeline_dock import CameraTimelineDock
from src.ui.widgets.camera_viewport import CameraViewport

logger = logging.getLogger(__name__)


class CameraWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Camera Director", parent)
        self.app = app

        # Multi-camera rig model
        self.rig = CameraRig()
        cam1 = self.rig.add_camera("Main Camera")
        self.rig.add_camera("Wide Shot")
        self.rig.add_camera("Close Up")

        self.timeline_data = CameraTimeline()
        self.active_camera = cam1

        self._current_frame = 0
        self._is_playing = False

        # Central Viewport
        self.viewport = CameraViewport(self)
        self.setCentralWidget(self.viewport)

        # Docks
        self.library_dock = CameraLibraryDock(self)
        self.properties_dock = CameraPropertiesDock(self)
        self.timeline_dock = CameraTimelineDock(self)
        self.console_dock = AIConsoleDock(self)

        # Phase 4 Docks
        self.switcher_dock = CameraSwitcherDock(self.rig, self)
        self.keyframe_dock = CameraKeyframeDock(self.rig, self)

        # Dock Layout
        self.addDockWidget(Qt.LeftDockWidgetArea, self.library_dock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.switcher_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.keyframe_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.timeline_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)

        self.tabifyDockWidget(self.timeline_dock, self.console_dock)
        self.timeline_dock.raise_()

        # Connect signals
        self.switcher_dock.camera_switched.connect(self._on_camera_switched)
        self.keyframe_dock.keyframe_changed.connect(self._on_keyframe_changed)
        self.properties_dock.comp_rule.currentTextChanged.connect(self._on_comp_rule_changed)
        self.properties_dock.generate_btn.clicked.connect(self._generate_camera_plan)

        # Playback animation timer
        self.play_timer = QTimer(self)
        self.play_timer.setInterval(41)  # ~24 fps
        self.play_timer.timeout.connect(self._on_animation_tick)

        # Autosave timer
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30 * 1000)

        self.properties_dock.load_camera(self.active_camera)

    def _on_camera_switched(self, camera_uuid: str):
        cam = self.rig.get_active()
        if cam:
            self.active_camera = cam
            self.properties_dock.load_camera(cam)
            self.keyframe_dock._refresh_keyframe_table()
            logger.info("CameraWorkspace: Switched to camera '%s'", cam.name)

    def _on_keyframe_changed(self):
        self._evaluate_frame(self._current_frame)

    def _on_comp_rule_changed(self, text):
        self.viewport.set_composition_mode(text)

    def _on_animation_tick(self):
        self._current_frame = (self._current_frame + 1) % self.timeline_data.total_frames
        self._evaluate_frame(self._current_frame)

    def _evaluate_frame(self, frame: int):
        """Evaluate animatable keyframes for the active camera at frame."""
        cam = self.rig.get_active()
        if not cam:
            return

        tracks = self.rig.get_tracks_for_camera(cam.uuid)
        for track in tracks:
            val = track.get_value_at_frame(frame)
            if track.property_name == "x":
                cam.x = val
            elif track.property_name == "y":
                cam.y = val
            elif track.property_name == "zoom":
                cam.zoom = val
            elif track.property_name == "rotation":
                cam.rotation = val
            elif track.property_name == "focus_distance":
                cam.focus_distance = val

        self.switcher_dock.set_frame(frame)
        self.keyframe_dock.set_current_frame(frame)

    def play(self):
        self._is_playing = True
        self.play_timer.start()

    def stop(self):
        self._is_playing = False
        self.play_timer.stop()

    def _generate_camera_plan(self):
        prompt = "Analyze scene and generate cinematic camera shots."
        logger.info("Generating Camera Plan: %s", prompt)
        registry.get(ZanimeAIAPI).generate_camera_plan(prompt, {})

    def autosave(self):
        logger.info("CameraWorkspace: Autosaving camera tracks...")

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

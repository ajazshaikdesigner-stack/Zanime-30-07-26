"""
Data models for Camera Director Studio — Phase 4 Extended.
Adds keyframe animation, movement presets, and multi-camera rigs.
"""

import math
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


@dataclass
class Camera:
    name: str = "Main Camera"
    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0
    rotation: float = 0.0
    focus_distance: float = 10.0
    depth_of_field: float = 5.6  # f-stop
    lens_type: str = "50mm"
    aspect_ratio: str = "16:9"
    is_active: bool = False
    color: str = "#4a9aff"   # Color used in switcher UI
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class CameraClip:
    name: str = "New Shot"
    shot_type: str = "Medium Shot"
    movement_type: str = "Static"
    composition_rule: str = "Rule of Thirds"
    start_frame: int = 0
    duration: int = 24
    transition_in: str = "Cut"
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class CameraTrack:
    clips: list[CameraClip] = field(default_factory=list)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class CameraTimeline:
    scene_uuid: str = ""
    fps: int = 24
    total_frames: int = 240
    tracks: list[CameraTrack] = field(default_factory=list)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


# ---------------------------------------------------------------------------
# Phase 4: Keyframe Animation
# ---------------------------------------------------------------------------

class EasingType(Enum):
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BEZIER = "bezier"


@dataclass
class CameraKeyframe:
    """A single keyframe for one animatable camera property."""
    frame: int = 0
    value: float = 0.0
    easing: str = EasingType.EASE_IN_OUT.value
    handle_left: float = 0.0    # Bezier tangent
    handle_right: float = 0.0


@dataclass
class CameraAnimationTrack:
    """
    Holds keyframes for one camera property (e.g., 'x', 'zoom', 'rotation').
    Supports linear, ease, and bezier interpolation.
    """
    property_name: str = "x"     # x, y, zoom, rotation, focus_distance
    camera_uuid: str = ""
    keyframes: list[CameraKeyframe] = field(default_factory=list)

    def get_value_at_frame(self, frame: int) -> float:
        """Interpolate the property value at a given frame."""
        kfs = sorted(self.keyframes, key=lambda k: k.frame)
        if not kfs:
            return 0.0
        if frame <= kfs[0].frame:
            return kfs[0].value
        if frame >= kfs[-1].frame:
            return kfs[-1].value

        # Find surrounding keyframes
        for i in range(len(kfs) - 1):
            k0, k1 = kfs[i], kfs[i + 1]
            if k0.frame <= frame <= k1.frame:
                t = (frame - k0.frame) / max(1, k1.frame - k0.frame)
                return self._interpolate(t, k0, k1)
        return 0.0

    @staticmethod
    def _interpolate(t: float, k0: CameraKeyframe, k1: CameraKeyframe) -> float:
        easing = k0.easing
        if easing == EasingType.LINEAR.value:
            pass  # t unchanged
        elif easing == EasingType.EASE_IN.value:
            t = t * t
        elif easing == EasingType.EASE_OUT.value:
            t = t * (2 - t)
        elif easing == EasingType.EASE_IN_OUT.value:
            t = t * t * (3 - 2 * t)  # Smoothstep
        elif easing == EasingType.BEZIER.value:
            # Cubic bezier approximation
            t = 3 * t * t - 2 * t * t * t
        return k0.value + (k1.value - k0.value) * t


# ---------------------------------------------------------------------------
# Phase 4: Movement Presets
# ---------------------------------------------------------------------------

class CameraMovementPreset(Enum):
    STATIC       = "Static"
    PAN_LEFT     = "Pan Left"
    PAN_RIGHT    = "Pan Right"
    TILT_UP      = "Tilt Up"
    TILT_DOWN    = "Tilt Down"
    ZOOM_IN      = "Zoom In"
    ZOOM_OUT     = "Zoom Out"
    DOLLY_IN     = "Dolly In"
    DOLLY_OUT    = "Dolly Out"
    ORBIT        = "Orbit"
    CRANE_UP     = "Crane Up"
    CRANE_DOWN   = "Crane Down"
    PUSH_IN      = "Push In"
    PULL_OUT     = "Pull Out"
    HANDHELD     = "Handheld Shake"


PRESET_KEYFRAMES: dict[str, list[dict]] = {
    "Pan Left":       [{"frame": 0, "prop": "x", "value": 0}, {"frame": 24, "prop": "x", "value": -200}],
    "Pan Right":      [{"frame": 0, "prop": "x", "value": 0}, {"frame": 24, "prop": "x", "value": 200}],
    "Tilt Up":        [{"frame": 0, "prop": "y", "value": 0}, {"frame": 24, "prop": "y", "value": -150}],
    "Tilt Down":      [{"frame": 0, "prop": "y", "value": 0}, {"frame": 24, "prop": "y", "value": 150}],
    "Zoom In":        [{"frame": 0, "prop": "zoom", "value": 1.0}, {"frame": 24, "prop": "zoom", "value": 2.5}],
    "Zoom Out":       [{"frame": 0, "prop": "zoom", "value": 2.5}, {"frame": 24, "prop": "zoom", "value": 1.0}],
    "Dolly In":       [{"frame": 0, "prop": "focus_distance", "value": 20.0}, {"frame": 24, "prop": "focus_distance", "value": 5.0}],
    "Crane Up":       [{"frame": 0, "prop": "y", "value": 100}, {"frame": 24, "prop": "y", "value": -200}],
    "Push In":        [{"frame": 0, "prop": "zoom", "value": 1.0}, {"frame": 48, "prop": "zoom", "value": 1.8}],
    "Orbit":          [{"frame": 0, "prop": "rotation", "value": 0}, {"frame": 48, "prop": "rotation", "value": 360}],
    "Handheld Shake": [{"frame": 0, "prop": "x", "value": 0}, {"frame": 3, "prop": "x", "value": 4},
                       {"frame": 6, "prop": "x", "value": -3}, {"frame": 9, "prop": "x", "value": 2}],
}


# ---------------------------------------------------------------------------
# Phase 4: Multi-Camera Rig (project-level camera roster)
# ---------------------------------------------------------------------------

@dataclass
class CameraRig:
    """
    Holds all cameras for a project. One camera is marked active at a time.
    The Camera Switcher UI operates on this model.
    """
    cameras: list[Camera] = field(default_factory=list)
    active_camera_uuid: str = ""
    animation_tracks: list[CameraAnimationTrack] = field(default_factory=list)
    switch_events: list[dict] = field(default_factory=list)  # [{frame, camera_uuid}]

    def add_camera(self, name: str = "Camera") -> Camera:
        cam = Camera(name=name)
        self.cameras.append(cam)
        if not self.active_camera_uuid:
            self.active_camera_uuid = cam.uuid
            cam.is_active = True
        return cam

    def switch_to(self, camera_uuid: str) -> None:
        for cam in self.cameras:
            cam.is_active = (cam.uuid == camera_uuid)
        self.active_camera_uuid = camera_uuid

    def get_active(self) -> Camera | None:
        for cam in self.cameras:
            if cam.uuid == self.active_camera_uuid:
                return cam
        return self.cameras[0] if self.cameras else None

    def get_tracks_for_camera(self, camera_uuid: str) -> list[CameraAnimationTrack]:
        return [t for t in self.animation_tracks if t.camera_uuid == camera_uuid]


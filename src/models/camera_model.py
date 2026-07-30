"""
Data models for Camera Director Studio.
"""

import uuid
from dataclasses import dataclass, field


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

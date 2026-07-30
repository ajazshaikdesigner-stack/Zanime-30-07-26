"""
Data models for Animation Director Studio.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Keyframe:
    frame: int = 0
    value: Any = 0.0
    interpolation: str = "Linear"  # Linear, Bezier, Hold
    property_name: str = "x"


@dataclass
class AnimationClip:
    name: str = "New Clip"
    start_frame: int = 0
    duration: int = 24  # in frames
    target_object_uuid: str = ""
    keyframes: list[Keyframe] = field(default_factory=list)
    looping: bool = False
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class AnimationTrack:
    target_object_uuid: str = ""
    clips: list[AnimationClip] = field(default_factory=list)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class AnimationTimeline:
    scene_uuid: str = ""
    fps: int = 24
    total_frames: int = 240  # 10 seconds default
    tracks: list[AnimationTrack] = field(default_factory=list)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

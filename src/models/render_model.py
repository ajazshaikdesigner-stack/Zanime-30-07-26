"""
Data models for Production Renderer.
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum


class RenderStatus(Enum):
    QUEUED = 1
    RENDERING = 2
    PAUSED = 3
    COMPLETED = 4
    FAILED = 5


@dataclass
class RenderSettings:
    resolution: str = "1080p"  # 480p, 720p, 1080p, 1440p
    fps: int = 24  # 24, 30, 60
    output_format: str = (
        "MP4 (H.264)"  # MP4 (H.264), MP4 (H.265), MOV, AVI, PNG Sequence
    )
    quality: str = (
        "High Quality"  # Draft, Preview, Standard, High Quality, Ultra Quality
    )
    watermark: bool = False
    output_path: str = "./render_output.mp4"


@dataclass
class RenderJob:
    scene_uuid: str = ""
    name: str = "Untitled Render"
    settings: RenderSettings = field(default_factory=RenderSettings)
    status: RenderStatus = RenderStatus.QUEUED
    progress: int = 0
    priority: int = 1  # 1 = High, 2 = Normal
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

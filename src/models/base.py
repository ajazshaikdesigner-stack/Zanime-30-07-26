"""
Base data models for ZANIME.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProjectModel:
    # Basic info
    name: str = "Untitled"
    description: str = ""
    author: str = ""
    company: str = ""
    copyright: str = ""

    # Metadata
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    # Versions
    project_version: str = "1.0.0"
    app_version: str = "1.0.0"
    engine_version: str = "1.0.0"
    format_version: str = "1.0.0"

    # Configurations
    language: str = "English"
    resolution: tuple = (1920, 1080)
    aspect_ratio: str = "16:9"
    fps: int = 24
    art_style: str = "Anime"
    default_output_folder: str = ""
    autosave_interval: int = 5  # minutes
    thumbnail_path: str = ""

    # List states
    pinned: bool = False
    favorite: bool = False

    layers: list[Any] = field(default_factory=list)


@dataclass
class LayerModel:
    id: str
    name: str
    visible: bool = True
    locked: bool = False
    opacity: float = 1.0
    blend_mode: str = "normal"

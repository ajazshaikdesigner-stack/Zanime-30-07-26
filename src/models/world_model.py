"""
Data models for World Builder Studio (Environments & Props).
"""

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class EnvironmentDNA:
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "New Environment"
    category: str = "Forest"
    style: str = "Anime"
    resolution: str = "1920x1080"
    aspect_ratio: str = "16:9"
    lighting: str = "Daylight"
    weather: str = "Sunny"
    season: str = "Summer"
    time_of_day: str = "Afternoon"
    mood: str = "Peaceful"
    camera_depth: str = "Wide"
    fog: str = "None"
    color_palette: str = "Vibrant"
    tags: list[str] = field(default_factory=list)
    image_path: str = ""
    is_favorite: bool = False
    created_at: float = field(default_factory=time.time)


@dataclass
class PropModel:
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "New Prop"
    category: str = "Furniture"
    size: str = "Medium"
    material: str = "Wood"
    style: str = "Anime"
    tags: list[str] = field(default_factory=list)
    color: str = "Brown"
    animation_support: bool = False
    collision: bool = True
    image_path: str = ""
    is_favorite: bool = False
    created_at: float = field(default_factory=time.time)

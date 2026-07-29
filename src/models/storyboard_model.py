"""
Data models for Storyboard & Scene Planning Studio.
"""
import uuid
import time
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ShotModel:
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    number: int = 1
    shot_type: str = "Wide" # Wide, Medium, Close Up, etc.
    duration: float = 3.0 # seconds
    characters: List[str] = field(default_factory=list) # List of Character UUIDs
    props: List[str] = field(default_factory=list) # List of Prop UUIDs
    camera_movement: str = "Static" # Pan, Tilt, Zoom, etc.
    thumbnail_path: str = ""
    notes: str = ""

@dataclass
class SceneModel:
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    number: int = 1
    name: str = "New Scene"
    description: str = ""
    environment_uuid: str = ""
    lighting: str = "Daylight"
    weather: str = "Sunny"
    season: str = "Summer"
    time_of_day: str = "Afternoon"
    mood: str = "Neutral"
    transition: str = "Cut"
    shots: List[ShotModel] = field(default_factory=list)

@dataclass
class StoryboardModel:
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Storyboard"
    scenes: List[SceneModel] = field(default_factory=list)
    total_duration: float = 0.0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def calculate_duration(self):
        dur = 0.0
        for scene in self.scenes:
            for shot in scene.shots:
                dur += shot.duration
        self.total_duration = dur

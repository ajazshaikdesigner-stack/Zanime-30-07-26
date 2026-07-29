"""
Data models for Voice & Dialogue Studio.
"""
import uuid
from dataclasses import dataclass, field
from typing import List

@dataclass
class VoiceProfile:
    name: str = "Default Voice"
    language: str = "English"
    accent: str = "Neutral"
    gender: str = "Female"
    age_group: str = "Adult"
    pitch: float = 1.0
    speed: float = 1.0
    provider: str = "AI_TTS"
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class VisemeData:
    frame: int = 0
    mouth_shape: str = "Closed" # E.g., 'A', 'E', 'I', 'O', 'U', 'M'

@dataclass
class DialogueClip:
    character_uuid: str = ""
    voice_profile_uuid: str = ""
    text: str = ""
    emotion: str = "Neutral"
    volume: float = 1.0
    start_frame: int = 0
    duration: int = 48 # Mock length
    audio_path: str = ""
    visemes: List[VisemeData] = field(default_factory=list)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class VoiceTrack:
    character_uuid: str = ""
    clips: List[DialogueClip] = field(default_factory=list)
    mute: bool = False
    solo: bool = False
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class VoiceTimeline:
    scene_uuid: str = ""
    fps: int = 24
    total_frames: int = 240
    tracks: List[VoiceTrack] = field(default_factory=list)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

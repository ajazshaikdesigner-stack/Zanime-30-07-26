import time
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class StoryVersion:
    version_id: str
    timestamp: float
    ai_model: str
    prompt: str
    result: str

@dataclass
class StoryModel:
    title: str = "Untitled Story"
    tagline: str = ""
    summary: str = ""
    content: str = ""
    
    characters: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    props: List[str] = field(default_factory=list)
    
    duration_est: str = "00:00:00"
    rating: str = "G"
    keywords: List[str] = field(default_factory=list)
    mood: str = ""
    moral: str = ""
    
    is_locked: bool = False
    
    history: List[StoryVersion] = field(default_factory=list)

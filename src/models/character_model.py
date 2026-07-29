"""
Data models for the Character Studio module.
"""
import uuid
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class CharacterDNA:
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "New Character"
    age: int = 18
    gender: str = "Unknown"
    height: float = 170.0 # cm
    weight: float = 60.0 # kg
    body_type: str = "Average"
    face_shape: str = "Oval"
    eye_shape: str = "Almond"
    eye_color: str = "Brown"
    hair_style: str = "Short"
    hair_color: str = "Black"
    skin_tone: str = "Fair"
    ethnicity: str = "Mixed"
    personality: str = "Neutral"
    occupation: str = "Student"
    speaking_style: str = "Normal"
    walking_style: str = "Normal"
    running_style: str = "Normal"
    favorite_color: str = "Blue"
    biography: str = ""

@dataclass
class Outfit:
    name: str
    clothes: str = ""
    shoes: str = ""
    accessories: List[str] = field(default_factory=list)
    hair_style: Optional[str] = None
    props: List[str] = field(default_factory=list)

@dataclass
class CharacterSheet:
    front: str = ""
    front_left: str = ""
    left: str = ""
    back_left: str = ""
    back: str = ""
    back_right: str = ""
    right: str = ""
    front_right: str = ""

@dataclass
class CharacterModel:
    dna: CharacterDNA = field(default_factory=CharacterDNA)
    outfits: Dict[str, Outfit] = field(default_factory=dict)
    expressions: Dict[str, str] = field(default_factory=dict) # Name -> image_path
    poses: Dict[str, str] = field(default_factory=dict)       # Name -> image_path
    model_sheet: CharacterSheet = field(default_factory=CharacterSheet)
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    is_favorite: bool = False
    
    def get_thumbnail(self) -> str:
        """Returns the front image path or an empty string."""
        return self.model_sheet.front

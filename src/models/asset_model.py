"""
Asset Data Models for Content Ecosystem
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum


class AssetType(Enum):
    CHARACTER = "Character"
    BACKGROUND = "Background"
    PROP = "Prop"
    EXPRESSION = "Expression"
    POSE = "Pose"
    ANIMATION = "Animation"
    VOICE = "Voice"
    MUSIC = "Music"
    SFX = "SFX"
    TEMPLATE = "Template"


@dataclass
class AssetMetadata:
    name: str
    asset_type: AssetType
    category: str
    author: str = "Zanime Studios"
    version: str = "1.0"
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    is_favorite: bool = False
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class AssetCollection:
    name: str
    asset_uuids: list[str] = field(default_factory=list)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class MarketplacePack:
    name: str
    description: str
    price: float = 0.0
    rating: float = 5.0
    assets_included: list[str] = field(default_factory=list)
    pack_id: str = field(default_factory=lambda: str(uuid.uuid4()))

"""
Data models for the Movie Composer Studio.
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum


class LayerType(Enum):
    FAR_BACKGROUND = 0
    BACKGROUND = 1
    MIDDLE_GROUND = 2
    CHARACTERS = 3
    FOREGROUND = 4
    EFFECTS = 5
    CAMERA = 6
    LIGHTING = 7
    OVERLAY = 8
    UI = 9


@dataclass
class ComposerObject:
    name: str = "New Object"
    object_type: str = "Prop"  # Character, Prop, Environment
    x: float = 0.0
    y: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    rotation: float = 0.0
    layer: LayerType = LayerType.CHARACTERS
    visible: bool = True
    locked: bool = False
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ComposerShot:
    name: str = "New Shot"
    objects: list[ComposerObject] = field(default_factory=list)
    background_uuid: str | None = None
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ComposerScene:
    name: str = "New Scene"
    shots: list[ComposerShot] = field(default_factory=list)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

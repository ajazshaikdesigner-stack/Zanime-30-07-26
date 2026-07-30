"""
AI History data models.
Every generation result is stored as an AIHistoryEntry and persisted per-project.
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum


class AITaskType(Enum):
    TEXT       = "text"
    IMAGE      = "image"
    AUDIO      = "audio"
    VIDEO      = "video"
    MUSIC      = "music"
    UPSCALE    = "upscale"
    TRANSCRIBE = "transcribe"
    LIPSYNC    = "lipsync"


@dataclass
class AIHistoryEntry:
    entry_id:        str        = field(default_factory=lambda: str(uuid.uuid4()))
    task_type:       str        = AITaskType.TEXT.value
    prompt:          str        = ""
    negative_prompt: str        = ""
    seed:            int        = -1
    model_name:      str        = ""
    provider:        str        = ""
    settings:        dict       = field(default_factory=dict)
    output_path:     str        = ""
    thumbnail_path:  str        = ""
    timestamp:       float      = field(default_factory=time.time)
    project_id:      str        = ""
    workspace:       str        = ""   # which workspace triggered the generation
    duration_ms:     int        = 0    # how long the job took
    is_favorite:     bool       = False
    tags:            list[str]  = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "entry_id":        self.entry_id,
            "task_type":       self.task_type,
            "prompt":          self.prompt,
            "negative_prompt": self.negative_prompt,
            "seed":            self.seed,
            "model_name":      self.model_name,
            "provider":        self.provider,
            "settings":        self.settings,
            "output_path":     self.output_path,
            "thumbnail_path":  self.thumbnail_path,
            "timestamp":       self.timestamp,
            "project_id":      self.project_id,
            "workspace":       self.workspace,
            "duration_ms":     self.duration_ms,
            "is_favorite":     self.is_favorite,
            "tags":            self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AIHistoryEntry":
        return cls(
            entry_id        = data.get("entry_id", str(uuid.uuid4())),
            task_type       = data.get("task_type", AITaskType.TEXT.value),
            prompt          = data.get("prompt", ""),
            negative_prompt = data.get("negative_prompt", ""),
            seed            = data.get("seed", -1),
            model_name      = data.get("model_name", ""),
            provider        = data.get("provider", ""),
            settings        = data.get("settings", {}),
            output_path     = data.get("output_path", ""),
            thumbnail_path  = data.get("thumbnail_path", ""),
            timestamp       = data.get("timestamp", time.time()),
            project_id      = data.get("project_id", ""),
            workspace       = data.get("workspace", ""),
            duration_ms     = data.get("duration_ms", 0),
            is_favorite     = data.get("is_favorite", False),
            tags            = data.get("tags", []),
        )

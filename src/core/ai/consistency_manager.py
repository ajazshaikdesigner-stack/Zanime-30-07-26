"""
Character Consistency Manager.

Tracks visual identity anchors for AI-generated characters so that
subsequent image generations maintain a consistent look:
  - Reference image path (first approved generation)
  - Seed lock (reproduce same latent starting point)
  - ControlNet pose reference
  - Character DNA descriptor (assembled from CharacterModel.dna)

Persists per-project in <project_temp_dir>/character_consistency.json.
"""

import json
import logging
import os
import threading
import time
from dataclasses import asdict, dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

_CONSISTENCY_FILENAME = "character_consistency.json"


@dataclass
class CharacterAnchor:
    """Visual DNA anchor for a single character."""
    character_uuid:    str
    character_name:    str
    reference_image:   str        = ""    # path to approved reference PNG
    locked_seed:       int        = -1    # -1 = unlocked
    dna_prompt:        str        = ""    # assembled positive prompt fragment
    style_suffix:      str        = ""    # e.g. "anime style, ZANIME production art"
    controlnet_pose:   str        = ""    # path to pose reference PNG
    controlnet_weight: float      = 0.7
    last_updated:      float      = field(default_factory=time.time)
    is_locked:         bool       = False  # when locked, all fields are frozen


class ConsistencyManager:
    """
    Builds and applies character consistency anchors into generation prompts.

    Usage:
        cm = registry.get(ConsistencyManager)
        cm.set_project_dir(...)
        cm.set_anchor(character_uuid, ...)          # store reference
        prompt = cm.apply(character_uuid, base_prompt)  # inject consistency
        params  = cm.inject_params(character_uuid, base_params)  # inject seed/CN
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._project_dir: str | None = None
        self._anchors: dict[str, CharacterAnchor] = {}

    # ------------------------------------------------------------------
    # Project lifecycle
    # ------------------------------------------------------------------

    def set_project_dir(self, project_dir: str) -> None:
        with self._lock:
            self._project_dir = project_dir
            self._anchors = {}
            self._load()

    # ------------------------------------------------------------------
    # Anchor management
    # ------------------------------------------------------------------

    def set_anchor(
        self,
        character_uuid: str,
        character_name: str,
        reference_image: str = "",
        locked_seed: int = -1,
        dna_prompt: str = "",
        style_suffix: str = "anime style, high quality, ZANIME production art",
        controlnet_pose: str = "",
        controlnet_weight: float = 0.7,
    ) -> CharacterAnchor:
        anchor = CharacterAnchor(
            character_uuid    = character_uuid,
            character_name    = character_name,
            reference_image   = reference_image,
            locked_seed       = locked_seed,
            dna_prompt        = dna_prompt,
            style_suffix      = style_suffix,
            controlnet_pose   = controlnet_pose,
            controlnet_weight = controlnet_weight,
        )
        with self._lock:
            self._anchors[character_uuid] = anchor
            self._save()
        logger.info(
            "ConsistencyManager: Anchor set for '%s' (uuid=%s, seed=%d).",
            character_name, character_uuid, locked_seed,
        )
        return anchor

    def get_anchor(self, character_uuid: str) -> CharacterAnchor | None:
        with self._lock:
            return self._anchors.get(character_uuid)

    def lock_anchor(self, character_uuid: str) -> None:
        with self._lock:
            if character_uuid in self._anchors:
                self._anchors[character_uuid].is_locked = True
                self._save()

    def unlock_anchor(self, character_uuid: str) -> None:
        with self._lock:
            if character_uuid in self._anchors:
                self._anchors[character_uuid].is_locked = False
                self._save()

    def delete_anchor(self, character_uuid: str) -> bool:
        with self._lock:
            if character_uuid in self._anchors:
                del self._anchors[character_uuid]
                self._save()
                return True
        return False

    def list_anchors(self) -> list[CharacterAnchor]:
        with self._lock:
            return list(self._anchors.values())

    # ------------------------------------------------------------------
    # Prompt injection
    # ------------------------------------------------------------------

    def apply(self, character_uuid: str, base_prompt: str) -> str:
        """
        Inject character consistency fragments into a generation prompt.
        Returns the modified prompt string.
        """
        anchor = self.get_anchor(character_uuid)
        if not anchor:
            return base_prompt

        parts = [base_prompt.strip()]
        if anchor.dna_prompt:
            parts.append(anchor.dna_prompt)
        if anchor.style_suffix:
            parts.append(anchor.style_suffix)

        return ", ".join(p for p in parts if p)

    def inject_params(self, character_uuid: str, base_params: dict[str, Any]) -> dict[str, Any]:
        """
        Inject consistency parameters (seed, ControlNet) into the params dict
        that will be passed to the image provider.
        """
        anchor = self.get_anchor(character_uuid)
        if not anchor:
            return base_params

        params = dict(base_params)

        if anchor.locked_seed != -1:
            params["seed"] = anchor.locked_seed

        if anchor.controlnet_pose and os.path.isfile(anchor.controlnet_pose):
            params["controlnet_image"] = anchor.controlnet_pose
            params["controlnet_weight"] = anchor.controlnet_weight

        return params

    @staticmethod
    def build_dna_prompt(dna) -> str:
        """
        Convert a CharacterDNA dataclass into a concise positive prompt fragment.
        e.g. "young adult female, oval face, almond eyes, brown eyes, short black hair, fair skin"
        """
        parts = [
            f"{dna.age}-year-old {dna.gender.lower()}",
            f"{dna.face_shape.lower()} face shape",
            f"{dna.eye_shape.lower()} {dna.eye_color.lower()} eyes",
            f"{dna.hair_style.lower()} {dna.hair_color.lower()} hair",
            f"{dna.skin_tone.lower()} skin",
        ]
        return ", ".join(parts)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _save(self) -> None:
        path = self._consistency_path()
        if not path:
            return
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            data = {uid: asdict(anchor) for uid, anchor in self._anchors.items()}
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, path)
        except Exception:
            logger.exception("ConsistencyManager: Failed to save %s.", path)

    def _load(self) -> None:
        path = self._consistency_path()
        if not path or not os.path.isfile(path):
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self._anchors = {
                uid: CharacterAnchor(**anchor_data)
                for uid, anchor_data in data.items()
            }
            logger.info(
                "ConsistencyManager: Loaded %d anchors.", len(self._anchors)
            )
        except Exception:
            logger.exception("ConsistencyManager: Failed to load %s.", path)
            self._anchors = {}

    def _consistency_path(self) -> str | None:
        if not self._project_dir:
            return None
        return os.path.join(self._project_dir, _CONSISTENCY_FILENAME)

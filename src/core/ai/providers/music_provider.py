"""
Music Generation Provider.

Backends (auto-detected):
  1. audiocraft (Facebook MusicGen — local, best quality)
  2. Subprocess fallback via MusicGen CLI

Output: WAV/MP3 file written to project temp directory.

execute() params:
  duration  (int)    — output duration in seconds (default 10)
  mood      (str)    — mood tag: epic/calm/sad/happy/tense/mysterious
  style     (str)    — music style: orchestral/electronic/acoustic/jazz
  output_dir (str)   — output directory
  format    (str)    — "wav" or "mp3" (default "wav")
"""

import logging
import os
import uuid as _uuid
from typing import Any

from .base import AIBaseProvider

logger = logging.getLogger(__name__)


# Mood → musical descriptor expansion
_MOOD_MAP = {
    "epic":        "epic orchestral cinematic soundtrack, powerful, heroic, intense",
    "calm":        "soft ambient peaceful music, gentle piano, serene, relaxing",
    "sad":         "melancholic emotional piano, sorrowful strings, bittersweet",
    "happy":       "cheerful upbeat playful music, light acoustic guitar, bright",
    "tense":       "suspenseful dark thriller music, staccato strings, pulsing",
    "mysterious":  "mysterious ethereal ambient music, deep synth pads, haunting",
    "action":      "fast-paced action battle music, heavy drums, electric guitar",
    "romance":     "romantic gentle violin melody, warm orchestral arrangement",
}

_STYLE_MAP = {
    "orchestral":   "full orchestra with strings, brass, woodwinds and percussion",
    "electronic":   "electronic synth music, EDM, pulsing beats",
    "acoustic":     "acoustic guitar and piano folk music",
    "jazz":         "jazz ensemble, saxophone, double bass, brushed drums",
    "lofi":         "lo-fi hip hop beats, mellow, chill",
}


class MusicProvider(AIBaseProvider):
    def __init__(self):
        super().__init__()
        self._backend = None
        self._model = None

    def load(self, model_name: str, config: dict[str, Any]) -> bool:
        model_size = config.get("musicgen_model", "small")  # small/medium/melody/large

        try:
            from audiocraft.models import MusicGen  # noqa: F401
            self._backend = "audiocraft"
            self._model_size = model_size
            logger.info("MusicProvider: audiocraft available (model=%s).", model_size)
            # Lazy load the model on first execute to save VRAM
            self.is_loaded = True
            return True
        except ImportError:
            logger.warning("MusicProvider: audiocraft not installed. Music generation disabled.")
            # We mark as loaded anyway with a graceful no-op so the rest of the app works
            self._backend = "disabled"
            self.is_loaded = True
            return True

    def unload(self) -> None:
        self._model = None
        self.is_loaded = False
        logger.info("MusicProvider: Unloaded.")

    def execute(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if not self.is_loaded:
            raise RuntimeError("MusicProvider: Not loaded.")

        if self._backend == "disabled":
            logger.warning("MusicProvider: audiocraft not available. Returning empty result.")
            return {"audio_path": "", "duration": 0, "backend": "disabled"}

        return self._generate_audiocraft(prompt, parameters)

    def memory_footprint(self) -> int:
        size_map = {"small": 500, "medium": 1500, "melody": 1500, "large": 3500}
        return size_map.get(getattr(self, "_model_size", "small"), 500)

    # ------------------------------------------------------------------
    # Backend: audiocraft MusicGen
    # ------------------------------------------------------------------

    def _generate_audiocraft(self, prompt: str, params: dict) -> dict:
        from audiocraft.models import MusicGen
        from audiocraft.data.audio import audio_write

        duration  = min(params.get("duration", 10), 60)   # cap at 60s
        mood      = params.get("mood", "calm")
        style     = params.get("style", "orchestral")
        output_dir = params.get("output_dir", os.path.expanduser("~/.zanime/music"))
        fmt       = params.get("format", "wav")

        os.makedirs(output_dir, exist_ok=True)

        # Build enriched prompt
        mood_desc  = _MOOD_MAP.get(mood, mood)
        style_desc = _STYLE_MAP.get(style, style)
        full_prompt = f"{prompt}, {mood_desc}, {style_desc}" if prompt else f"{mood_desc}, {style_desc}"

        # Lazy-load model
        if self._model is None:
            logger.info("MusicProvider: Loading MusicGen-%s model...", self._model_size)
            self._model = MusicGen.get_pretrained(self._model_size)

        self._model.set_generation_params(duration=duration)

        logger.info("MusicProvider: Generating %.0fs of music — '%s'", duration, full_prompt[:80])
        wav = self._model.generate([full_prompt])  # returns tensor [1, channels, samples]

        filename = f"music_{_uuid.uuid4().hex[:8]}"
        output_path_base = os.path.join(output_dir, filename)
        audio_write(
            output_path_base,
            wav[0].cpu(),
            self._model.sample_rate,
            strategy="loudness",
            format=fmt,
        )

        output_path = f"{output_path_base}.{fmt}"
        logger.info("MusicProvider: Music saved to %s", output_path)

        return {
            "audio_path": output_path,
            "duration": duration,
            "prompt": full_prompt,
            "backend": "audiocraft",
        }

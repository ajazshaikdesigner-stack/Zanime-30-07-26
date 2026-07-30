"""
Whisper Speech-to-Text Provider.

Supports two backends (auto-detected at load time):
  1. faster-whisper (preferred — 4x faster, lower VRAM)
  2. openai-whisper  (fallback)
  3. Subprocess CLI fallback if neither library is installed

Returns: transcript text + word-level timestamps for lip-sync data.
"""

import logging
import os
import subprocess
import json
from typing import Any

from .base import AIBaseProvider

logger = logging.getLogger(__name__)

_SUPPORTED_SIZES = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]
_DEFAULT_MODEL = "base"


class WhisperProvider(AIBaseProvider):
    """
    Whisper STT provider. Transcribes audio files and returns word-level
    timestamps usable for lip-sync generation.
    """

    def __init__(self):
        super().__init__()
        self._model_name = _DEFAULT_MODEL
        self._backend = None       # "faster_whisper" | "openai_whisper" | "cli"
        self._model_obj = None     # loaded model object

    # ------------------------------------------------------------------
    # AIBaseProvider interface
    # ------------------------------------------------------------------

    def load(self, model_name: str, config: dict[str, Any]) -> bool:
        self._model_name = model_name or _DEFAULT_MODEL

        # Try faster-whisper first (best performance on AMD / CPU)
        try:
            from faster_whisper import WhisperModel  # noqa: F401
            self._backend = "faster_whisper"
            logger.info("WhisperProvider: Using faster-whisper backend.")
        except ImportError:
            pass

        # Fall back to openai-whisper
        if not self._backend:
            try:
                import whisper  # noqa: F401
                self._backend = "openai_whisper"
                logger.info("WhisperProvider: Using openai-whisper backend.")
            except ImportError:
                pass

        # Last resort: CLI subprocess (whisper must be on PATH)
        if not self._backend:
            if self._which("whisper"):
                self._backend = "cli"
                logger.info("WhisperProvider: Using CLI subprocess backend.")
            else:
                logger.error(
                    "WhisperProvider: No Whisper backend found. "
                    "Install faster-whisper or openai-whisper."
                )
                self.is_loaded = False
                return False

        # Eagerly load the model object for faster-whisper / openai-whisper
        device = config.get("whisper_device", "cpu")
        compute = config.get("whisper_compute", "int8")

        try:
            if self._backend == "faster_whisper":
                from faster_whisper import WhisperModel
                self._model_obj = WhisperModel(
                    self._model_name, device=device, compute_type=compute
                )
                logger.info(
                    "WhisperProvider: faster-whisper model '%s' loaded on %s.",
                    self._model_name, device,
                )
            elif self._backend == "openai_whisper":
                import whisper
                self._model_obj = whisper.load_model(
                    self._model_name,
                    device=device if device != "cpu" else None,
                )
                logger.info(
                    "WhisperProvider: openai-whisper model '%s' loaded.", self._model_name
                )
            # CLI backend loads lazily per invocation
        except Exception:
            logger.exception("WhisperProvider: Failed to load model '%s'.", self._model_name)
            self.is_loaded = False
            return False

        self.is_loaded = True
        return True

    def unload(self) -> None:
        self._model_obj = None
        self.is_loaded = False
        logger.info("WhisperProvider: Model unloaded.")

    def execute(self, audio_path: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """
        Transcribe an audio file.

        Returns:
            {
                "text": str,                        # full transcript
                "segments": [...],                  # list of segment dicts
                "words": [{"word", "start", "end"}] # word-level timestamps
            }
        """
        if not self.is_loaded:
            raise RuntimeError("WhisperProvider: Not loaded.")

        if not os.path.isfile(audio_path):
            raise FileNotFoundError(f"WhisperProvider: Audio file not found: {audio_path}")

        language = parameters.get("language", None)  # None = auto-detect

        if self._backend == "faster_whisper":
            return self._transcribe_faster_whisper(audio_path, language)
        elif self._backend == "openai_whisper":
            return self._transcribe_openai_whisper(audio_path, language)
        else:
            return self._transcribe_cli(audio_path, language)

    def memory_footprint(self) -> int:
        footprint = {
            "tiny": 150, "base": 290, "small": 500,
            "medium": 1500, "large-v2": 3000, "large-v3": 3000,
        }
        return footprint.get(self._model_name, 1000)

    # ------------------------------------------------------------------
    # Backend implementations
    # ------------------------------------------------------------------

    def _transcribe_faster_whisper(self, audio_path: str, language: str | None) -> dict:
        segments_raw, info = self._model_obj.transcribe(
            audio_path,
            language=language,
            word_timestamps=True,
            beam_size=5,
        )
        segments = []
        words = []
        full_text_parts = []

        for seg in segments_raw:
            seg_dict = {
                "start": seg.start,
                "end": seg.end,
                "text": seg.text.strip(),
            }
            segments.append(seg_dict)
            full_text_parts.append(seg.text.strip())

            if seg.words:
                for w in seg.words:
                    words.append({"word": w.word.strip(), "start": w.start, "end": w.end})

        return {
            "text": " ".join(full_text_parts),
            "segments": segments,
            "words": words,
            "language": info.language,
        }

    def _transcribe_openai_whisper(self, audio_path: str, language: str | None) -> dict:
        import whisper
        kwargs = {"word_timestamps": True}
        if language:
            kwargs["language"] = language

        result = self._model_obj.transcribe(audio_path, **kwargs)
        words = []
        for seg in result.get("segments", []):
            for w in seg.get("words", []):
                words.append({"word": w["word"].strip(), "start": w["start"], "end": w["end"]})

        return {
            "text": result.get("text", ""),
            "segments": result.get("segments", []),
            "words": words,
            "language": result.get("language", ""),
        }

    def _transcribe_cli(self, audio_path: str, language: str | None) -> dict:
        """Use the whisper CLI and parse the JSON output."""
        cmd = [
            "whisper", audio_path,
            "--model", self._model_name,
            "--output_format", "json",
            "--output_dir", os.path.dirname(audio_path),
        ]
        if language:
            cmd += ["--language", language]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"Whisper CLI failed: {result.stderr}")

        # Whisper CLI outputs <audio_path_basename>.json
        base = os.path.splitext(os.path.basename(audio_path))[0]
        json_out = os.path.join(os.path.dirname(audio_path), f"{base}.json")
        if os.path.isfile(json_out):
            with open(json_out) as f:
                data = json.load(f)
            return {
                "text": data.get("text", ""),
                "segments": data.get("segments", []),
                "words": [],  # CLI JSON format lacks word timestamps
                "language": data.get("language", ""),
            }
        return {"text": result.stdout.strip(), "segments": [], "words": [], "language": ""}

    @staticmethod
    def _which(cmd: str) -> bool:
        import shutil
        return shutil.which(cmd) is not None

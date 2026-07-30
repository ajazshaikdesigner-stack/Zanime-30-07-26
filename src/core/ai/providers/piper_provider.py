"""
TTS Provider — XTTS-v2 primary backend, Piper lightweight fallback.

XTTS-v2 (by Coqui): best quality, voice cloning, emotion control.
Piper: ultra-fast, offline, low VRAM.

Auto-selects based on available libraries and config.
Output: WAV file written to project temp directory.
"""

import logging
import os
import subprocess
import shutil
from typing import Any

from .base import AIBaseProvider

logger = logging.getLogger(__name__)

_DEFAULT_XTTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
_DEFAULT_PIPER_VOICE = "en_US-ryan-medium"


class TTSProvider(AIBaseProvider):
    """
    Text-to-Speech provider.

    execute() params:
      voice      (str)   — voice name / model variant
      emotion    (str)   — emotion hint: neutral/happy/sad/angry/excited
      speed      (float) — speaking speed multiplier (default 1.0)
      language   (str)   — language code (default "en")
      speaker_wav (str)  — path to reference WAV for XTTS voice cloning
      output_dir (str)   — output directory for WAV files
    """

    def __init__(self):
        super().__init__()
        self._backend = None   # "xtts" | "piper" | "cli"
        self._tts_obj = None   # XTTS TTS() object
        self._model_name = _DEFAULT_XTTS_MODEL

    # ------------------------------------------------------------------
    # AIBaseProvider interface
    # ------------------------------------------------------------------

    def load(self, model_name: str, config: dict[str, Any]) -> bool:
        prefer = config.get("tts_backend", "xtts")

        if prefer == "xtts":
            if self._try_load_xtts(model_name, config):
                self.is_loaded = True
                return True
            logger.warning("TTSProvider: XTTS unavailable, falling back to Piper.")

        if self._try_load_piper(config):
            self.is_loaded = True
            return True

        logger.error("TTSProvider: No TTS backend available. Install TTS (Coqui) or Piper.")
        self.is_loaded = False
        return False

    def unload(self) -> None:
        self._tts_obj = None
        self._backend = None
        self.is_loaded = False
        logger.info("TTSProvider: Unloaded.")

    def execute(self, text: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if not self.is_loaded:
            raise RuntimeError("TTSProvider: Not loaded.")

        output_dir = parameters.get("output_dir", os.path.expanduser("~/.zanime/voice"))
        os.makedirs(output_dir, exist_ok=True)

        import uuid as _uuid
        output_path = os.path.join(output_dir, f"tts_{_uuid.uuid4().hex[:8]}.wav")

        if self._backend == "xtts":
            return self._synthesize_xtts(text, parameters, output_path)
        elif self._backend == "piper":
            return self._synthesize_piper(text, parameters, output_path)
        else:
            raise RuntimeError("TTSProvider: No backend active.")

    def memory_footprint(self) -> int:
        return 3000 if self._backend == "xtts" else 200

    # ------------------------------------------------------------------
    # Backend: XTTS-v2
    # ------------------------------------------------------------------

    def _try_load_xtts(self, model_name: str, config: dict) -> bool:
        try:
            from TTS.api import TTS  # noqa: F401

            self._model_name = model_name or _DEFAULT_XTTS_MODEL
            gpu = config.get("tts_gpu", False)

            logger.info("TTSProvider: Loading XTTS model '%s' (gpu=%s)...", self._model_name, gpu)
            from TTS.api import TTS
            self._tts_obj = TTS(self._model_name, gpu=gpu)
            self._backend = "xtts"
            logger.info("TTSProvider: XTTS-v2 loaded.")
            return True
        except ImportError:
            logger.debug("TTSProvider: TTS (Coqui) not installed.")
            return False
        except Exception:
            logger.exception("TTSProvider: XTTS load failed.")
            return False

    def _synthesize_xtts(self, text: str, params: dict, output_path: str) -> dict:
        language = params.get("language", "en")
        speaker_wav = params.get("speaker_wav", None)

        # Build emotion-modulated text if requested
        emotion = params.get("emotion", "neutral")
        text = self._apply_emotion_prefix(text, emotion)

        if speaker_wav and os.path.isfile(speaker_wav):
            # Voice cloning mode
            self._tts_obj.tts_to_file(
                text=text,
                file_path=output_path,
                speaker_wav=speaker_wav,
                language=language,
            )
        else:
            # Default speaker
            self._tts_obj.tts_to_file(
                text=text,
                file_path=output_path,
                speaker=self._tts_obj.speakers[0] if self._tts_obj.speakers else None,
                language=language,
            )

        logger.info("TTSProvider (XTTS): Synthesized to %s", output_path)
        return {"audio_path": output_path, "backend": "xtts", "emotion": emotion}

    # ------------------------------------------------------------------
    # Backend: Piper
    # ------------------------------------------------------------------

    def _try_load_piper(self, config: dict) -> bool:
        voice = config.get("piper_voice", _DEFAULT_PIPER_VOICE)
        self._piper_voice = voice

        # piper can be a Python package or a standalone binary
        try:
            import piper  # noqa: F401
            self._backend = "piper_lib"
            logger.info("TTSProvider: Using piper Python library (voice=%s).", voice)
            return True
        except ImportError:
            pass

        if shutil.which("piper"):
            self._backend = "piper"
            logger.info("TTSProvider: Using piper CLI binary.")
            return True

        return False

    def _synthesize_piper(self, text: str, params: dict, output_path: str) -> dict:
        voice = params.get("voice", self._piper_voice)

        if self._backend == "piper_lib":
            try:
                from piper import PiperVoice
                voice_obj = PiperVoice.load(voice)
                with open(output_path, "wb") as wav_file:
                    voice_obj.synthesize(text, wav_file)
                logger.info("TTSProvider (piper lib): Synthesized to %s", output_path)
                return {"audio_path": output_path, "backend": "piper"}
            except Exception:
                logger.exception("TTSProvider: piper lib synthesis failed.")
                raise

        # CLI subprocess
        cmd = ["piper", "--voice", voice, "--output_file", output_path]
        result = subprocess.run(
            cmd, input=text, capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            raise RuntimeError(f"Piper TTS failed: {result.stderr}")

        return {"audio_path": output_path, "backend": "piper_cli"}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_emotion_prefix(text: str, emotion: str) -> str:
        """
        XTTS responds to emotional cues embedded in prompt text.
        This is a lightweight heuristic approach; full emotion control
        requires fine-tuned models.
        """
        prefixes = {
            "happy":   "[laughing] ",
            "sad":     "[sighing] ",
            "angry":   "[angry] ",
            "excited": "[excited] ",
            "whisper": "[whispering] ",
        }
        return prefixes.get(emotion, "") + text

"""
Voice IO Service for exporting metadata.
"""

import json
import logging
import os

from src.models.voice_model import VoiceTimeline

logger = logging.getLogger(__name__)


class VoiceIO:
    @staticmethod
    def export_dialogue_package(timeline: VoiceTimeline, path: str) -> bool:
        """
        Exports a Dialogue Package (JSON) which can be consumed by external tools or the renderer.
        """
        try:
            data = {
                "uuid": timeline.uuid,
                "scene_uuid": timeline.scene_uuid,
                "fps": timeline.fps,
                "total_frames": timeline.total_frames,
                "tracks": [],
            }
            for track in timeline.tracks:
                t_data = {
                    "character_uuid": track.character_uuid,
                    "mute": track.mute,
                    "clips": [],
                }
                for clip in track.clips:
                    c_data = {
                        "text": clip.text,
                        "emotion": clip.emotion,
                        "start_frame": clip.start_frame,
                        "duration": clip.duration,
                        "audio_path": clip.audio_path,
                    }
                    t_data["clips"].append(c_data)
                data["tracks"].append(t_data)

            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:  # noqa: BLE001
            logger.error("Error exporting dialogue package: %s", e)
            return False

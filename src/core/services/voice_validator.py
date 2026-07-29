"""
Voice Validator for checking audio integrity on the timeline.
"""
from typing import List
from src.models.voice_model import VoiceTimeline

class VoiceValidator:
    @staticmethod
    def validate_timeline(timeline: VoiceTimeline) -> List[str]:
        errors = []
        
        for track in timeline.tracks:
            # Overlap check
            clips_sorted = sorted(track.clips, key=lambda c: c.start_frame)
            for i in range(len(clips_sorted) - 1):
                current = clips_sorted[i]
                next_clip = clips_sorted[i+1]
                if current.start_frame + current.duration > next_clip.start_frame:
                    errors.append(f"Overlapping Audio: '{current.text}' overlaps with next clip.")
                    
            for clip in track.clips:
                if not clip.voice_profile_uuid:
                    errors.append(f"Missing Voice: Clip starting at {clip.start_frame} has no assigned voice.")
                if not clip.text and not clip.audio_path:
                    errors.append(f"Missing Dialogue: Clip starting at {clip.start_frame} has no text or audio.")
                    
        return errors

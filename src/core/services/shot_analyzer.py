"""
Shot Analyzer validates camera framing and timings.
"""

from src.models.camera_model import CameraTimeline


class ShotAnalyzer:
    @staticmethod
    def analyze(timeline: CameraTimeline) -> list[str]:
        errors = []
        fps = timeline.fps
        rapid_cut_threshold = fps * 0.5  # half a second

        for track in timeline.tracks:
            for clip in track.clips:
                if clip.duration < rapid_cut_threshold:
                    errors.append(
                        f"Rapid Cut: Clip '{clip.name}' is too short ({clip.duration} frames)."
                    )

                # Mock Empty Frame logic: if camera pans way out of bounds
                # We would usually inspect keyframes here. Let's mock a transition rule check.
                if clip.transition_in == "Custom Transition":
                    errors.append(
                        f"Validation Warning: '{clip.name}' uses undefined Custom Transition."
                    )

        return errors

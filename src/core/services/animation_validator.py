"""
Animation Validator for checking timeline integrity.
"""

from src.models.animation_model import AnimationTimeline


class AnimationValidator:
    @staticmethod
    def validate_timeline(timeline: AnimationTimeline) -> list[str]:
        errors = []

        for track in timeline.tracks:
            for clip in track.clips:
                end_frame = clip.start_frame + clip.duration
                if end_frame > timeline.total_frames:
                    errors.append(
                        (
                            "Broken Timeline: Clip '"
                            + f"{clip.name}"
                            + "' extends beyond total frames ("
                            + f"{end_frame} > {timeline.total_frames}"
                            + ")."
                        )
                    )

                # Check for conflicting keyframes (same frame, same property)
                seen_kfs = set()
                for kf in clip.keyframes:
                    kf_id = f"{kf.frame}_{kf.property_name}"
                    if kf_id in seen_kfs:
                        errors.append(
                            f"Conflicting Keyframes: Multiple keyframes on frame {kf.frame} for '{kf.property_name}'."
                        )
                    seen_kfs.add(kf_id)

        return errors

from src.core.services.animation_validator import AnimationValidator
from src.models.animation_model import (
    AnimationClip,
    AnimationTimeline,
    AnimationTrack,
    Keyframe,
)


def test_animation_validator():
    timeline = AnimationTimeline(total_frames=100)
    track = AnimationTrack()

    # Valid clip
    clip1 = AnimationClip(name="Walk", start_frame=0, duration=24)
    kf1 = Keyframe(frame=0, property_name="x", value=10)
    kf2 = Keyframe(frame=10, property_name="x", value=20)
    clip1.keyframes = [kf1, kf2]

    # Invalid clip (out of bounds)
    clip2 = AnimationClip(name="Run", start_frame=90, duration=20)

    # Invalid clip (conflicting keyframes)
    clip3 = AnimationClip(name="Jump", start_frame=0, duration=10)
    kf3 = Keyframe(frame=5, property_name="y", value=10)
    kf4 = Keyframe(frame=5, property_name="y", value=20)
    clip3.keyframes = [kf3, kf4]

    track.clips = [clip1, clip2, clip3]
    timeline.tracks.append(track)

    errors = AnimationValidator.validate_timeline(timeline)

    assert any("Broken Timeline" in e for e in errors)
    assert any("Conflicting Keyframes" in e for e in errors)

    # Remove bad clips
    track.clips = [clip1]
    errors = AnimationValidator.validate_timeline(timeline)
    assert len(errors) == 0

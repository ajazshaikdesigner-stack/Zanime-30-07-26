from src.core.services.voice_validator import VoiceValidator
from src.models.voice_model import DialogueClip, VoiceTimeline, VoiceTrack


def test_voice_validator():
    timeline = VoiceTimeline()
    track = VoiceTrack()

    # Valid clip
    clip1 = DialogueClip(
        text="Hello!", voice_profile_uuid="123", start_frame=0, duration=24
    )

    # Overlapping clip
    clip2 = DialogueClip(
        text="Wait!", voice_profile_uuid="123", start_frame=12, duration=24
    )

    # Missing voice and text
    clip3 = DialogueClip(start_frame=50, duration=24)

    track.clips = [clip1, clip2, clip3]
    timeline.tracks.append(track)

    errors = VoiceValidator.validate_timeline(timeline)

    assert any("Overlapping Audio" in e for e in errors)
    assert any("Missing Voice" in e for e in errors)
    assert any("Missing Dialogue" in e for e in errors)

    # Remove bad clips
    track.clips = [clip1]
    errors = VoiceValidator.validate_timeline(timeline)
    assert len(errors) == 0

import pytest
from src.models.camera_model import CameraTimeline, CameraTrack, CameraClip
from src.core.services.shot_analyzer import ShotAnalyzer

def test_shot_analyzer():
    timeline = CameraTimeline(fps=24)
    track = CameraTrack()
    
    # Valid clip
    clip1 = CameraClip(name="Long Shot", duration=120)
    
    # Rapid cut (under 12 frames for 24fps)
    clip2 = CameraClip(name="Action Cut", duration=5)
    
    # Custom transition warning
    clip3 = CameraClip(name="Weird Transition", duration=48, transition_in="Custom Transition")
    
    track.clips = [clip1, clip2, clip3]
    timeline.tracks.append(track)
    
    errors = ShotAnalyzer.analyze(timeline)
    
    assert any("Rapid Cut" in e for e in errors)
    assert any("Custom Transition" in e for e in errors)
    
    track.clips = [clip1]
    errors = ShotAnalyzer.analyze(timeline)
    assert len(errors) == 0

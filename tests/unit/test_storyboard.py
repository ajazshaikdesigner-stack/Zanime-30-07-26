import pytest
import os
from src.models.storyboard_model import StoryboardModel, SceneModel, ShotModel
from src.core.services.continuity_checker import ContinuityChecker
from src.core.services.storyboard_io import StoryboardIO

def test_continuity_checker():
    model = StoryboardModel()
    scene = SceneModel()
    shot = ShotModel(duration=0.0) # Invalid duration
    scene.shots.append(shot)
    model.scenes.append(scene)
    
    errors = ContinuityChecker.check(model)
    assert len(errors) == 2
    assert any("Environment" in e for e in errors)
    assert any("Duration" in e for e in errors)
    
    # Fix errors
    scene.environment_uuid = "123"
    shot.duration = 2.0
    
    assert len(ContinuityChecker.check(model)) == 0

def test_storyboard_io(tmp_path):
    model = StoryboardModel(title="Test Board")
    
    json_path = os.path.join(tmp_path, "board.json")
    pdf_path = os.path.join(tmp_path, "board.pdf")
    
    assert StoryboardIO.export_json(model, json_path) is True
    assert os.path.exists(json_path)
    
    assert StoryboardIO.export_pdf(model, pdf_path) is True
    assert os.path.exists(pdf_path)

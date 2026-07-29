import pytest
from src.models.composer_model import ComposerShot, ComposerObject, LayerType
from src.core.services.scene_validator import SceneValidator

def test_scene_validator():
    shot = ComposerShot()
    obj1 = ComposerObject(name="Hero", x=0, y=0, visible=True, layer=LayerType.CHARACTERS)
    shot.objects.append(obj1)
    
    errors = SceneValidator.validate_shot(shot)
    # Missing background error
    assert any("Missing Background" in e for e in errors)
    
    # Add out of bounds object
    obj2 = ComposerObject(name="Prop", x=9999, y=0, visible=False, layer=LayerType.BACKGROUND)
    shot.objects.append(obj2)
    
    errors = SceneValidator.validate_shot(shot)
    assert any("Hidden Object" in e for e in errors)
    assert any("Out of Bounds" in e for e in errors)
    assert not any("Missing Background" in e for e in errors) # Has bg now

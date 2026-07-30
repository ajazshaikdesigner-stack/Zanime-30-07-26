from src.core.services.production_validator import ProductionValidator


def test_production_validator():
    # Test completely broken scene
    errors = ProductionValidator.validate_scene("scene_1", False, False, False)
    assert any("Missing Camera" in e for e in errors)
    assert any("Missing Animation" in e for e in errors)
    assert any("Missing Voice" in e for e in errors)

    # Test valid scene
    errors2 = ProductionValidator.validate_scene("scene_2", True, True, True)
    assert len(errors2) == 0

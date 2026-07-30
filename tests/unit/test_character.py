import os

from src.core.services.character_io import CharacterIO
from src.core.services.character_validator import CharacterValidator
from src.models.character_model import CharacterModel, Outfit


def test_character_validator():
    model = CharacterModel()

    warnings = CharacterValidator.validate(model)
    # Default model should fail validation
    assert len(warnings) >= 4

    # Fix name
    model.dna.name = "Hero"

    # Add outfit
    model.outfits["Casual"] = Outfit(name="Casual", clothes="T-shirt")

    # Add expression
    model.expressions["Happy"] = "happy.png"

    # Add pose
    model.poses["Standing"] = "standing.png"

    # Add front sheet
    model.model_sheet.front = "front.png"

    warnings = CharacterValidator.validate(model)
    assert len(warnings) == 0


def test_character_io(tmp_path):
    model = CharacterModel()
    model.dna.name = "TestIO"
    model.dna.age = 25
    model.is_favorite = True

    file_path = os.path.join(tmp_path, "char.json")

    assert CharacterIO.export_json(model, file_path) is True
    assert os.path.exists(file_path)

    loaded = CharacterIO.import_json(file_path)
    assert loaded.dna.name == "TestIO"
    assert loaded.dna.age == 25
    assert loaded.is_favorite is True

from src.core.services.story_validator import StoryValidator
from src.models.story_model import StoryModel


def test_story_validation_incomplete():
    model = StoryModel()
    model.content = "Short story."

    warnings = StoryValidator.validate(model)
    assert any("short" in w for w in warnings)


def test_story_validation_ending():
    model = StoryModel()
    model.content = "This is a sentence without punctuation"

    warnings = StoryValidator.validate(model)
    assert any("punctuation" in w for w in warnings)


def test_story_validation_characters():
    model = StoryModel()
    model.content = "This is a story. Yes!"
    model.characters = []

    warnings = StoryValidator.validate(model)
    assert any("characters" in w for w in warnings)


def test_story_validation_pass():
    model = StoryModel()
    # 50+ words
    model.content = "Word " * 60 + "End!"
    model.characters = ["John"]

    warnings = StoryValidator.validate(model)
    assert len(warnings) == 0

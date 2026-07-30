"""
Validator for CharacterModel data.
"""

from src.models.character_model import CharacterModel


class CharacterValidator:
    @staticmethod
    def validate(model: CharacterModel) -> list[str]:
        warnings = []

        if not model.dna.name or model.dna.name == "New Character":
            warnings.append("⚠️ Character name is not set properly.")

        if not model.outfits:
            warnings.append("⚠️ Missing Outfit: Character has no outfits defined.")

        if not model.expressions:
            warnings.append("⚠️ Missing Expressions: No facial expressions mapped.")

        if not model.poses:
            warnings.append("⚠️ Missing Poses: No poses mapped.")

        if not model.model_sheet.front:
            warnings.append("⚠️ Broken Assets: Missing front profile image.")

        # Duplicate detection would normally query a database or project manager

        return warnings

"""
Character I/O operations (Export/Import).
"""

import json

from src.models.character_model import CharacterModel


class CharacterIO:
    @staticmethod
    def export_json(model: CharacterModel, path: str) -> bool:
        """Dumps character metadata to JSON."""
        # Simple serialization
        data = {
            "name": model.dna.name,
            "age": model.dna.age,
            "gender": model.dna.gender,
            "outfits": list(model.outfits.keys()),
            "favorite": model.is_favorite,
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception:
            return False

    @staticmethod
    def import_json(path: str) -> CharacterModel:
        """Loads a character from JSON."""
        model = CharacterModel()
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                model.dna.name = data.get("name", "Unknown")
                model.dna.age = data.get("age", 18)
                model.dna.gender = data.get("gender", "Unknown")
                model.is_favorite = data.get("favorite", False)
        except Exception:
            pass
        return model

"""
Service to validate the content of a StoryModel.
"""
from typing import List
from src.models.story_model import StoryModel

class StoryValidator:
    @staticmethod
    def validate(model: StoryModel) -> List[str]:
        warnings = []
        
        # Incomplete checking
        words = len(model.content.split())
        if words < 50 and model.content.strip() != "":
            warnings.append("⚠️ Story is very short (under 50 words)")
            
        # Ending checks
        if model.content.strip():
            last_char = model.content.strip()[-1]
            if last_char not in ['.', '!', '?', '"', "'"]:
                warnings.append("⚠️ Story appears to have a missing ending (no punctuation)")
                
        # Character checks
        if not model.characters:
            warnings.append("⚠️ No characters detected")
            
        return warnings

"""
Asset Validator for Environments and Props.
"""
from typing import List
from src.models.world_model import EnvironmentDNA, PropModel

class AssetValidator:
    @staticmethod
    def validate_environment(model: EnvironmentDNA) -> List[str]:
        warnings = []
        if not model.name or model.name == "New Environment":
            warnings.append("⚠️ Missing Metadata: Name not set.")
        if not model.image_path:
            warnings.append("⚠️ Broken Asset: No preview image generated.")
        if not model.resolution:
            warnings.append("⚠️ Invalid Resolution.")
        return warnings
        
    @staticmethod
    def validate_prop(model: PropModel) -> List[str]:
        warnings = []
        if not model.name or model.name == "New Prop":
            warnings.append("⚠️ Missing Metadata: Name not set.")
        if not model.image_path:
            warnings.append("⚠️ Broken Asset: No preview image generated.")
        return warnings

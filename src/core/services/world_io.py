"""
World I/O operations (Export/Import).
"""

import json
import logging

from src.models.world_model import EnvironmentDNA, PropModel

logger = logging.getLogger(__name__)


class WorldIO:
    @staticmethod
    def export_environment_json(model: EnvironmentDNA, path: str) -> bool:
        data = {
            "name": model.name,
            "category": model.category,
            "style": model.style,
            "lighting": model.lighting,
            "weather": model.weather,
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception:  # noqa: BLE001
            logger.exception("WorldIO: Failed to export environment JSON to %s", path)
            return False

    @staticmethod
    def export_prop_json(model: PropModel, path: str) -> bool:
        data = {
            "name": model.name,
            "category": model.category,
            "material": model.material,
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception:  # noqa: BLE001
            logger.exception("WorldIO: Failed to export prop JSON to %s", path)
            return False

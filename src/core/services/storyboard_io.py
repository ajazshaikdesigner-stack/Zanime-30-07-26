"""
Storyboard IO
"""

import json

from src.models.storyboard_model import StoryboardModel


class StoryboardIO:
    @staticmethod
    def export_json(model: StoryboardModel, path: str) -> bool:
        data = {
            "title": model.title,
            "total_duration": model.total_duration,
            "scenes": [
                {"name": s.name, "shots": [{"duration": sh.duration} for sh in s.shots]}
                for s in model.scenes
            ],
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception:
            return False

    @staticmethod
    def export_pdf(model: StoryboardModel, path: str) -> bool:
        # Mock PDF creation
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"PDF EXPORT: {model.title}")
            return True
        except Exception:
            return False

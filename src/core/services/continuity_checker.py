"""
Continuity Checker for validating Storyboard integrity.
"""

from src.models.storyboard_model import StoryboardModel


class ContinuityChecker:
    @staticmethod
    def check(model: StoryboardModel) -> list[str]:
        errors = []
        for scene in model.scenes:
            if not scene.environment_uuid:
                errors.append(f"Scene {scene.number}: Missing Environment Assignment.")

            for shot in scene.shots:
                if shot.duration <= 0:
                    errors.append(
                        f"Scene {scene.number}, Shot {shot.number}: Timeline Error (Duration <= 0)."
                    )

        return errors

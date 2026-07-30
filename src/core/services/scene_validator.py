"""
Scene Validator ensures all placed objects are legal within the Composer.
"""

from src.models.composer_model import ComposerShot, LayerType


class SceneValidator:
    @staticmethod
    def validate_shot(
        shot: ComposerShot, canvas_width=1920, canvas_height=1080
    ) -> list[str]:
        errors = []

        # Check background
        has_bg = False
        for obj in shot.objects:
            if obj.layer in (LayerType.BACKGROUND, LayerType.FAR_BACKGROUND):
                has_bg = True

            # Check hidden
            if not obj.visible:
                errors.append(f"Hidden Object: '{obj.name}' is invisible.")

            # Check bounds
            # This is a naive check (doesn't account for scale perfectly, but proves the concept)
            if (
                obj.x < -canvas_width
                or obj.x > canvas_width * 2
                or obj.y < -canvas_height
                or obj.y > canvas_height * 2
            ):
                errors.append(
                    f"Out of Bounds: '{obj.name}' is placed way outside the camera frame."
                )

        if not has_bg and not shot.background_uuid:
            errors.append("Missing Background: Shot has no environment layer assigned.")

        return errors

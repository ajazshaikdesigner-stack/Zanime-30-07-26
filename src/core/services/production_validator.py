"""
Production Validator - Pre-flight checks before sending project to the render queue.
"""


class ProductionValidator:
    @staticmethod
    def validate_scene(
        scene_uuid: str, has_camera: bool, has_animation: bool, has_voice: bool
    ) -> list[str]:
        """
        Mock validation. In a real scenario, this would query the Data Manager
        to ensure timelines are fully populated.
        """
        errors = []

        if not has_camera:
            errors.append("Missing Camera: Scene has no camera assigned.")

        if not has_animation:
            errors.append("Missing Animation: Characters lack keyframes or clips.")

        if not has_voice:
            errors.append("Missing Voice: Scene requires dialogue but none is present.")

        return errors

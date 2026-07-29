"""
Demo Project Manager - Bootstraps 'The Crystal Forest' project.
"""
import logging
from src.models.base import ProjectModel

logger = logging.getLogger(__name__)

class DemoProjectManager:
    @staticmethod
    def create_crystal_forest_demo() -> ProjectModel:
        logger.info("Bootstrapping Demo Project: The Crystal Forest")
        proj = ProjectModel(name="The Crystal Forest")
        
        # In a real app, this would deeply populate models for Story, Characters, etc.
        # For this implementation, we just set the high level project data.
        proj.resolution = (1920, 1080)
        proj.fps = 24
        
        return proj

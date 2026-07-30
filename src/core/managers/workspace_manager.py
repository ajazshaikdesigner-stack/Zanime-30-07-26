"""
Workspace Manager for switching UI contexts.
"""

import logging

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.managers.layout_manager import LayoutManager

logger = logging.getLogger(__name__)


class WorkspaceManager:
    def __init__(self, event_bus: EventBus, layout_manager: LayoutManager):
        self.event_bus = event_bus
        self.layout_manager = layout_manager
        self.active_workspace: str = "Welcome"

    def set_workspace(self, workspace_name: str, force: bool = False) -> None:
        """Changes the active workspace and publishes an event for the UI."""
        if self.active_workspace != workspace_name or force:
            logger.info(
                f"Switching workspace from {self.active_workspace} to {workspace_name}"
            )

            # Save layout of current workspace before switching
            if self.active_workspace and self.active_workspace not in ("Home", "Welcome"):
                self.layout_manager.save_layout(self.active_workspace)

            self.active_workspace = workspace_name
            self.event_bus.publish(Event.WORKSPACE_CHANGED, workspace_name)

            # Try restoring layout for the new workspace
            self.layout_manager.restore_layout(workspace_name)

            # Lazily initialize AI framework if needed
            ai_workspaces = {
                "Story",
                "Script",
                "Characters",
                "World",
                "Storyboard",
                "Camera",
                "Animation",
                "Voice",
                "Music",
                "SceneComposer",
            }
            if workspace_name in ai_workspaces:
                from PySide6.QtCore import QRunnable, QThreadPool

                from src.core.ai.manager import AIManager
                from src.core.services.service_registry import registry

                try:
                    ai_manager = registry.get(AIManager)
                    if not ai_manager._is_initialized:
                        runnable = QRunnable.create(ai_manager.initialize)
                        QThreadPool.globalInstance().start(runnable)
                except KeyError:
                    logger.debug("WorkspaceManager: AIManager not registered; skipping lazy AI initialization.")


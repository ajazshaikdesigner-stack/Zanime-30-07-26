"""
Factory for dynamically instantiating UI workspaces on demand.
"""

import logging
import traceback
from collections import OrderedDict
from typing import Any

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.ui.workspaces.animation_workspace import AnimationWorkspace
from src.ui.workspaces.backgrounds_workspace import BackgroundsWorkspace
from src.ui.workspaces.camera_workspace import CameraWorkspace
from src.ui.workspaces.characters_workspace import CharactersWorkspace
from src.ui.workspaces.home_workspace import HomeWorkspace
from src.ui.workspaces.library_workspace import LibraryWorkspace
from src.ui.workspaces.music_workspace import MusicWorkspace
from src.ui.workspaces.performance_workspace import PerformanceWorkspace
from src.ui.workspaces.props_workspace import PropsWorkspace
from src.ui.workspaces.render_workspace import RenderWorkspace
from src.ui.workspaces.scene_composer_workspace import SceneComposerWorkspace
from src.ui.workspaces.script_workspace import ScriptWorkspace
from src.ui.workspaces.settings_workspace import SettingsWorkspace
from src.ui.workspaces.story_workspace import StoryWorkspace
from src.ui.workspaces.storyboard_workspace import StoryboardWorkspace
from src.ui.workspaces.tutorial_workspace import TutorialWorkspace
from src.ui.workspaces.voice_workspace import VoiceWorkspace
from src.ui.workspaces.welcome_workspace import WelcomeWorkspace
from src.ui.workspaces.world_workspace import WorldWorkspace

logger = logging.getLogger(__name__)


class WorkspaceErrorWidget(QWidget):
    def __init__(self, name: str, exc: Exception, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        lbl_title = QLabel(f"Failed to load workspace: {name}")
        lbl_title.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
        layout.addWidget(lbl_title)

        lbl_err = QLabel(f"{type(exc).__name__}: {exc!s}")
        lbl_err.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(lbl_err)

        lbl_trace = QLabel(traceback.format_exc())
        lbl_trace.setStyleSheet("font-family: monospace; color: #ccc;")
        lbl_trace.setWordWrap(True)
        layout.addWidget(lbl_trace)

        layout.addStretch()

    def get_required_docks(self):
        return []

    def get_hidden_docks(self):
        return []

    def save_state(self):
        return None

    def restore_state(self, state):
        pass


class WorkspaceFactory:
    def __init__(self, max_cache_size: int = 20):
        self.max_cache_size = max_cache_size
        self._cache = OrderedDict()
        self._state_cache: dict[str, Any] = {}

        self._registry = {
            "Home": HomeWorkspace,
            "Story": StoryWorkspace,
            "Script": ScriptWorkspace,
            "Characters": CharactersWorkspace,
            "Backgrounds": BackgroundsWorkspace,
            "Props": PropsWorkspace,
            "World": WorldWorkspace,
            "Storyboard": StoryboardWorkspace,
            "Camera": CameraWorkspace,
            "SceneComposer": SceneComposerWorkspace,
            "Animation": AnimationWorkspace,
            "Voice": VoiceWorkspace,
            "Music": MusicWorkspace,
            "Tutorial": TutorialWorkspace,
            "Performance": PerformanceWorkspace,
            "Welcome": WelcomeWorkspace,
            "Render": RenderWorkspace,
            "Library": LibraryWorkspace,
            "Settings": SettingsWorkspace,
        }

    def get_workspace(self, name: str, app, main_window) -> QWidget:
        """Retrieves a workspace from the cache, instantiating it if necessary."""
        if name not in self._registry:
            raise ValueError(f"Workspace '{name}' is not registered in the factory.")

        if name in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(name)
            return self._cache[name]

        # Needs instantiation
        logger.info(f"WorkspaceFactory: Instantiating {name}")
        cls = self._registry[name]

        try:
            widget = cls(app, main_window)
        except Exception as e:
            logger.exception(
                f"WorkspaceFactory: Crash during {name} initialization"
            )
            widget = WorkspaceErrorWidget(name, e, main_window)

        # Restore state if previously cached
        if name in self._state_cache and hasattr(widget, "restore_state"):
            try:
                widget.restore_state(self._state_cache[name])
            except Exception as e:
                logger.error(f"Failed to restore state for {name}: {e}")

        self._cache[name] = widget
        self._enforce_cache_limits(main_window)
        return widget

    def destroy_workspace(self, name: str, main_window):
        """Explicitly ejects a workspace from memory and saves its state."""
        if name not in self._cache:
            return

        widget = self._cache[name]

        # Save state before destruction
        if hasattr(widget, "save_state"):
            try:
                self._state_cache[name] = widget.save_state()
            except Exception as e:
                logger.error(f"Failed to save state for {name}: {e}")

        logger.info(f"WorkspaceFactory: Ejecting {name} to reclaim memory.")
        self._cache.pop(name)
        main_window.workspace_stack.removeWidget(widget)
        widget.deleteLater()

    def reload_workspace(self, name: str, app, main_window):
        """Forces a workspace to be destroyed and re-instantiated."""
        self.destroy_workspace(name, main_window)
        return self.get_workspace(name, app, main_window)

    def cleanup_memory(self, main_window, active_workspace_name: str | None = None):
        """Destroys all workspaces except the active one to maximize free RAM."""
        names_to_destroy = []
        for name in list(self._cache.keys()):
            if name != active_workspace_name and name != "Welcome":
                names_to_destroy.append(name)

        for name in names_to_destroy:
            self.destroy_workspace(name, main_window)

    def _enforce_cache_limits(self, main_window):
        """Destroys the least recently used workspace if the cache exceeds limits."""
        if len(self._cache) > self.max_cache_size:
            # oldest is at the front of the OrderedDict
            for name in list(self._cache.keys()):
                # Protect Welcome space
                if name == "Welcome":
                    continue

                # Do not eject the most recently accessed
                if name == next(reversed(self._cache)):
                    continue

                self.destroy_workspace(name, main_window)

                # Check if we're under the limit now
                if len(self._cache) <= self.max_cache_size:
                    break

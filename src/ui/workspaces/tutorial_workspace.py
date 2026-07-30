"""
Tutorial Workspace - The Meta Workspace wrapping the entire learning experience.
"""

import logging

from PySide6.QtCore import Qt

from src.core.managers.demo_manager import DemoProjectManager
from src.core.managers.tutorial_manager import TutorialManager
from src.core.sdk.base_workspace import BaseWorkspace
from src.ui.docks.tutorial_instructions_dock import TutorialInstructionsDock
from src.ui.docks.tutorial_navigation_dock import TutorialNavigationDock
from src.ui.docks.tutorial_progress_dock import TutorialProgressDock
from src.ui.widgets.tutorial_host_widget import TutorialHostWidget

logger = logging.getLogger(__name__)


class TutorialWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Interactive Tutorial", parent)
        self.app = app

        self.tutorial_manager = TutorialManager()
        self.demo_project = DemoProjectManager.create_crystal_forest_demo()

        self.host_widget = TutorialHostWidget(self)
        self.setCentralWidget(self.host_widget)

        # Setup Docks
        self.nav_dock = TutorialNavigationDock(self)
        self.inst_dock = TutorialInstructionsDock(self)
        self.prog_dock = TutorialProgressDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.nav_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.inst_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.prog_dock)

        # Setup Mock Workspaces for the StackedWidget
        workspace_names = [
            "Story",
            "Characters",
            "World",
            "SceneComposer",
            "Animation",
            "Camera",
            "Voice",
            "Render",
        ]
        for w in workspace_names:
            self.host_widget.add_mock_workspace(w)

        # Connect Signals
        self.tutorial_manager.step_changed.connect(self._on_step_changed)
        self.tutorial_manager.progress_updated.connect(self._on_progress_updated)
        self.tutorial_manager.achievement_unlocked.connect(self._on_achievement)

        self.inst_dock.next_btn.clicked.connect(self.tutorial_manager.next_step)
        self.inst_dock.prev_btn.clicked.connect(self.tutorial_manager.prev_step)

        # Init
        self.nav_dock.populate(self.tutorial_manager.steps)
        self.tutorial_manager._emit_state()

    def _on_step_changed(self, step):
        self.nav_dock.set_current_step(step.step_id)
        self.inst_dock.update_step(step)
        self.host_widget.switch_to(step.target_workspace)

    def _on_progress_updated(self, current, total):
        self.prog_dock.update_progress(current, total)

    def _on_achievement(self, ach):
        self.prog_dock.log_achievement(ach)

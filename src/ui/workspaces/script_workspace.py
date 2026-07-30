"""
Script Workspace - Screenplay and dialogue editing environment.
"""

import logging

from PySide6.QtCore import Qt, QTimer

from src.core.ai import ZanimeAIAPI
from src.core.sdk.base_workspace import BaseWorkspace
from src.core.services.service_registry import registry
from src.ui.docks.ai_console_dock import AIConsoleDock
from src.ui.docks.dialogue_timeline_dock import DialogueTimelineDock
from src.ui.docks.scene_list_dock import SceneListDock
from src.ui.docks.story_settings_dock import StorySettingsDock
from src.ui.widgets.dialogue_editor import DialogueEditor

logger = logging.getLogger(__name__)


class ScriptWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Script Studio", parent)
        self.app = app

        # Center Widget
        self.editor = DialogueEditor(self)
        self.setCentralWidget(self.editor)

        # Docks
        self.list_dock = SceneListDock(self)
        self.settings_dock = StorySettingsDock(self)
        self.timeline_dock = DialogueTimelineDock(self)
        self.console_dock = AIConsoleDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.list_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.settings_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.timeline_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)

        self.tabifyDockWidget(self.timeline_dock, self.console_dock)
        self.timeline_dock.raise_()

        # Connect AI Gen button
        self.settings_dock.generate_btn.clicked.connect(self._generate_script)

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30 * 1000)

    def _generate_script(self):
        prompt = self.settings_dock.prompt_edit.toPlainText()
        logger.info("ScriptWorkspace: Generating script for prompt: %s", prompt)
        registry.get(ZanimeAIAPI).generate_story(
            f"Write screenplay dialogue: {prompt}", {}
        )

    def autosave(self):
        logger.info("ScriptWorkspace: Autosaving screenplay script...")

    def get_required_docks(self):
        return []

    def get_hidden_docks(self):
        return [
            "Properties",
            "Timeline",
            "ProjectExplorer",
            "Console",
            "AssetBrowser",
            "NotificationCenter",
            "History",
            "Preview",
        ]

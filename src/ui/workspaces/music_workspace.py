"""
Music Workspace - BGM, SFX, and audio composition studio.
"""

import logging

from PySide6.QtCore import Qt, QTimer

from src.core.ai import ZanimeAIAPI
from src.core.sdk.base_workspace import BaseWorkspace
from src.core.services.service_registry import registry
from src.ui.docks.ai_console_dock import AIConsoleDock
from src.ui.docks.dialogue_timeline_dock import DialogueTimelineDock
from src.ui.docks.voice_library_dock import VoiceLibraryDock
from src.ui.docks.voice_properties_dock import VoicePropertiesDock
from src.ui.widgets.dialogue_editor import DialogueEditor

logger = logging.getLogger(__name__)


class MusicWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Music Studio", parent)
        self.app = app

        self.editor = DialogueEditor(self)
        self.setCentralWidget(self.editor)

        self.library_dock = VoiceLibraryDock(self)
        self.properties_dock = VoicePropertiesDock(self)
        self.timeline_dock = DialogueTimelineDock(self)
        self.console_dock = AIConsoleDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.library_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.timeline_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)

        self.tabifyDockWidget(self.timeline_dock, self.console_dock)
        self.timeline_dock.raise_()

        self.properties_dock.generate_btn.clicked.connect(self._generate_music)

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30 * 1000)

    def _generate_music(self):
        text = self.editor.text_edit.toPlainText()
        prompt = f"BGM & SFX composition: {text if text else 'Epic cinematic soundtrack'}"
        logger.info("Generating Music: %s", prompt)
        registry.get(ZanimeAIAPI).generate_voice(prompt, {})

    def autosave(self):
        logger.info("MusicWorkspace: Autosaving audio tracks...")

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

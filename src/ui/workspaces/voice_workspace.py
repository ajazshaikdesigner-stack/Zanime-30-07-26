"""
Voice & Dialogue Workspace
"""

import logging

from PySide6.QtCore import Qt, QTimer

from src.core.ai import ZanimeAIAPI
from src.core.sdk.base_workspace import BaseWorkspace
from src.core.services.service_registry import registry
from src.models.voice_model import VoiceTimeline
from src.ui.docks.ai_console_dock import AIConsoleDock
from src.ui.docks.dialogue_timeline_dock import DialogueTimelineDock
from src.ui.docks.voice_library_dock import VoiceLibraryDock
from src.ui.docks.voice_properties_dock import VoicePropertiesDock
from src.ui.widgets.dialogue_editor import DialogueEditor

logger = logging.getLogger(__name__)


class VoiceWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Voice Studio", parent)
        self.app = app

        self.timeline_data = VoiceTimeline()

        self.editor = DialogueEditor(self)
        self.setCentralWidget(self.editor)

        self.library_dock = VoiceLibraryDock(self)
        self.properties_dock = VoicePropertiesDock(self)
        self.timeline_dock = DialogueTimelineDock(self)
        self.console_dock = AIConsoleDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.library_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.timeline_dock)

        self.tabifyDockWidget(self.timeline_dock, self.console_dock)
        self.timeline_dock.raise_()

        # Connect AI Gen
        self.properties_dock.generate_btn.clicked.connect(self._generate_voice)

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30 * 1000)

    def _generate_voice(self):
        text = self.editor.text_edit.toPlainText()
        if not text:
            logger.warning("VoiceWorkspace: No text entered for voice generation.")
            return

        prompt = f"TTS: {text}"
        logger.info(f"Generating Voice: {prompt}")
        registry.get(ZanimeAIAPI).generate_voice(prompt, {})
        registry.get(ZanimeAIAPI).generate_lipsync(prompt, {})

    def autosave(self):
        logger.info("VoiceWorkspace: Autosaving audio tracks...")

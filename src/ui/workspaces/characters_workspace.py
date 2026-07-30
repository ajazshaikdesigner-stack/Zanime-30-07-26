"""
Characters Workspace
"""

import logging

from PySide6.QtCore import Qt, QTimer

from src.core.ai import ZanimeAIAPI
from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.sdk.base_workspace import BaseWorkspace
from src.core.services.service_registry import registry
from src.models.character_model import CharacterModel
from src.ui.docks.ai_console_dock import AIConsoleDock
from src.ui.docks.character_library_dock import CharacterLibraryDock
from src.ui.docks.character_properties_dock import CharacterPropertiesDock
from src.ui.widgets.character_preview import CharacterPreview

logger = logging.getLogger(__name__)


class CharactersWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Character Studio", parent)
        self.app = app
        self.active_character = CharacterModel()

        self.preview = CharacterPreview(self)
        self.setCentralWidget(self.preview)

        self.library_dock = CharacterLibraryDock(self)
        self.properties_dock = CharacterPropertiesDock(self)
        self.console_dock = AIConsoleDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.library_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)

        # Connect AI Gen button
        self.properties_dock.generate_btn.clicked.connect(self._generate_character)
        registry.get(EventBus).subscribe(Event.AI_TASK_COMPLETED, self._on_ai_completed)

        # Autosave timer
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30 * 1000)

    def _generate_character(self):
        # Trigger mock diffusers provider via AI API
        name = self.properties_dock.dna_name.text()
        gender = self.properties_dock.dna_gender.currentText()
        prompt = f"Anime character sheet, 360 view, {name}, {gender}, high quality"
        logger.info(f"Requesting character generation: {prompt}")
        registry.get(ZanimeAIAPI).generate_character_image(prompt, {})

    def _on_ai_completed(self, data: dict):
        # We assume result has 'image_path' from DiffusersProvider mock
        res = data.get("result", {})
        if "image_path" in res:
            # We don't have a real image on disk, so load_image will show "Failed to load: mock_image.png"
            # which proves the wiring is correct.
            self.preview.load_image(res["image_path"])

    def autosave(self):
        logger.info("CharactersWorkspace: Autosaving character...")
        # In a real app, this would use CharacterIO to write to the temp project dir

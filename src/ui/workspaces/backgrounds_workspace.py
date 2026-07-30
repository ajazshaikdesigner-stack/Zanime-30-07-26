"""
Backgrounds Workspace - Environment and background layer studio.
"""

import logging

from PySide6.QtCore import Qt, QTimer

from src.core.ai import ZanimeAIAPI
from src.core.sdk.base_workspace import BaseWorkspace
from src.core.services.service_registry import registry
from src.ui.docks.ai_console_dock import AIConsoleDock
from src.ui.docks.world_library_dock import WorldLibraryDock
from src.ui.docks.world_properties_dock import WorldPropertiesDock
from src.ui.widgets.world_preview import WorldPreview

logger = logging.getLogger(__name__)


class BackgroundsWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Backgrounds Studio", parent)
        self.app = app

        self.preview = WorldPreview(self)
        self.setCentralWidget(self.preview)

        self.library_dock = WorldLibraryDock(self)
        self.properties_dock = WorldPropertiesDock(self)
        self.console_dock = AIConsoleDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.library_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)

        self.properties_dock.generate_btn.clicked.connect(self._generate_background)

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30 * 1000)

    def _generate_background(self):
        env_type = self.properties_dock.env_type.currentText()
        weather = self.properties_dock.weather.currentText()
        prompt = f"Anime background landscape, {env_type}, {weather} weather, high detail"
        logger.info("Requesting background generation: %s", prompt)
        registry.get(ZanimeAIAPI).generate_character_image(prompt, {})

    def autosave(self):
        logger.info("BackgroundsWorkspace: Autosaving background environment...")

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

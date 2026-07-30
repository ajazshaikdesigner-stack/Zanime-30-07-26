"""
Camera Director Workspace
"""

import logging

from PySide6.QtCore import Qt, QTimer

from src.core.ai import ZanimeAIAPI
from src.core.sdk.base_workspace import BaseWorkspace
from src.core.services.service_registry import registry
from src.models.camera_model import Camera, CameraTimeline
from src.ui.docks.ai_console_dock import AIConsoleDock
from src.ui.docks.camera_library_dock import CameraLibraryDock
from src.ui.docks.camera_properties_dock import CameraPropertiesDock
from src.ui.docks.camera_timeline_dock import CameraTimelineDock
from src.ui.widgets.camera_viewport import CameraViewport

logger = logging.getLogger(__name__)


class CameraWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Camera Director", parent)
        self.app = app

        self.timeline_data = CameraTimeline()
        self.active_camera = Camera()

        self.viewport = CameraViewport(self)
        self.setCentralWidget(self.viewport)

        self.library_dock = CameraLibraryDock(self)
        self.properties_dock = CameraPropertiesDock(self)
        self.timeline_dock = CameraTimelineDock(self)
        self.console_dock = AIConsoleDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.library_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.timeline_dock)

        self.tabifyDockWidget(self.timeline_dock, self.console_dock)
        self.timeline_dock.raise_()

        # Connect composition rule change
        self.properties_dock.comp_rule.currentTextChanged.connect(
            self._on_comp_rule_changed
        )

        # Connect AI Gen
        self.properties_dock.generate_btn.clicked.connect(self._generate_camera_plan)

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30 * 1000)

        self.properties_dock.load_camera(self.active_camera)

    def _on_comp_rule_changed(self, text):
        self.viewport.set_composition_mode(text)

    def _generate_camera_plan(self):
        prompt = "Analyze scene and generate cinematic camera shots."
        logger.info(f"Generating Camera Plan: {prompt}")
        registry.get(ZanimeAIAPI).generate_camera_plan(prompt, {})

    def autosave(self):
        logger.info("CameraWorkspace: Autosaving camera tracks...")

"""
Scene Composer Workspace
"""

import logging

from PySide6.QtCore import Qt, QTimer

from src.core.sdk.base_workspace import BaseWorkspace
from src.models.composer_model import ComposerObject, ComposerScene, ComposerShot
from src.ui.docks.composer_properties_dock import ComposerPropertiesDock
from src.ui.docks.composer_timeline_dock import ComposerTimelineDock
from src.ui.docks.scene_hierarchy_dock import SceneHierarchyDock
from src.ui.widgets.movie_canvas import MovieCanvas

logger = logging.getLogger(__name__)


class SceneComposerWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Movie Composer Studio", parent)
        self.app = app

        self.scenes = []

        self.canvas = MovieCanvas(self)
        self.setCentralWidget(self.canvas)

        self.hierarchy_dock = SceneHierarchyDock(self)
        self.properties_dock = ComposerPropertiesDock(self)
        self.timeline_dock = ComposerTimelineDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.hierarchy_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.timeline_dock)

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30 * 1000)

        self._load_mock_data()

    def _load_mock_data(self):
        obj = ComposerObject(name="Hero Sprite")
        shot = ComposerShot(objects=[obj])
        scene = ComposerScene(shots=[shot])
        self.scenes.append(scene)
        self.hierarchy_dock.populate(self.scenes)
        self.properties_dock.load_object(obj)

    def autosave(self):
        logger.info("SceneComposerWorkspace: Autosaving layout...")

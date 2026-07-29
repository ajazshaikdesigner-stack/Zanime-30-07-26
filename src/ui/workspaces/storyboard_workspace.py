"""
Storyboard & Scene Planning Workspace
"""
import logging
import json
from src.core.sdk.base_workspace import BaseWorkspace
from src.ui.docks.scene_list_dock import SceneListDock
from src.ui.docks.storyboard_properties_dock import StoryboardPropertiesDock
from src.ui.widgets.storyboard_canvas import StoryboardCanvas
from src.ui.docks.storyboard_timeline_dock import StoryboardTimelineDock
from src.ui.docks.ai_console_dock import AIConsoleDock
from src.models.storyboard_model import StoryboardModel, SceneModel, ShotModel
from src.core.events.event_types import Event
from PySide6.QtCore import Qt, QTimer
from src.core.services.service_registry import registry
from src.core.events.event_bus import EventBus
from src.core.ai import ZanimeAIAPI

logger = logging.getLogger(__name__)

class StoryboardWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Storyboard Studio", parent)
        self.app = app
        
        self.storyboard = StoryboardModel()
        
        self.canvas = StoryboardCanvas(self)
        self.setCentralWidget(self.canvas)
        
        self.list_dock = SceneListDock(self)
        self.properties_dock = StoryboardPropertiesDock(self)
        self.timeline_dock = StoryboardTimelineDock(self)
        self.console_dock = AIConsoleDock(self)
        
        self.addDockWidget(Qt.LeftDockWidgetArea, self.list_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.timeline_dock)
        
        self.tabifyDockWidget(self.timeline_dock, self.console_dock)
        self.timeline_dock.raise_()
        
        # Connect AI Gen button
        self.properties_dock.generate_btn.clicked.connect(self._generate_storyboard)
        registry.get(EventBus).subscribe(Event.AI_TASK_COMPLETED, self._on_ai_completed)
        
        # Tree click events
        self.list_dock.tree.itemSelectionChanged.connect(self._on_tree_selection)
        
        # Auto save
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30 * 1000)
        
    def _on_tree_selection(self):
        items = self.list_dock.tree.selectedItems()
        if not items:
            return
            
        item = items[0]
        data = item.data(0, 99)
        if data:
            item_type, uuid = data
            if item_type == "scene":
                self.properties_dock.show_scene_properties()
            elif item_type == "shot":
                self.properties_dock.show_shot_properties()

    def _generate_storyboard(self):
        prompt = "Parse screenplay into JSON scene/shot list"
        logger.info(f"Generating Storyboard: {prompt}")
        registry.get(ZanimeAIAPI).generate_storyboard(prompt, {})
        
    def _on_ai_completed(self, data: dict):
        # We mock building a scene/shot list
        scene = SceneModel(name="Generated Scene 1")
        shot1 = ShotModel(number=1, shot_type="Wide", duration=4.0)
        shot2 = ShotModel(number=2, shot_type="Close Up", duration=2.5)
        scene.shots = [shot1, shot2]
        
        self.storyboard.scenes.append(scene)
        self.storyboard.calculate_duration()
        
        self._refresh_ui()
        
    def _refresh_ui(self):
        self.list_dock.populate(self.storyboard)
        self.canvas.render_board(self.storyboard)
        self.timeline_dock.render_timeline(self.storyboard)
        
    def autosave(self):
        logger.info("StoryboardWorkspace: Autosaving storyboard...")

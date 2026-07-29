"""
World Workspace - Environment and Prop Studio
"""
import logging
from src.core.sdk.base_workspace import BaseWorkspace
from src.ui.docks.world_library_dock import WorldLibraryDock
from src.ui.docks.world_properties_dock import WorldPropertiesDock
from src.ui.widgets.world_preview import WorldPreview
from src.ui.docks.ai_console_dock import AIConsoleDock
from src.models.world_model import EnvironmentDNA, PropModel
from src.core.events.event_types import Event
from PySide6.QtCore import Qt, QTimer
from src.core.services.service_registry import registry
from src.core.events.event_bus import EventBus
from src.core.ai import ZanimeAIAPI

logger = logging.getLogger(__name__)

class WorldWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("World Builder Studio", parent)
        self.app = app
        
        self.active_env = EnvironmentDNA()
        self.active_prop = PropModel()
        
        self.preview = WorldPreview(self)
        self.setCentralWidget(self.preview)
        
        self.library_dock = WorldLibraryDock(self)
        self.properties_dock = WorldPropertiesDock(self)
        self.console_dock = AIConsoleDock(self)
        
        self.addDockWidget(Qt.LeftDockWidgetArea, self.library_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)
        
        # Connect library tab switch to properties stack switch
        self.library_dock.tabs.currentChanged.connect(self._on_tab_changed)
        
        # Connect AI Gen button
        self.properties_dock.generate_btn.clicked.connect(self._generate_asset)
        registry.get(EventBus).subscribe(Event.AI_TASK_COMPLETED, self._on_ai_completed)
        
        # Autosave timer
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30 * 1000)
        
    def _on_tab_changed(self, index: int):
        if index == 0:
            self.properties_dock.show_env_properties()
        else:
            self.properties_dock.show_prop_properties()
            
    def _generate_asset(self):
        index = self.library_dock.tabs.currentIndex()
        if index == 0:
            # Environment
            name = self.properties_dock.env_name.text()
            style = self.properties_dock.env_style.currentText()
            lighting = self.properties_dock.env_lighting.currentText()
            weather = self.properties_dock.env_weather.currentText()
            prompt = f"Environment, {name}, {style} style, {lighting}, {weather}"
            logger.info(f"Generating Environment: {prompt}")
            registry.get(ZanimeAIAPI).generate_environment(prompt, {})
        else:
            # Prop
            name = self.properties_dock.prop_name.text()
            material = self.properties_dock.prop_material.currentText()
            prompt = f"Prop design, {name}, {material}, high detail"
            logger.info(f"Generating Prop: {prompt}")
            registry.get(ZanimeAIAPI).generate_prop(prompt, {})
            
    def _on_ai_completed(self, data: dict):
        res = data.get("result", {})
        if "image_path" in res:
            self.preview.load_image(res["image_path"])
            
    def autosave(self):
        logger.info("WorldWorkspace: Autosaving assets...")

"""
Animation Director Workspace
"""
import logging
from src.core.sdk.base_workspace import BaseWorkspace
from src.ui.docks.animation_library_dock import AnimationLibraryDock
from src.ui.docks.animation_properties_dock import AnimationPropertiesDock
from src.ui.docks.animation_timeline_dock import AnimationTimelineDock
from src.ui.widgets.animation_viewport import AnimationViewport
from src.models.animation_model import AnimationTimeline, AnimationTrack, AnimationClip, Keyframe
from PySide6.QtCore import Qt, QTimer
from src.core.services.service_registry import registry
from src.core.ai import ZanimeAIAPI

logger = logging.getLogger(__name__)

class AnimationWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Animation Director", parent)
        self.app = app
        
        self.timeline_data = AnimationTimeline()
        
        self.viewport = AnimationViewport(self)
        self.setCentralWidget(self.viewport)
        
        self.library_dock = AnimationLibraryDock(self)
        self.properties_dock = AnimationPropertiesDock(self)
        self.timeline_dock = AnimationTimelineDock(self)
        
        self.addDockWidget(Qt.LeftDockWidgetArea, self.library_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.timeline_dock)
        
        # Connect AI Gen
        self.properties_dock.generate_btn.clicked.connect(self._generate_animation)
        
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30 * 1000)
        
        self._load_mock_data()
        
    def _load_mock_data(self):
        kf = Keyframe(frame=10, value=150.0, interpolation="Bezier", property_name="x")
        clip = AnimationClip(name="Walk", start_frame=0, duration=24, keyframes=[kf])
        track = AnimationTrack(clips=[clip])
        self.timeline_data.tracks.append(track)
        self.properties_dock.load_keyframe(kf)
        
    def _generate_animation(self):
        prompt = "Walk cycle for Anime Character"
        logger.info(f"Generating Animation: {prompt}")
        registry.get(ZanimeAIAPI).generate_animation(prompt, {})
        
    def autosave(self):
        logger.info("AnimationWorkspace: Autosaving timeline...")

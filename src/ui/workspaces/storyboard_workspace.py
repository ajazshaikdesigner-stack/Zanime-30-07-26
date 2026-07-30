"""
Storyboard & Scene Planning Workspace — Phase 3 AI Integration
"""

import json
import logging
import re
import time

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QInputDialog, QMessageBox

from src.core.ai import ZanimeAIAPI
from src.core.ai.history_manager import AIHistoryManager
from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.sdk.base_workspace import BaseWorkspace
from src.core.services.service_registry import registry
from src.models.storyboard_model import SceneModel, ShotModel, StoryboardModel
from src.ui.docks.ai_console_dock import AIConsoleDock
from src.ui.docks.scene_list_dock import SceneListDock
from src.ui.docks.storyboard_properties_dock import StoryboardPropertiesDock
from src.ui.docks.storyboard_timeline_dock import StoryboardTimelineDock
from src.ui.widgets.storyboard_canvas import StoryboardCanvas

logger = logging.getLogger(__name__)


class StoryboardWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Storyboard Studio", parent)
        self.app = app

        self.storyboard = StoryboardModel()
        self._pending_task_id: str | None = None
        self._pending_task_type: str = ""
        self._pending_scene_idx: int = -1  # for panel image generation
        self._task_start_time: float = 0.0

        self.canvas = StoryboardCanvas(self)
        self.setCentralWidget(self.canvas)

        self.list_dock = SceneListDock(self)
        self.properties_dock = StoryboardPropertiesDock(self)
        self.timeline_dock = StoryboardTimelineDock(self)
        self.console_dock = AIConsoleDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.list_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.timeline_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)

        self.tabifyDockWidget(self.timeline_dock, self.console_dock)
        self.timeline_dock.raise_()

        # Connect AI Gen buttons
        self.properties_dock.generate_btn.clicked.connect(self._generate_storyboard_from_scene)
        registry.get(EventBus).subscribe(Event.AI_TASK_COMPLETED, self._on_ai_completed)
        registry.get(EventBus).subscribe(Event.AI_TASK_FAILED, self._on_ai_failed)

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
            item_type, _uuid = data
            if item_type == "scene":
                self.properties_dock.show_scene_properties()
            elif item_type == "shot":
                self.properties_dock.show_shot_properties()

    # ------------------------------------------------------------------
    # AI Generation
    # ------------------------------------------------------------------

    def generate_storyboard_from_story(self, story_text: str):
        """
        Public API: call this with story text to auto-generate a full storyboard.
        Also accessible from Story workspace "Export to Storyboard" button.
        """
        logger.info("StoryboardWorkspace: Generating storyboard from story text.")
        self._task_start_time = time.time()
        self._pending_task_type = "storyboard_plan"
        try:
            task_id = registry.get(ZanimeAIAPI).generate_storyboard_plan(story_text, {})
            self._pending_task_id = task_id
        except Exception:
            logger.exception("StoryboardWorkspace: Failed to queue storyboard generation.")

    def _generate_storyboard_from_scene(self):
        """Triggered by the Generate button in the properties dock."""
        desc = self.properties_dock.get_scene_description()
        if not desc:
            desc, ok = QInputDialog.getMultiLineText(
                self, "Scene Description",
                "Describe the scene to storyboard:"
            )
            if not ok or not desc.strip():
                return

        self._task_start_time = time.time()
        self._pending_task_type = "storyboard_plan"
        try:
            task_id = registry.get(ZanimeAIAPI).generate_storyboard_plan(desc, {})
            self._pending_task_id = task_id
        except Exception:
            logger.exception("StoryboardWorkspace: Failed to queue storyboard generation.")

    def _on_ai_completed(self, data: dict):
        if self._pending_task_id and data.get("id") == self._pending_task_id:
            self._pending_task_id = None
            result = data.get("result", {})
            text = result.get("text", "") if isinstance(result, dict) else str(result)

            if self._pending_task_type == "storyboard_plan":
                self._parse_and_build_storyboard(text)

                # Record in AI history
                try:
                    elapsed_ms = int((time.time() - self._task_start_time) * 1000)
                    registry.get(AIHistoryManager).record(
                        task_type="text",
                        prompt="Storyboard plan generation",
                        output_path="",
                        model_name="llama3:8b",
                        provider="llm",
                        workspace="Storyboard",
                        duration_ms=elapsed_ms,
                    )
                except Exception:
                    pass

    def _on_ai_failed(self, data: dict):
        if self._pending_task_id and data.get("id") == self._pending_task_id:
            self._pending_task_id = None
            logger.error("StoryboardWorkspace: AI generation failed: %s", data.get("error"))

    def _parse_and_build_storyboard(self, text: str):
        """
        Parse JSON shot plan from LLM response and build SceneModel / ShotModel objects.
        The LLM is prompted to return individual JSON objects (one per line or in a list).
        """
        scenes_built = 0
        shot_list = self._extract_json_list(text)

        if shot_list:
            # Group shots into a single generated scene
            scene = SceneModel(
                name="AI Generated Scene",
                description="Auto-generated by ZANIME AI",
                mood="Neutral",
            )
            for i, shot_data in enumerate(shot_list):
                shot = ShotModel(
                    number=i + 1,
                    shot_type=shot_data.get("shot_type", "Wide"),
                    duration=float(shot_data.get("duration_seconds", 3.0)),
                    camera_movement=shot_data.get("camera_movement", "Static"),
                    notes=shot_data.get("description", "") + "\n" + shot_data.get("dialogue", ""),
                )
                scene.shots.append(shot)

            self.storyboard.scenes.append(scene)
            scenes_built = 1
        else:
            # Fallback: create a minimal 3-shot scene from the text
            logger.warning("StoryboardWorkspace: Could not parse JSON from LLM response. Building fallback scene.")
            scene = SceneModel(name="AI Scene", description=text[:200])
            scene.shots = [
                ShotModel(number=1, shot_type="Wide",     duration=4.0, notes="Establishing shot"),
                ShotModel(number=2, shot_type="Medium",   duration=3.0, notes="Character introduction"),
                ShotModel(number=3, shot_type="Close Up", duration=2.0, notes="Reaction shot"),
            ]
            self.storyboard.scenes.append(scene)
            scenes_built = 1

        self.storyboard.calculate_duration()
        self._refresh_ui()
        logger.info("StoryboardWorkspace: Built %d scene(s) from AI output.", scenes_built)

    @staticmethod
    def _extract_json_list(text: str) -> list[dict]:
        """Extract a JSON array or sequence of JSON objects from LLM text."""
        # Try direct JSON array first
        match = re.search(r'\[.*?\]', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        # Try individual JSON objects on each line
        shots = []
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    shots.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return shots

    def _refresh_ui(self):
        self.list_dock.populate(self.storyboard)
        self.canvas.render_board(self.storyboard)
        self.timeline_dock.render_timeline(self.storyboard)

    def autosave(self):
        logger.info("StoryboardWorkspace: Autosaving storyboard...")

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

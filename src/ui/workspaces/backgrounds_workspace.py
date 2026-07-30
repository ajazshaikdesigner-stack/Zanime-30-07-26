"""
Backgrounds Workspace - Environment and background layer studio.
"""

import logging
import time

from PySide6.QtCore import Qt, QTimer

from src.core.ai import ZanimeAIAPI
from src.core.ai.history_manager import AIHistoryManager
from src.core.ai.prompt_engine import PromptEngine
from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
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

        self._pending_task_id: str | None = None
        self._task_start_time: float = 0.0

        self.preview = WorldPreview(self)
        self.setCentralWidget(self.preview)

        self.library_dock = WorldLibraryDock(self)
        self.properties_dock = WorldPropertiesDock(self)
        self.console_dock = AIConsoleDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.library_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)

        self.properties_dock.generate_btn.clicked.connect(self._generate_background)

        try:
            registry.get(EventBus).subscribe(Event.AI_TASK_COMPLETED, self._on_ai_completed)
            registry.get(EventBus).subscribe(Event.AI_TASK_FAILED, self._on_ai_failed)
        except KeyError:
            logger.debug("BackgroundsWorkspace: EventBus not available during init.")

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30 * 1000)

    def _generate_background(self):
        # Read from the correct WorldPropertiesDock attributes
        env_name    = self.properties_dock.env_name.text().strip()
        style       = self.properties_dock.env_style.currentText()
        lighting    = self.properties_dock.env_lighting.currentText()
        weather     = self.properties_dock.env_weather.currentText()
        season      = self.properties_dock.env_season.currentText()

        # Use PromptEngine template for structured prompt assembly
        location = env_name if env_name else "landscape"
        try:
            tpl = PromptEngine.fill_template(
                "background_exterior_day",
                {"location": location, "weather": weather.lower(), "season": season.lower()},
            )
            positive = tpl["positive"]
            negative = tpl["negative"]
        except Exception:
            positive = (
                f"anime background, {location}, {lighting.lower()} lighting, "
                f"{weather.lower()} weather, {season.lower()} season, "
                f"{style.lower()} style, high detail, no characters"
            )
            negative = "characters, people, low quality, blurry"

        logger.info("BackgroundsWorkspace: Requesting background — %s", positive[:80])

        self._task_start_time = time.time()
        try:
            api = registry.get(ZanimeAIAPI)
            self._pending_task_id = api.generate_background(
                positive, {"negative_prompt": negative, "width": 1344, "height": 768}
            )
        except Exception:
            logger.exception("BackgroundsWorkspace: Failed to queue background generation.")

    def _on_ai_completed(self, data: dict):
        if self._pending_task_id and data.get("id") != self._pending_task_id:
            return
        self._pending_task_id = None

        result = data.get("result", {})
        image_path = result.get("image_path", "") if isinstance(result, dict) else ""

        if image_path:
            self.preview.load_image(image_path)
            self.console_dock.log.append(f"✓ Background generated: {image_path}")

        # Record in AI history
        try:
            elapsed_ms = int((time.time() - self._task_start_time) * 1000)
            registry.get(AIHistoryManager).record(
                task_type="image",
                prompt=self.properties_dock.env_name.text() or "background",
                output_path=image_path,
                model_name="v1-5-pruned-emaonly.ckpt",
                provider="diffusion",
                workspace="Backgrounds",
                duration_ms=elapsed_ms,
                thumbnail_path=image_path,
            )
        except Exception:
            pass

    def _on_ai_failed(self, data: dict):
        if self._pending_task_id and data.get("id") == self._pending_task_id:
            self._pending_task_id = None
            logger.error("BackgroundsWorkspace: AI generation failed: %s", data.get("error"))
            self.console_dock.log.append(f"✗ Generation failed: {data.get('error', 'Unknown')}")

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

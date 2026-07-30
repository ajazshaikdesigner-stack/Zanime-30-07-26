"""
Core AI Manager orchestration logic.
"""

import logging
import threading
import time
from typing import Any

from PySide6.QtCore import QObject, QTimer

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event

from .download_manager import DownloadManager
from .model_manager import ModelManager
from .providers.base import AIBaseProvider
from .providers.diffusers_provider import DiffusersProvider
from .providers.ollama_provider import OllamaProvider
from .providers.piper_provider import PiperProvider
from .providers.whisper_provider import WhisperProvider
from .task_queue import AITaskQueue

logger = logging.getLogger(__name__)


class AIManager(QObject):
    def __init__(self, event_bus: EventBus, config_manager: Any):
        super().__init__()
        self.event_bus = event_bus
        self.config_manager = config_manager

        # Hardware Constraints (RX6500M target)
        self.MAX_VRAM_MB = 3500  # Leave 500MB for OS/UI

        # Sub-managers
        self.model_manager = ModelManager(config_manager)
        self.task_queue = AITaskQueue()
        self.download_manager = DownloadManager()

        # Providers will be lazily loaded
        self.providers: dict[str, AIBaseProvider] = {}
        self.active_provider: str | None = None

        self._is_initialized = False
        self._init_lock = threading.Lock()
        self.last_activity_time = time.time()

        # Idle unloader (checks every 60 seconds)
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.unload_idle_models)
        self.idle_timer.start(60000)

    def initialize(self):
        """Lazily load the AI framework when first requested."""
        with self._init_lock:
            if self._is_initialized:
                return

            logger.info("Initializing AI Framework...")
            from src.core.managers.notification_manager import NotificationManager
            from src.core.services.service_registry import registry

            try:
                nm = registry.get(NotificationManager)
                nm.show_info("Initializing AI Engines...")
            except KeyError:
                pass

            # Initialize providers
            self.providers = {
                "llm": OllamaProvider(),
                "diffusion": DiffusersProvider(),
                "stt": WhisperProvider(),
                "tts": PiperProvider(),
            }

            self._is_initialized = True
            logger.info("AI Framework Initialized.")

    def unload_idle_models(self):
        """Unload active models if idle for more than 5 minutes (300s)."""
        if self.active_provider and (time.time() - self.last_activity_time > 300):
            logger.info(
                f"AI Provider {self.active_provider} has been idle. Unloading to free VRAM."
            )
            self.providers[self.active_provider].unload()
            self.event_bus.publish(Event.AI_MODEL_UNLOADED, self.active_provider)
            self.active_provider = None

    def _enforce_vram_limits(self, incoming_provider_type: str) -> bool:
        """Ensures we unload active models if a new one exceeds constraints."""
        if self.active_provider and self.active_provider != incoming_provider_type:
            logger.warning(
                f"Unloading {self.active_provider} to free VRAM for {incoming_provider_type}"
            )
            self.providers[self.active_provider].unload()
            self.event_bus.publish(Event.AI_MODEL_UNLOADED, self.active_provider)
            self.active_provider = None
        return True

    def execute_task(
        self,
        provider_type: str,
        model_name: str,
        prompt: str,
        params: dict[str, Any],
        priority: int = 0,
    ) -> str:
        """Main entry point for API module to queue jobs."""
        if not self._is_initialized:
            self.initialize()

        self.last_activity_time = time.time()

        if provider_type not in self.providers:
            raise ValueError(f"Unknown provider type: {provider_type}")

        provider = self.providers[provider_type]

        # Check limits and load
        self._enforce_vram_limits(provider_type)
        if not provider.is_loaded:
            if not provider.load(
                model_name, self.config_manager.get_user("ai_settings", {})
            ):
                raise RuntimeError(
                    f"Failed to load model {model_name} for {provider_type}"
                )
            self.active_provider = provider_type
            self.event_bus.publish(Event.AI_MODEL_LOADED, model_name)

        # Queue the job
        task = self.task_queue.queue_job(provider, prompt, params, priority)

        # Connect signals to EventBus
        task.signals.started.connect(
            lambda t_id: self.event_bus.publish(Event.AI_TASK_STARTED, t_id)
        )
        task.signals.progress.connect(
            lambda t_id, p, m: self.event_bus.publish(
                Event.AI_TASK_PROGRESS, {"id": t_id, "progress": p, "msg": m}
            )
        )
        task.signals.finished.connect(
            lambda t_id, res: self.event_bus.publish(
                Event.AI_TASK_COMPLETED, {"id": t_id, "result": res}
            )
        )
        task.signals.error.connect(
            lambda t_id, err: self.event_bus.publish(
                Event.AI_TASK_FAILED, {"id": t_id, "error": err}
            )
        )

        return task.task_id

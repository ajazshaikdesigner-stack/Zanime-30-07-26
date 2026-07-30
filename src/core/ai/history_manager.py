"""
AI History Manager — persists every generation entry per-project.

Storage: <project_temp_dir>/ai_history.json (max 500 entries, FIFO eviction).
Integrates with EventBus: publishes AI_HISTORY_ENTRY_ADDED after each save.
"""

import json
import logging
import os
import threading
import time
from typing import Any

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.models.ai_history_model import AIHistoryEntry, AITaskType

logger = logging.getLogger(__name__)

_MAX_ENTRIES = 500
_HISTORY_FILENAME = "ai_history.json"


class AIHistoryManager:
    """
    Thread-safe per-project AI generation history store.

    Usage:
        history = registry.get(AIHistoryManager)
        history.set_project_dir("/path/to/temp/MyProject")
        entry = history.record(task_type=..., prompt=..., output_path=..., ...)
    """

    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._lock = threading.Lock()
        self._project_dir: str | None = None
        self._entries: list[AIHistoryEntry] = []

    # ------------------------------------------------------------------
    # Project lifecycle
    # ------------------------------------------------------------------

    def set_project_dir(self, project_dir: str) -> None:
        """Point the history manager at a project's temp directory and load existing history."""
        with self._lock:
            self._project_dir = project_dir
            self._entries = []
            self._load()

    def _history_path(self) -> str | None:
        if not self._project_dir:
            return None
        return os.path.join(self._project_dir, _HISTORY_FILENAME)

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def record(
        self,
        task_type: str,
        prompt: str,
        output_path: str,
        model_name: str = "",
        provider: str = "",
        negative_prompt: str = "",
        seed: int = -1,
        settings: dict | None = None,
        workspace: str = "",
        duration_ms: int = 0,
        thumbnail_path: str = "",
        tags: list[str] | None = None,
    ) -> AIHistoryEntry:
        """Record a new generation entry and persist it."""
        entry = AIHistoryEntry(
            task_type        = task_type,
            prompt           = prompt,
            negative_prompt  = negative_prompt,
            seed             = seed,
            model_name       = model_name,
            provider         = provider,
            settings         = settings or {},
            output_path      = output_path,
            thumbnail_path   = thumbnail_path,
            workspace        = workspace,
            duration_ms      = duration_ms,
            tags             = tags or [],
            timestamp        = time.time(),
        )

        with self._lock:
            self._entries.append(entry)
            # FIFO eviction
            if len(self._entries) > _MAX_ENTRIES:
                self._entries = self._entries[-_MAX_ENTRIES:]
            self._save()

        try:
            self._event_bus.publish(Event.AI_HISTORY_ENTRY_ADDED, entry)
        except Exception:
            logger.exception("AIHistoryManager: Failed to publish AI_HISTORY_ENTRY_ADDED.")

        logger.debug(
            "AIHistoryManager: Recorded %s entry (id=%s).", task_type, entry.entry_id
        )
        return entry

    def get_all(self, task_type: str | None = None) -> list[AIHistoryEntry]:
        """Return all entries, optionally filtered by task type."""
        with self._lock:
            if task_type:
                return [e for e in self._entries if e.task_type == task_type]
            return list(self._entries)

    def get_recent(self, limit: int = 20) -> list[AIHistoryEntry]:
        """Return the N most recent entries."""
        with self._lock:
            return list(reversed(self._entries[-limit:]))

    def get_by_id(self, entry_id: str) -> AIHistoryEntry | None:
        with self._lock:
            for e in self._entries:
                if e.entry_id == entry_id:
                    return e
        return None

    def toggle_favorite(self, entry_id: str) -> bool:
        with self._lock:
            for e in self._entries:
                if e.entry_id == entry_id:
                    e.is_favorite = not e.is_favorite
                    self._save()
                    return e.is_favorite
        return False

    def delete(self, entry_id: str) -> bool:
        with self._lock:
            before = len(self._entries)
            self._entries = [e for e in self._entries if e.entry_id != entry_id]
            if len(self._entries) < before:
                self._save()
                return True
        return False

    def clear(self) -> None:
        with self._lock:
            self._entries = []
            self._save()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _save(self) -> None:
        path = self._history_path()
        if not path:
            return
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            data = [e.to_dict() for e in self._entries]
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, path)
        except Exception:
            logger.exception("AIHistoryManager: Failed to save history to %s.", path)

    def _load(self) -> None:
        path = self._history_path()
        if not path or not os.path.isfile(path):
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self._entries = [AIHistoryEntry.from_dict(d) for d in data]
            logger.info(
                "AIHistoryManager: Loaded %d entries from %s.", len(self._entries), path
            )
        except Exception:
            logger.exception("AIHistoryManager: Failed to load history from %s.", path)
            self._entries = []

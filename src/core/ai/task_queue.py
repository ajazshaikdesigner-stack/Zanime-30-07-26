"""
AI Task Queue for running generation jobs in the background via QThreadPool.
"""

import logging
import time
import uuid
from typing import Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

logger = logging.getLogger(__name__)


class AITaskSignals(QObject):
    started = Signal(str)
    progress = Signal(str, int, str)
    finished = Signal(str, dict)
    error = Signal(str, str)


class AITask(QRunnable):
    def __init__(self, task_id: str, provider, prompt: str, params: dict[str, Any]):
        super().__init__()
        self.task_id = task_id
        self.provider = provider
        self.prompt = prompt
        self.params = params
        self.signals = AITaskSignals()
        # Prevent the QRunnable from being auto-deleted by the thread pool
        try:
            self.setAutoDelete(False)
        except Exception:  # noqa: BLE001
            # setAutoDelete may not be available in some PySide bindings; ignore safely
            logger.debug("AITask: setAutoDelete not available in this PySide binding; ignored.")
        self.is_cancelled = False
        self.is_paused = False

    def run(self):
        self._safe_emit(self.signals.started, self.task_id)
        try:
            # Mock long running process with pause/cancel checks
            for i in range(10):
                if self.is_cancelled:
                    raise InterruptedError("Task was cancelled.")
                while self.is_paused:
                    time.sleep(0.5)
                time.sleep(0.2)  # Simulate work
                self._safe_emit(
                    self.signals.progress, self.task_id, (i + 1) * 10, "Processing..."
                )

            result = self.provider.execute(self.prompt, self.params)
            self._safe_emit(self.signals.finished, self.task_id, result)
        except Exception as e:  # noqa: BLE001
            self._safe_emit(self.signals.error, self.task_id, str(e))

    def _safe_emit(self, signal, *args):
        try:
            signal.emit(*args)
        except RuntimeError:
            # Signal source deleted (likely due to app/shutdown); ignore safely
            logger.debug(
                "Signal source deleted for task %s", getattr(self, "task_id", None)
            )
        except Exception:
            logger.exception(
                "Unexpected error emitting signal for task %s",
                getattr(self, "task_id", None),
            )


class AITaskQueue:
    def __init__(self):
        self.thread_pool = QThreadPool.globalInstance()
        self.active_tasks: dict[str, AITask] = {}

    def queue_job(
        self, provider, prompt: str, params: dict[str, Any], priority: int = 0
    ) -> AITask:
        task_id = str(uuid.uuid4())
        task = AITask(task_id, provider, prompt, params)
        self.active_tasks[task_id] = task

        # Ensure we remove completed/errored tasks from the active map to avoid dangling objects
        def _cleanup_finished(tid, *_):
            self.active_tasks.pop(tid, None)

        task.signals.finished.connect(_cleanup_finished)
        task.signals.error.connect(_cleanup_finished)
        self.thread_pool.start(task, priority)
        return task

    def cancel_job(self, task_id: str) -> bool:
        if task_id in self.active_tasks:
            self.active_tasks[task_id].is_cancelled = True
            return True
        return False

    def pause_job(self, task_id: str) -> bool:
        if task_id in self.active_tasks:
            self.active_tasks[task_id].is_paused = True
            return True
        return False

    def resume_job(self, task_id: str) -> bool:
        if task_id in self.active_tasks:
            self.active_tasks[task_id].is_paused = False
            return True
        return False

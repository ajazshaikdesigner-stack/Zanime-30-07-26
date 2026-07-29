"""
AI Task Queue for running generation jobs in the background via QThreadPool.
"""
import logging
import time
import uuid
from typing import Dict, Any, Callable
from PySide6.QtCore import QRunnable, QThreadPool, QObject, Signal

logger = logging.getLogger(__name__)

class AITaskSignals(QObject):
    started = Signal(str)
    progress = Signal(str, int, str)
    finished = Signal(str, dict)
    error = Signal(str, str)

class AITask(QRunnable):
    def __init__(self, task_id: str, provider, prompt: str, params: Dict[str, Any]):
        super().__init__()
        self.task_id = task_id
        self.provider = provider
        self.prompt = prompt
        self.params = params
        self.signals = AITaskSignals()
        self.is_cancelled = False
        self.is_paused = False
        
    def run(self):
        self.signals.started.emit(self.task_id)
        try:
            # Mock long running process with pause/cancel checks
            for i in range(10):
                if self.is_cancelled:
                    raise InterruptedError("Task was cancelled.")
                while self.is_paused:
                    time.sleep(0.5)
                time.sleep(0.2) # Simulate work
                self.signals.progress.emit(self.task_id, (i+1)*10, "Processing...")
                
            result = self.provider.execute(self.prompt, self.params)
            self.signals.finished.emit(self.task_id, result)
        except Exception as e:
            self.signals.error.emit(self.task_id, str(e))

class AITaskQueue:
    def __init__(self):
        self.thread_pool = QThreadPool.globalInstance()
        self.active_tasks: Dict[str, AITask] = {}
        
    def queue_job(self, provider, prompt: str, params: Dict[str, Any], priority: int = 0) -> AITask:
        task_id = str(uuid.uuid4())
        task = AITask(task_id, provider, prompt, params)
        self.active_tasks[task_id] = task
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

"""
Render Manager - Handles asynchronous render queues.
"""

import logging
import time

from PySide6.QtCore import QThread, Signal

from src.models.render_model import RenderJob, RenderStatus

logger = logging.getLogger(__name__)


class RenderWorker(QThread):
    progress = Signal(str, int)  # job_uuid, percentage
    finished = Signal(str, bool)  # job_uuid, success

    def __init__(self, job: RenderJob, parent=None):
        super().__init__(parent)
        self.job = job
        self._is_paused = False
        self._is_cancelled = False

    def run(self):
        logger.info(f"RenderWorker: Starting job {self.job.name}")
        self.job.status = RenderStatus.RENDERING

        # Mock rendering process
        total_frames = 100
        current_frame = self.job.progress

        while current_frame < total_frames:
            if self._is_cancelled:
                self.job.status = RenderStatus.FAILED
                try:
                    self.finished.emit(self.job.uuid, False)
                except RuntimeError:
                    logger.debug(
                        "RenderWorker: Signal source deleted on cancel for %s",
                        self.job.uuid,
                    )
                return

            while self._is_paused:
                time.sleep(0.5)

            time.sleep(0.05)  # Simulate frame render time
            current_frame += 1

            percent = int((current_frame / total_frames) * 100)
            self.job.progress = percent
            try:
                self.progress.emit(self.job.uuid, percent)
            except RuntimeError:
                logger.debug(
                    "RenderWorker: Signal source deleted while emitting progress for %s",
                    self.job.uuid,
                )

        self.job.status = RenderStatus.COMPLETED
        try:
            self.finished.emit(self.job.uuid, True)
        except RuntimeError:
            logger.debug(
                "RenderWorker: Signal source deleted on finish for %s", self.job.uuid
            )

    def pause(self):
        self._is_paused = True
        self.job.status = RenderStatus.PAUSED

    def resume(self):
        self._is_paused = False
        self.job.status = RenderStatus.RENDERING

    def cancel(self):
        self._is_cancelled = True


class RenderManager:
    def __init__(self):
        self.queue = []
        self.active_worker = None

    def add_job(self, job: RenderJob):
        self.queue.append(job)
        self.queue.sort(key=lambda j: j.priority)

    def start_next(self):
        if self.active_worker and self.active_worker.isRunning():
            return

        pending = [j for j in self.queue if j.status == RenderStatus.QUEUED]
        if not pending:
            return

        job = pending[0]
        self.active_worker = RenderWorker(job)
        self.active_worker.start()
        return self.active_worker

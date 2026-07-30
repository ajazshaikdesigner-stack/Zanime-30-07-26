"""
Production Renderer Workspace
"""

import logging

from PySide6.QtCore import Qt

from src.core.sdk.base_workspace import BaseWorkspace
from src.core.services.render_manager import RenderManager
from src.models.render_model import RenderJob
from src.ui.docks.performance_monitor_dock import PerformanceMonitorDock
from src.ui.docks.render_queue_dock import RenderQueueDock
from src.ui.docks.render_settings_dock import RenderSettingsDock
from src.ui.widgets.render_preview import RenderPreview

logger = logging.getLogger(__name__)


class RenderWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Production Renderer", parent)
        self.app = app

        self.render_manager = RenderManager()

        self.preview = RenderPreview(self)
        self.setCentralWidget(self.preview)

        self.queue_dock = RenderQueueDock(self)
        self.settings_dock = RenderSettingsDock(self)
        self.perf_dock = PerformanceMonitorDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.queue_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.settings_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.perf_dock)

        self.settings_dock.queue_btn.clicked.connect(self._on_queue_render)

        self.queue_dock.pause_btn.clicked.connect(self._pause_render)
        self.queue_dock.resume_btn.clicked.connect(self._resume_render)
        self.queue_dock.cancel_btn.clicked.connect(self._cancel_render)

    def _on_queue_render(self):
        job = RenderJob(name=f"Movie_Render_{len(self.render_manager.queue)+1}")
        job.settings.resolution = self.settings_dock.resolution.currentText()
        job.settings.fps = int(self.settings_dock.fps.currentText())
        job.settings.output_format = self.settings_dock.output_format.currentText()

        self.render_manager.add_job(job)
        self.queue_dock.list.addItem(
            f"{job.name} ({job.settings.resolution}, {job.settings.fps}fps) - QUEUED"
        )
        self.perf_dock.log.append(f"Queued Job: {job.name}")

        worker = self.render_manager.start_next()
        if worker:
            worker.progress.connect(self._on_render_progress)
            worker.finished.connect(self._on_render_finished)

    def _on_render_progress(self, uuid, percent):
        self.preview.progress_bar.setValue(percent)
        self.preview.status_lbl.setText(f"Rendering: {percent}%")

    def _on_render_finished(self, uuid, success):
        status_text = "Completed" if success else "Failed/Cancelled"
        self.preview.status_lbl.setText(f"Render {status_text}")
        self.perf_dock.log.append(f"Job {uuid} {status_text}")
        self.render_manager.start_next()

    def _pause_render(self):
        if self.render_manager.active_worker:
            self.render_manager.active_worker.pause()
            self.preview.status_lbl.setText("Rendering Paused")
            self.perf_dock.log.append("Render Paused")

    def _resume_render(self):
        if self.render_manager.active_worker:
            self.render_manager.active_worker.resume()
            self.preview.status_lbl.setText("Rendering Resumed")
            self.perf_dock.log.append("Render Resumed")

    def _cancel_render(self):
        if self.render_manager.active_worker:
            self.render_manager.active_worker.cancel()

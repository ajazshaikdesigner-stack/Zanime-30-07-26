"""
Performance Workspace - The Dashboard.
"""

import logging

from PySide6.QtCore import Qt

from src.core.managers.performance_manager import PerformanceManager
from src.core.sdk.base_workspace import BaseWorkspace
from src.ui.docks.cache_log_dock import CacheLogDock
from src.ui.docks.diagnostics_nav_dock import DiagnosticsNavDock
from src.ui.docks.performance_settings_dock import PerformanceSettingsDock
from src.ui.widgets.live_dashboard_widget import LiveDashboardWidget

logger = logging.getLogger(__name__)


class PerformanceWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Performance Dashboard", parent)
        self.app = app

        self.perf_manager = PerformanceManager()

        self.dashboard = LiveDashboardWidget(self)
        self.setCentralWidget(self.dashboard)

        self.nav_dock = DiagnosticsNavDock(self)
        self.settings_dock = PerformanceSettingsDock(self)
        self.log_dock = CacheLogDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.nav_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.settings_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)

        # Connections
        self.perf_manager.monitor.metrics_updated.connect(self.dashboard.update_metrics)
        self.settings_dock.clear_cache_btn.clicked.connect(self._on_clear_cache)
        self.settings_dock.mode_combo.currentIndexChanged.connect(self._on_mode_changed)

        # Start background loop
        self.perf_manager.start_monitoring()

    def _on_clear_cache(self):
        self.perf_manager.cache.clear()
        self.log_dock.log.append("ACTION: All caches forcefully cleared.")

    def _on_mode_changed(self, index):
        mode = self.settings_dock.mode_combo.currentData()
        self.perf_manager.set_mode(mode)
        self.log_dock.log.append(f"SYS: Switched to {mode.name} mode.")

    def hideEvent(self, event):
        # Stop background polling when tab is hidden to save CPU
        self.perf_manager.stop_monitoring()
        super().hideEvent(event)

    def showEvent(self, event):
        self.perf_manager.start_monitoring()
        super().showEvent(event)

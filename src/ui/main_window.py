"""
Main window using the Workspace Manager and dynamic Docks.
"""

import logging

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QToolBar

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.managers.workspace_manager import WorkspaceManager
from src.core.services.service_registry import registry
from src.ui.docks.asset_browser_dock import AssetBrowserDock
from src.ui.docks.console_dock import ConsoleDock
from src.ui.docks.history_dock import HistoryDock
from src.ui.docks.notification_dock import NotificationDock
from src.ui.docks.preview_dock import PreviewDock
from src.ui.docks.project_explorer_dock import ProjectExplorerDock
from src.ui.docks.ai_copilot_dock import AICopilotDock
from src.ui.docks.ai_history_dock import AIHistoryDock
from src.ui.docks.ai_job_manager_dock import AIJobManagerDock
from src.ui.docks.model_manager_dock import ModelManagerDock
from src.ui.docks.properties_dock import PropertiesDock
from src.ui.docks.timeline_dock import TimelineDock
from src.ui.docks.toolbox_dock import ToolboxDock
from src.ui.widgets.menu_bar import ZanimeMenuBar
from src.ui.widgets.sidebar import ZanimeSidebar
from src.ui.widgets.status_bar import ZanimeStatusBar
from src.ui.widgets.tool_bar import ZanimeToolBar
from src.ui.workspace_factory import WorkspaceFactory

logger = logging.getLogger(__name__)


class ZanimeMainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("✦ ZANIME v2 — Professional 2D Animation Studio")
        self.setMinimumSize(1024, 768)

        # Central Stacked Widget
        self.workspace_stack = QStackedWidget(self)
        self.setCentralWidget(self.workspace_stack)

        self.docks = {}
        self.workspace_factory = WorkspaceFactory(max_cache_size=20)

        self.settings = QSettings("ZanimeStudio", "Zanime_v2")

        self._setup_docks()
        self._setup_events()
        self._restore_window_state()

    def _setup_docks(self):
        # Top
        self.setMenuBar(ZanimeMenuBar(self))
        self.addToolBar(Qt.TopToolBarArea, ZanimeToolBar(self))

        # Bottom
        self.status_bar = ZanimeStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Left
        self.addToolBar(Qt.LeftToolBarArea, ZanimeSidebar(self))

        # Docks
        self.docks["Toolbox"] = ToolboxDock(self)
        self.docks["Properties"] = PropertiesDock(self)
        self.docks["Timeline"] = TimelineDock(self)
        self.docks["ProjectExplorer"] = ProjectExplorerDock(self)
        self.docks["Console"] = ConsoleDock(self)
        self.docks["AssetBrowser"] = AssetBrowserDock(self)
        self.docks["NotificationCenter"] = NotificationDock(self)
        self.docks["History"] = HistoryDock(self)
        self.docks["Preview"] = PreviewDock(self)
        # Phase 3 AI docks
        self.docks["AICopilot"] = AICopilotDock(self)
        self.docks["AIJobs"] = AIJobManagerDock(self)
        self.docks["AIHistory"] = AIHistoryDock(self)
        self.docks["ModelManager"] = ModelManagerDock(self)

        # Specific Dock Areas
        self.addDockWidget(Qt.RightDockWidgetArea, self.docks["Properties"])
        self.addDockWidget(Qt.RightDockWidgetArea, self.docks["ProjectExplorer"])
        self.addDockWidget(Qt.RightDockWidgetArea, self.docks["AssetBrowser"])

        self.addDockWidget(Qt.BottomDockWidgetArea, self.docks["Timeline"])
        self.addDockWidget(Qt.BottomDockWidgetArea, self.docks["NotificationCenter"])
        self.addDockWidget(Qt.BottomDockWidgetArea, self.docks["Console"])

        self.addDockWidget(Qt.LeftDockWidgetArea, self.docks["Toolbox"])
        self.addDockWidget(Qt.LeftDockWidgetArea, self.docks["History"])
        self.addDockWidget(Qt.LeftDockWidgetArea, self.docks["Preview"])
        # Phase 3 AI docks — right panel
        self.addDockWidget(Qt.RightDockWidgetArea, self.docks["AICopilot"])
        self.addDockWidget(Qt.RightDockWidgetArea, self.docks["AIJobs"])
        self.addDockWidget(Qt.RightDockWidgetArea, self.docks["AIHistory"])
        self.addDockWidget(Qt.RightDockWidgetArea, self.docks["ModelManager"])

        for dock in self.docks.values():
            dock.hide()

    def _setup_events(self):
        bus = registry.get(EventBus)
        bus.subscribe(Event.WORKSPACE_CHANGED, self._on_workspace_changed)
        bus.subscribe(Event.WORKSPACE_CHANGED, self._on_workspace_changed_sidebar)
        bus.subscribe(Event.PROJECT_OPENED, self._on_project_opened)

    def _on_project_opened(self, path: str):
        wm = registry.get(WorkspaceManager)
        if wm.active_workspace == "Welcome":
            wm.set_workspace("Home")

    def _restore_window_state(self):
        from PySide6.QtWidgets import QApplication

        geometry = self.settings.value("geometry")
        state = self.settings.value("windowState")

        if geometry:
            self.restoreGeometry(geometry)
            # Guard against off-screen position (e.g. disconnected monitor)
            screen = QApplication.primaryScreen().availableGeometry()
            if not screen.intersects(self.geometry()):
                logger.warning("Window geometry was off-screen; resetting to default.")
                self.resize(1280, 720)
                self.move(
                    screen.center().x() - 640,
                    screen.center().y() - 360,
                )
        else:
            self.resize(1280, 720)

        if state:
            self.restoreState(state)

    def closeEvent(self, event):
        """Unsubscribe from event bus and save state before closing."""
        try:
            bus = registry.get(EventBus)
            bus.unsubscribe(Event.WORKSPACE_CHANGED, self._on_workspace_changed)
            bus.unsubscribe(Event.WORKSPACE_CHANGED, self._on_workspace_changed_sidebar)
            bus.unsubscribe(Event.PROJECT_OPENED, self._on_project_opened)
        except KeyError:
            pass  # Registry already cleared during shutdown

        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

        # Cleanup remaining workspaces
        self.workspace_factory.cleanup_memory(self)
        super().closeEvent(event)

    def _on_workspace_changed_sidebar(self, workspace_name: str):
        """Sync sidebar active button and menu dock checkboxes."""
        # Sync sidebar
        for tb in self.findChildren(QToolBar):
            if hasattr(tb, "set_active"):
                tb.set_active(workspace_name)
                break
        # Sync View menu dock checkboxes
        menu_bar = self.menuBar()
        if hasattr(menu_bar, "dock_actions"):
            for dock_id, action in menu_bar.dock_actions.items():
                if dock_id in self.docks:
                    action.blockSignals(True)
                    action.setChecked(self.docks[dock_id].isVisible())
                    action.blockSignals(False)

    def _on_workspace_changed(self, workspace_name: str):
        try:
            ws_widget = self.workspace_factory.get_workspace(
                workspace_name, self.app, self
            )

            if self.workspace_stack.indexOf(ws_widget) == -1:
                self.workspace_stack.addWidget(ws_widget)

            self.workspace_stack.setCurrentWidget(ws_widget)

            # Status bar telemetry update context
            if hasattr(self, "status_bar"):
                self.status_bar.set_workspace_name(workspace_name)

            # Manage Docks specific to the Editor Framework
            if hasattr(ws_widget, "get_required_docks"):
                req = ws_widget.get_required_docks()
                hid = ws_widget.get_hidden_docks()

                for dock_name in req:
                    if dock_name in self.docks:
                        self.docks[dock_name].show()
                for dock_name in hid:
                    if dock_name in self.docks:
                        self.docks[dock_name].hide()
        except Exception:
            logger.exception(
                "Workspace change failed for '%s'", workspace_name
            )

"""
Props Workspace - Animated objects and prop asset management.
"""

import logging

from PySide6.QtCore import Qt, QTimer

from src.core.sdk.base_workspace import BaseWorkspace
from src.ui.docks.ai_console_dock import AIConsoleDock
from src.ui.docks.asset_categories_dock import AssetCategoriesDock
from src.ui.docks.asset_information_dock import AssetInformationDock
from src.ui.widgets.asset_browser_widget import AssetBrowserWidget

logger = logging.getLogger(__name__)


class PropsWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Props Studio", parent)
        self.app = app

        self.browser_widget = AssetBrowserWidget(self)
        self.setCentralWidget(self.browser_widget)

        self.categories_dock = AssetCategoriesDock(self)
        self.info_dock = AssetInformationDock(self)
        self.console_dock = AIConsoleDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.categories_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.info_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30 * 1000)

    def autosave(self):
        logger.info("PropsWorkspace: Autosaving props inventory...")

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

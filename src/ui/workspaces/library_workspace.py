"""
Content Library Workspace - The ecosystem explorer.
"""

import logging

from PySide6.QtCore import Qt

from src.core.managers.asset_manager import AssetManager
from src.core.sdk.base_workspace import BaseWorkspace
from src.models.asset_model import AssetType
from src.ui.docks.asset_categories_dock import AssetCategoriesDock
from src.ui.docks.asset_information_dock import AssetInformationDock
from src.ui.docks.asset_preview_dock import AssetPreviewDock
from src.ui.widgets.asset_browser_widget import AssetBrowserWidget

logger = logging.getLogger(__name__)


class LibraryWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Content Library", parent)
        self.app = app
        self.asset_manager = AssetManager()

        self.browser = AssetBrowserWidget(self)
        self.setCentralWidget(self.browser)

        self.categories_dock = AssetCategoriesDock(self)
        self.info_dock = AssetInformationDock(self)
        self.preview_dock = AssetPreviewDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.categories_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.info_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.preview_dock)

        # Connections
        self.browser.search_bar.textChanged.connect(self._on_search)
        self.categories_dock.tree.itemClicked.connect(self._on_category_clicked)

        # Initial Load
        self._load_assets()

    def _load_assets(self, query="", asset_type=None):
        results = self.asset_manager.search(query, asset_type, limit=100)
        self.browser.populate(results)

    def _on_search(self, text):
        self._load_assets(query=text)

    def _on_category_clicked(self, item, col):
        text = item.text(0)
        try:
            # Check if it matches an enum
            atype = AssetType(text)
            self._load_assets(asset_type=atype)
        except ValueError:
            # If "Favorites" or others
            if text == "Favorites":
                # Mock favorite filter
                favs = [a for a in self.asset_manager._assets.values() if a.is_favorite]
                self.browser.populate(favs)
            else:
                self._load_assets()

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

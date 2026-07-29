"""
World Library Dock - Tabbed view for Environments and Props.
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QTabWidget, QWidget, QListWidget, QLineEdit, QComboBox, QHBoxLayout

class WorldLibraryDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("World Library", parent)
        
        layout = QVBoxLayout(self.container)
        
        # Tabs
        self.tabs = QTabWidget()
        self._setup_env_tab()
        self._setup_prop_tab()
        
        layout.addWidget(self.tabs)
        
    def _setup_env_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Filters
        f_layout = QHBoxLayout()
        self.env_search = QLineEdit()
        self.env_search.setPlaceholderText("Search envs...")
        self.env_cat = QComboBox()
        self.env_cat.addItems(["All", "Forest", "Village", "City", "School", "Custom"])
        f_layout.addWidget(self.env_search)
        f_layout.addWidget(self.env_cat)
        
        layout.addLayout(f_layout)
        
        # List
        self.env_list = QListWidget()
        layout.addWidget(self.env_list)
        
        self.tabs.addTab(tab, "Environments")
        
    def _setup_prop_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Filters
        f_layout = QHBoxLayout()
        self.prop_search = QLineEdit()
        self.prop_search.setPlaceholderText("Search props...")
        self.prop_cat = QComboBox()
        self.prop_cat.addItems(["All", "Furniture", "Nature", "Vehicles", "Weapons"])
        f_layout.addWidget(self.prop_search)
        f_layout.addWidget(self.prop_cat)
        
        layout.addLayout(f_layout)
        
        # List
        self.prop_list = QListWidget()
        layout.addWidget(self.prop_list)
        
        self.tabs.addTab(tab, "Props")

"""
Performance Settings Dock
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QFormLayout, QComboBox, QPushButton
from src.models.performance_model import PerformanceMode

class PerformanceSettingsDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Settings", parent)
        
        layout = QVBoxLayout(self.container)
        
        form = QFormLayout()
        
        self.mode_combo = QComboBox()
        for mode in PerformanceMode:
            self.mode_combo.addItem(mode.name, userData=mode)
            
        # Default to BALANCED
        self.mode_combo.setCurrentText("BALANCED")
        form.addRow("Mode:", self.mode_combo)
        
        layout.addLayout(form)
        
        self.clear_cache_btn = QPushButton("Clear All Caches (Free Memory)")
        self.clear_cache_btn.setStyleSheet("background-color: #7b2c2c; color: white;")
        layout.addWidget(self.clear_cache_btn)
        
        layout.addStretch()

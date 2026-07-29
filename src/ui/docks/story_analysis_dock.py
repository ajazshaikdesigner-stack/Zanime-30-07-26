"""
Story Analysis Dock for displaying extracted data and validation warnings.
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QLabel, QListWidget

class StoryAnalysisDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Story Analysis", parent)
        
        layout = QVBoxLayout(self.container)
        
        layout.addWidget(QLabel("<b>Validation Warnings</b>"))
        self.warnings_list = QListWidget()
        layout.addWidget(self.warnings_list)
        
        layout.addWidget(QLabel("<b>Characters Found</b>"))
        self.characters_list = QListWidget()
        layout.addWidget(self.characters_list)
        
        layout.addWidget(QLabel("<b>Locations</b>"))
        self.locations_list = QListWidget()
        layout.addWidget(self.locations_list)
        
        layout.addWidget(QLabel("<b>Metadata</b>"))
        self.metadata_lbl = QLabel("Duration: 00:00:00\nRating: G\nKeywords: None")
        layout.addWidget(self.metadata_lbl)
        
    def update_analysis(self, model, warnings):
        self.warnings_list.clear()
        if warnings:
            self.warnings_list.addItems(warnings)
        else:
            self.warnings_list.addItem("✅ All checks passed")
            
        self.characters_list.clear()
        self.characters_list.addItems(model.characters if model.characters else ["None"])
        
        self.locations_list.clear()
        self.locations_list.addItems(model.locations if model.locations else ["None"])
        
        self.metadata_lbl.setText(f"Duration: {model.duration_est}\nRating: {model.rating}\nKeywords: {', '.join(model.keywords)}")

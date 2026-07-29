"""
Tutorial Navigation Dock - Shows the list of learning modules.
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QListWidget
from src.models.tutorial_model import TutorialStep

class TutorialNavigationDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Tutorial Modules", parent)
        
        layout = QVBoxLayout(self.container)
        self.list = QListWidget()
        layout.addWidget(self.list)
        
    def populate(self, steps: list[TutorialStep]):
        self.list.clear()
        for step in steps:
            self.list.addItem(f"Step {step.step_id + 1}: {step.title}")
            
    def set_current_step(self, index: int):
        self.list.setCurrentRow(index)

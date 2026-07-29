"""
Timeline Dock representing shots horizontally.
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QHBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

class StoryboardTimelineDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Timeline", parent)
        
        self.layout = QHBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignLeft)
        
    def render_timeline(self, storyboard_model):
        # Clear
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)
            
        for scene in storyboard_model.scenes:
            for shot in scene.shots:
                width = int(shot.duration * 20) # 20px per second
                lbl = QLabel(f"S{scene.number}:{shot.number}")
                lbl.setStyleSheet("border: 1px solid #777; background-color: #225588; color: white;")
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setFixedSize(width, 40)
                self.layout.addWidget(lbl)

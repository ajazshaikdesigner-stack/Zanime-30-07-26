"""
Storyboard Properties Dock
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import (QVBoxLayout, QStackedWidget, QWidget, QFormLayout, 
                               QLineEdit, QComboBox, QTextEdit, QDoubleSpinBox, QPushButton)

class StoryboardPropertiesDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Properties", parent)
        
        layout = QVBoxLayout(self.container)
        
        self.stack = QStackedWidget()
        self._setup_scene_form()
        self._setup_shot_form()
        
        layout.addWidget(self.stack)
        
        self.generate_btn = QPushButton("AI Generate Selected")
        layout.addWidget(self.generate_btn)
        
    def _setup_scene_form(self):
        self.scene_widget = QWidget()
        form = QFormLayout(self.scene_widget)
        
        self.scene_name = QLineEdit()
        form.addRow("Name:", self.scene_name)
        
        self.scene_desc = QTextEdit()
        self.scene_desc.setMaximumHeight(80)
        form.addRow("Desc:", self.scene_desc)
        
        self.scene_lighting = QComboBox()
        self.scene_lighting.addItems(["Daylight", "Night", "Sunset", "Moody"])
        form.addRow("Lighting:", self.scene_lighting)
        
        self.stack.addWidget(self.scene_widget)
        
    def _setup_shot_form(self):
        self.shot_widget = QWidget()
        form = QFormLayout(self.shot_widget)
        
        self.shot_type = QComboBox()
        self.shot_type.addItems(["Wide", "Medium", "Close Up", "Extreme Close Up", "Over Shoulder", "Tracking", "Pan"])
        form.addRow("Type:", self.shot_type)
        
        self.shot_dur = QDoubleSpinBox()
        self.shot_dur.setRange(0.1, 60.0)
        form.addRow("Duration (s):", self.shot_dur)
        
        self.shot_cam = QComboBox()
        self.shot_cam.addItems(["Static", "Pan", "Tilt", "Zoom", "Crane", "Dolly", "Orbit"])
        form.addRow("Movement:", self.shot_cam)
        
        self.stack.addWidget(self.shot_widget)
        
    def show_scene_properties(self):
        self.stack.setCurrentWidget(self.scene_widget)
        
    def show_shot_properties(self):
        self.stack.setCurrentWidget(self.shot_widget)

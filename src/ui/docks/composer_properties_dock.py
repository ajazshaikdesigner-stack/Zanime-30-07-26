"""
Composer Properties Dock
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QFormLayout, QWidget, QDoubleSpinBox, QComboBox, QLineEdit

class ComposerPropertiesDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Properties", parent)
        
        layout = QVBoxLayout(self.container)
        
        form = QFormLayout()
        
        self.obj_name = QLineEdit()
        form.addRow("Name:", self.obj_name)
        
        self.pos_x = QDoubleSpinBox()
        self.pos_x.setRange(-5000, 5000)
        form.addRow("Pos X:", self.pos_x)
        
        self.pos_y = QDoubleSpinBox()
        self.pos_y.setRange(-5000, 5000)
        form.addRow("Pos Y:", self.pos_y)
        
        self.scale_xy = QDoubleSpinBox()
        self.scale_xy.setRange(0.01, 100.0)
        self.scale_xy.setSingleStep(0.1)
        form.addRow("Scale:", self.scale_xy)
        
        self.rotation = QDoubleSpinBox()
        self.rotation.setRange(-360, 360)
        form.addRow("Rotation:", self.rotation)
        
        self.layer = QComboBox()
        self.layer.addItems(["FAR_BACKGROUND", "BACKGROUND", "CHARACTERS", "FOREGROUND", "UI"])
        form.addRow("Layer:", self.layer)
        
        layout.addLayout(form)
        layout.addStretch()
        
    def load_object(self, obj_model):
        self.obj_name.setText(obj_model.name)
        self.pos_x.setValue(obj_model.x)
        self.pos_y.setValue(obj_model.y)
        self.scale_xy.setValue(obj_model.scale_x)
        self.rotation.setValue(obj_model.rotation)
        self.layer.setCurrentText(obj_model.layer.name)

"""
Animation Properties Dock - Keyframe inspector
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QFormLayout, QWidget, QDoubleSpinBox, QComboBox, QLineEdit, QPushButton

class AnimationPropertiesDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Keyframes", parent)
        
        layout = QVBoxLayout(self.container)
        
        form = QFormLayout()
        
        self.clip_name = QLineEdit()
        form.addRow("Clip Name:", self.clip_name)
        
        self.property_name = QComboBox()
        self.property_name.addItems(["x", "y", "scale_x", "scale_y", "rotation", "opacity"])
        form.addRow("Property:", self.property_name)
        
        self.value = QDoubleSpinBox()
        self.value.setRange(-5000, 5000)
        form.addRow("Value:", self.value)
        
        self.interp = QComboBox()
        self.interp.addItems(["Linear", "Bezier", "Hold"])
        form.addRow("Interpolation:", self.interp)
        
        layout.addLayout(form)
        
        self.generate_btn = QPushButton("Generate AI Animation")
        layout.addWidget(self.generate_btn)
        
        layout.addStretch()
        
    def load_keyframe(self, kf):
        self.property_name.setCurrentText(kf.property_name)
        self.value.setValue(float(kf.value))
        self.interp.setCurrentText(kf.interpolation)

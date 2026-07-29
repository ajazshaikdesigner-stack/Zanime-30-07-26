"""
Render Settings Dock
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QFormLayout, QComboBox, QLineEdit, QPushButton

class RenderSettingsDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Render Settings", parent)
        
        layout = QVBoxLayout(self.container)
        
        form = QFormLayout()
        
        self.resolution = QComboBox()
        self.resolution.addItems(["1080p", "720p", "480p", "1440p", "4K"])
        form.addRow("Resolution:", self.resolution)
        
        self.fps = QComboBox()
        self.fps.addItems(["24", "30", "60"])
        form.addRow("FPS:", self.fps)
        
        self.output_format = QComboBox()
        self.output_format.addItems(["MP4 (H.264)", "MP4 (H.265)", "MOV", "AVI", "PNG Sequence"])
        form.addRow("Format:", self.output_format)
        
        self.quality = QComboBox()
        self.quality.addItems(["High Quality", "Preview", "Standard", "Draft", "Ultra Quality"])
        form.addRow("Quality:", self.quality)
        
        layout.addLayout(form)
        
        self.queue_btn = QPushButton("Add to Render Queue")
        layout.addWidget(self.queue_btn)
        
        layout.addStretch()

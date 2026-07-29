"""
AI Settings Dialog
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QComboBox, QSpinBox, QPushButton, QLineEdit)
from PySide6.QtCore import Qt

class AISettingsDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("AI Framework Settings")
        self.setFixedSize(400, 300)
        
        self._setup_ui()
        self._populate_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.cpu_spin = QSpinBox()
        self.cpu_spin.setRange(1, 64)
        form.addRow("CPU Threads:", self.cpu_spin)
        
        self.vram_spin = QSpinBox()
        self.vram_spin.setRange(512, 24000)
        self.vram_spin.setSuffix(" MB")
        form.addRow("GPU Memory Limit:", self.vram_spin)
        
        self.cache_edit = QLineEdit()
        form.addRow("Cache Location:", self.cache_edit)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["llama3:8b", "llama3:70b", "zanime_sdxl"])
        form.addRow("Default Story Model:", self.model_combo)
        
        layout.addLayout(form)
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self._on_save)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def _populate_data(self):
        ai_settings = self.config_manager.get_user("ai_settings", {})
        self.cpu_spin.setValue(ai_settings.get("cpu_threads", 4))
        self.vram_spin.setValue(ai_settings.get("gpu_limit_mb", 3500)) # Default mapped to RX6500M safely
        self.cache_edit.setText(ai_settings.get("cache_location", "~/.zanime/models"))

    def _on_save(self):
        settings = {
            "cpu_threads": self.cpu_spin.value(),
            "gpu_limit_mb": self.vram_spin.value(),
            "cache_location": self.cache_edit.text()
        }
        self.config_manager.set_user("ai_settings", settings)
        self.accept()

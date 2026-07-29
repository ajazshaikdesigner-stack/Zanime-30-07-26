"""
Main Status Bar component with live telemetry.
"""
import psutil
import os
from PySide6.QtWidgets import QStatusBar, QLabel
from PySide6.QtCore import QTimer
from src.core.events.event_types import Event
from src.core.services.service_registry import registry
from src.core.managers.configuration_manager import ConfigurationManager
from src.core.events.event_bus import EventBus

class ZanimeStatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent.app if hasattr(parent, 'app') else None
        
        self.process = psutil.Process(os.getpid())
        
        # Telemetry Labels
        self.workspace_label = QLabel("Workspace: Welcome")
        self.workspace_label.setStyleSheet("font-weight: bold; padding-right: 15px;")
        
        self.project_label = QLabel("Project: Untitled")
        self.project_label.setStyleSheet("padding-right: 15px;")
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #aaa;")
        
        self.addWidget(self.workspace_label)
        self.addWidget(self.project_label)
        self.addWidget(self.status_label)
        
        # Permanent widgets (Right side)
        self.ai_label = QLabel("AI: Idle")
        self.render_label = QLabel("Render: Idle")
        self.cpu_label = QLabel("CPU: 0%")
        self.ram_label = QLabel("RAM: 0 MB")
        
        for lbl in (self.ai_label, self.render_label, self.cpu_label, self.ram_label):
            lbl.setStyleSheet("padding-left: 10px; color: #888;")
            self.addPermanentWidget(lbl)
            
        version = registry.get(ConfigurationManager).get("version", "1.0.0") if self.app else "1.0.0"
        self.version_label = QLabel(f"v{version}")
        self.version_label.setStyleSheet("padding-left: 15px; color: #666;")
        self.addPermanentWidget(self.version_label)
        
        if self.app:
            registry.get(EventBus).subscribe(Event.PROJECT_SAVED, self._on_saved)
            
        # Telemetry Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_telemetry)
        self.timer.start(2000)

    def set_workspace_name(self, name: str):
        self.workspace_label.setText(f"Workspace: {name}")

    def set_status(self, message: str):
        self.status_label.setText(message)

    def _on_saved(self, path):
        self.set_status(f"Saved: {path}")

    def _update_telemetry(self):
        try:
            cpu = self.process.cpu_percent()
            ram = self.process.memory_info().rss / (1024 * 1024)
            self.cpu_label.setText(f"CPU: {cpu:.1f}%")
            self.ram_label.setText(f"RAM: {ram:.1f} MB")
        except Exception:
            pass

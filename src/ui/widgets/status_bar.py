"""
Premium Status Bar with live telemetry and AI/render badges.
"""

import logging
import os

try:
    import psutil
except ImportError:
    psutil = None

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame, QLabel, QStatusBar

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.managers.configuration_manager import ConfigurationManager
from src.core.services.service_registry import registry

logger = logging.getLogger(__name__)

_STYLE = """
QStatusBar {
    background-color: #0d0f17;
    border-top: 1px solid #1e2235;
    color: #475569;
    font-size: 8pt;
    padding: 0;
    min-height: 26px;
    max-height: 26px;
}
QStatusBar::item { border: none; }

QLabel#SbWorkspace {
    color: #a78bfa;
    font-weight: bold;
    font-size: 8pt;
    padding: 0 12px;
    background: transparent;
}
QLabel#SbProject {
    color: #64748b;
    font-size: 8pt;
    padding: 0 8px;
    background: transparent;
}
QLabel#SbStatus {
    color: #475569;
    font-size: 8pt;
    padding: 0 8px;
    background: transparent;
}
QLabel#SbDot {
    font-size: 8pt;
    padding: 0;
    background: transparent;
}
QLabel#SbBadge {
    color: #475569;
    font-size: 8pt;
    padding: 0 10px;
    background: transparent;
}
QLabel#SbBadgeActive {
    color: #10b981;
    font-size: 8pt;
    padding: 0 10px;
    background: transparent;
    font-weight: bold;
}
QLabel#SbTelemetry {
    color: #334155;
    font-size: 8pt;
    padding: 0 8px;
    background: transparent;
}
QLabel#SbVersion {
    color: #1e293b;
    font-size: 8pt;
    padding: 0 10px;
    background: transparent;
}
QFrame#SbSep {
    color: #1e2235;
    background-color: #1e2235;
}
"""


def _sep():
    f = QFrame()
    f.setObjectName("SbSep")
    f.setFrameShape(QFrame.VLine)
    f.setFixedWidth(1)
    f.setFixedHeight(14)
    return f


class ZanimeStatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent.app if hasattr(parent, "app") else None
        self.setStyleSheet(_STYLE)
        self.setSizeGripEnabled(False)

        try:
            self.process = psutil.Process(os.getpid()) if psutil else None
        except Exception as e:
            logger.debug("Failed to initialize process telemetry: %s", e)
            self.process = None

        # ── Left side labels ──────────────────────────────────────────
        self.workspace_label = QLabel("● Welcome")
        self.workspace_label.setObjectName("SbWorkspace")

        self.project_label = QLabel("No Project")
        self.project_label.setObjectName("SbProject")

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("SbStatus")

        self.addWidget(_sep())
        self.addWidget(self.workspace_label)
        self.addWidget(_sep())
        self.addWidget(self.project_label)
        self.addWidget(_sep())
        self.addWidget(self.status_label)

        # ── Right side permanent badges ──────────────────────────────
        self.ai_label = QLabel("◦ AI: Idle")
        self.ai_label.setObjectName("SbBadge")

        self.render_label = QLabel("◦ Render: Idle")
        self.render_label.setObjectName("SbBadge")

        self.cpu_label = QLabel("CPU: —")
        self.cpu_label.setObjectName("SbTelemetry")

        self.ram_label = QLabel("RAM: —")
        self.ram_label.setObjectName("SbTelemetry")

        version = "2.0.0"
        if self.app:
            try:
                version = registry.get(ConfigurationManager).get("version", "2.0.0")
            except Exception as e:
                logger.debug("Failed to load version: %s", e)
        self.version_label = QLabel(f"v{version}")
        self.version_label.setObjectName("SbVersion")

        for widget in (
            _sep(), self.ai_label,
            _sep(), self.render_label,
            _sep(), self.cpu_label,
            _sep(), self.ram_label,
            _sep(), self.version_label,
        ):
            self.addPermanentWidget(widget)

        # Subscribe to events
        if self.app:
            try:
                bus = registry.get(EventBus)
                bus.subscribe(Event.PROJECT_SAVED, self._on_saved)
                bus.subscribe(Event.APP_STARTED, lambda: self.set_status("Ready"))
            except Exception as e:
                logger.debug("Failed to subscribe to event bus: %s", e)

        # Telemetry timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_telemetry)
        self.timer.start(2000)

    def set_workspace_name(self, name: str):
        self.workspace_label.setText(f"● {name}")

    def set_project_name(self, name: str):
        self.project_label.setText(f"📁 {name}")

    def set_status(self, message: str):
        self.status_label.setText(message)

    def set_ai_status(self, status: str, active: bool = False):
        if active:
            self.ai_label.setText(f"● AI: {status}")
            self.ai_label.setObjectName("SbBadgeActive")
        else:
            self.ai_label.setText(f"◦ AI: {status}")
            self.ai_label.setObjectName("SbBadge")
        self.ai_label.setStyleSheet("")  # force stylesheet re-eval

    def set_render_status(self, status: str, active: bool = False):
        if active:
            self.render_label.setText(f"● Render: {status}")
            self.render_label.setObjectName("SbBadgeActive")
        else:
            self.render_label.setText(f"◦ Render: {status}")
            self.render_label.setObjectName("SbBadge")
        self.render_label.setStyleSheet("")

    def _on_saved(self, path):
        self.set_status("Saved ✓")

    def _update_telemetry(self):
        if not self.process:
            return
        try:
            cpu = self.process.cpu_percent()
            ram = self.process.memory_info().rss / (1024 * 1024)
            self.cpu_label.setText(f"CPU: {cpu:.0f}%")
            self.ram_label.setText(f"RAM: {ram:.0f} MB")
        except Exception as e:
            logger.debug("Telemetry update error: %s", e)

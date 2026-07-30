"""
Application Bootstrapper.
"""

from PySide6.QtWidgets import QApplication

from src.core.managers.startup_manager import StartupManager  # noqa: F401 — kept for SDK compatibility


class ZanimeApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.setApplicationName("ZANIME")
        # Shutdown is orchestrated by ApplicationBootstrap.shutdown()
        # which is connected to aboutToQuit in ApplicationBootstrap.initialize_app()

"""
Application Bootstrapper.
"""

from PySide6.QtWidgets import QApplication

from src.core.managers.startup_manager import StartupManager


class ZanimeApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.setApplicationName("ZANIME")

        self.startup_manager = StartupManager(self)
        self.aboutToQuit.connect(self._cleanup)

    def _cleanup(self):
        import logging

        from PySide6.QtCore import QThreadPool

        from src.core.managers.application_manager import ApplicationManager
        from src.core.managers.cache_manager import CacheManager
        from src.core.services.service_registry import registry

        logger = logging.getLogger(__name__)
        logger.info("Waiting for background tasks to finish...")
        QThreadPool.globalInstance().waitForDone(3000)

        try:
            app_manager = registry.get(ApplicationManager)
            app_manager.shutdown()
        except KeyError:
            pass

        try:
            cache_manager = registry.get(CacheManager)
            cache_manager.clear_cache()
        except KeyError:
            pass

        registry.clear()

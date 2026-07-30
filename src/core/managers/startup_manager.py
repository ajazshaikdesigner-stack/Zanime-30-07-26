"""
Startup Manager for orchestrating application boot sequence.
"""

import logging


class StartupManager:
    """Delegates application orchestration to the dedicated ApplicationBootstrap class."""

    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(__name__)

    def boot(self, splash=None):
        from src.core.bootstrap import ApplicationBootstrap

        bootstrap = ApplicationBootstrap([])
        bootstrap.app = self.app
        return bootstrap.boot(splash)

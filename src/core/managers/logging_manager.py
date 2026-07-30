"""
Logging Manager for domain-specific log streams.
"""

import logging
import os
import sys


class LoggingManager:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self._setup_root_logger()
        self._setup_domain_logger("Renderer", "renderer.log")
        self._setup_domain_logger("AI", "ai.log")
        self._setup_domain_logger("Plugin", "plugin.log")

    def _setup_root_logger(self):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)

        # Standard File Handler (no rotation, no auto log cleanup)
        file_handler = logging.FileHandler(
            os.path.join(self.log_dir, "app.log"),
            encoding="utf-8",
            delay=True,
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        if not logger.handlers:
            logger.addHandler(console)
            logger.addHandler(file_handler)

    def _setup_domain_logger(self, name: str, filename: str):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        # Standard File Handler (no rotation, no auto log cleanup)
        file_handler = logging.FileHandler(
            os.path.join(self.log_dir, filename),
            encoding="utf-8",
            delay=True,
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        if not logger.handlers:
            logger.addHandler(file_handler)

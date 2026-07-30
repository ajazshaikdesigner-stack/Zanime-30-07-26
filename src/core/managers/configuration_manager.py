"""
Configuration Manager handling multiple config domains.
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class ConfigurationManager:
    def __init__(self):
        self.app_config: dict[str, Any] = {}
        self.user_config: dict[str, Any] = {}
        self.workspace_config: dict[str, Any] = {}
        self.project_config: dict[str, Any] = {}

        self.config_dir = "config"
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def get(self, key: str, default: Any = None) -> Any:
        """Resolves configuration in priority order: Project > User > App."""
        if key in self.project_config:
            return self.project_config[key]
        if key in self.user_config:
            return self.user_config[key]
        if key in self.app_config:
            return self.app_config[key]
        return default

    def get_user(self, key: str, default: Any = None) -> Any:
        """Reads directly from user config (bypasses project/app config priority)."""
        return self.user_config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Alias for set_user() — writes to user config and persists to disk."""
        self.set_user(key, value)

    def set_user(self, key: str, value: Any) -> None:
        self.user_config[key] = value
        self.save_user_config()

    def save_user_config(self):
        path = os.path.join(self.config_dir, "user_config.json")
        try:
            with open(path, "w") as f:
                json.dump(self.user_config, f, indent=4)
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to save user config: {e}")

    def load_defaults(self):
        self.app_config = {"version": "1.0.0", "hardware_accel": True}

        user_config_path = os.path.join(self.config_dir, "user_config.json")
        if os.path.exists(user_config_path):
            try:
                with open(user_config_path, "r") as f:
                    self.user_config = json.load(f)
            except Exception as e:  # noqa: BLE001
                logger.error(f"Failed to load user config: {e}")
                self._load_fallback_user_config()
        else:
            self._load_fallback_user_config()

    def _load_fallback_user_config(self):
        self.user_config = {"default_theme": "dark", "recent_projects": []}
        self.save_user_config()

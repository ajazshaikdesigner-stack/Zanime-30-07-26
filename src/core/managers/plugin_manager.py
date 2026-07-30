"""
Plugin Manager for extending ZANIME functionality.
"""

import ast
import importlib
import json
import logging
import os
import sys

from src.core.managers.configuration_manager import ConfigurationManager

logger = logging.getLogger(__name__)


class PluginManager:
    def __init__(
        self, config_manager: ConfigurationManager, plugin_dir: str = "plugins"
    ):
        self.config_manager = config_manager
        self.plugin_dir = plugin_dir
        self.loaded_plugins = {}

        self.report = {
            "discovered": [],
            "validated": [],
            "enabled": [],
            "loaded": [],
            "errors": {},
        }

        if self.plugin_dir not in sys.path:
            sys.path.insert(0, self.plugin_dir)

    def discover_and_load(self):
        """Executes the full plugin lifecycle safely."""
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)

        logger.info(f"PluginManager: Scanning {self.plugin_dir}")

        # 1. Discover Plugins
        discovered_files = self._discover_plugins()

        for filename in discovered_files:
            module_name = filename[:-3]
            self.report["discovered"].append(module_name)

            # 2 & 3. Validate & Read Metadata
            metadata = self._validate_and_read_metadata(module_name, filename)
            if metadata is None:
                continue

            self.report["validated"].append(module_name)

            # 4. Enable Approved Plugins
            if not self._check_enabled(module_name):
                logger.info(f"Plugin {module_name} is disabled. Bypassing load.")
                continue

            self.report["enabled"].append(module_name)

            # 5. Load Enabled Plugins
            self._load_plugin(module_name)

    def _discover_plugins(self) -> list:
        discovered = []
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                discovered.append(filename)
        return discovered

    def _validate_and_read_metadata(self, module_name: str, filename: str) -> dict:
        filepath = os.path.join(self.plugin_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()

            # Safely parse AST to prevent arbitrary code execution
            tree = ast.parse(source)
            metadata = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if (
                            isinstance(target, ast.Name)
                            and target.id == "PLUGIN_METADATA"
                        ):
                            if isinstance(node.value, ast.Dict):
                                metadata = ast.literal_eval(node.value)
                                break
            # Returning an empty dict is fine if no metadata exists, it just means it passed structural validation.
            return metadata
        except SyntaxError as e:
            self._report_error(module_name, f"SyntaxError: {e}")
            return None
        except Exception as e:
            self._report_error(module_name, f"ValidationError: {e}")
            return None

    def _check_enabled(self, module_name: str) -> bool:
        enabled_plugins = self.config_manager.get_user("enabled_plugins", {})
        return enabled_plugins.get(module_name, True)

    def _load_plugin(self, module_name: str):
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "initialize"):
                module.initialize()
                self.loaded_plugins[module_name] = module
                self.report["loaded"].append(module_name)
                logger.info(f"Successfully loaded plugin: {module_name}")
            else:
                self._report_error(module_name, "Missing initialize() function")
        except Exception as e:
            self._report_error(module_name, f"Crash during load: {e}")

    def _report_error(self, module_name: str, reason: str):
        logger.error(f"Plugin Error [{module_name}]: {reason}")
        self.report["errors"][module_name] = reason

    def generate_report(self):
        """Dumps a plugin loading report to disk and logs."""
        report_str = json.dumps(self.report, indent=4)
        logger.info(f"--- Plugin Lifecycle Report ---\n{report_str}")

        # Ensure log directory exists
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        with open(os.path.join(log_dir, "plugin_report.json"), "w") as f:
            f.write(report_str)

"""
Startup Manager for orchestrating application boot sequence.
"""

import logging
import os

from src.core.ai import AIManager, ZanimeAIAPI
from src.core.events.event_bus import EventBus
from src.core.managers.application_manager import ApplicationManager
from src.core.managers.asset_manager import AssetManager
from src.core.managers.cache_manager import CacheManager
from src.core.managers.command_manager import CommandManager
from src.core.managers.configuration_manager import ConfigurationManager
from src.core.managers.layout_manager import LayoutManager
from src.core.managers.logging_manager import LoggingManager
from src.core.managers.plugin_manager import PluginManager
from src.core.managers.project_manager import ProjectManager
from src.core.managers.shortcut_manager import ShortcutManager
from src.core.managers.theme_engine import ThemeEngine
from src.core.managers.window_manager import WindowManager
from src.core.managers.workspace_manager import WorkspaceManager


class StartupManager:
    """Orchestrates initialization of all managers to decouple boot from the Application instance."""

    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(__name__)

    def boot(self, splash=None):
        def update_splash(val, msg):
            if splash:
                splash.update_progress(val, msg)

        from src.core.services.service_registry import registry

        update_splash(10, "Running health checks...")
        import sys

        from PySide6.QtWidgets import QMessageBox

        from src.core.managers.health_check_manager import HealthCheckManager

        health_manager = HealthCheckManager()
        while True:
            report = health_manager.run_all_checks()
            # Allow automated environments to bypass the interactive health-check dialog
            # by setting the environment variable `ZANIME_AUTO_CONTINUE_HEALTH=1`.
            if os.environ.get("ZANIME_AUTO_CONTINUE_HEALTH") == "1":
                if report["status"] != "pass":
                    self.logger.warning(
                        "Auto-continue enabled: proceeding despite health check status '%s'",
                        report["status"],
                    )
                break

            if report["status"] == "pass":
                break

            msg = "Health Check Issues Found:\n\n"
            if report["errors"]:
                msg += (
                    "ERRORS:\n" + "\n".join(f"- {e}" for e in report["errors"]) + "\n\n"
                )
            if report["warnings"]:
                msg += "WARNINGS:\n" + "\n".join(f"- {w}" for w in report["warnings"])

            box = QMessageBox()
            box.setWindowTitle("ZANIME Health Check")
            box.setText(msg)
            box.setIcon(
                QMessageBox.Critical if report["errors"] else QMessageBox.Warning
            )

            box.addButton("Retry", QMessageBox.ActionRole)
            btn_exit = box.addButton("Exit", QMessageBox.RejectRole)
            btn_continue = None
            if not report["errors"]:  # Only allow continue if there are no hard errors
                btn_continue = box.addButton("Continue Anyway", QMessageBox.AcceptRole)

            box.exec()

            if box.clickedButton() == btn_exit:
                sys.exit(1)
            elif btn_continue and box.clickedButton() == btn_continue:
                break

        update_splash(20, "Initializing Logger...")
        registry.register(LoggingManager, LoggingManager())

        update_splash(30, "Loading Configuration...")
        config = ConfigurationManager()
        config.load_defaults()
        registry.register(ConfigurationManager, config)

        update_splash(40, "Loading Theme...")
        theme = ThemeEngine(config, self.app)
        theme.apply_theme()
        registry.register(ThemeEngine, theme)

        update_splash(45, "Initializing Event Bus...")
        event_bus = EventBus()
        registry.register(EventBus, event_bus)

        from src.core.managers.notification_manager import NotificationManager

        registry.register(NotificationManager, NotificationManager(event_bus))

        update_splash(50, "Loading Assets...")
        registry.register(CacheManager, CacheManager())
        registry.register(AssetManager, AssetManager())

        update_splash(55, "Loading Project Manager...")
        registry.register(ProjectManager, ProjectManager(event_bus))

        update_splash(60, "Loading Workspace Manager...")
        layout_manager = LayoutManager(config, None)
        registry.register(LayoutManager, layout_manager)
        registry.register(WorkspaceManager, WorkspaceManager(event_bus, layout_manager))
        registry.register(CommandManager, CommandManager(event_bus))
        registry.register(ShortcutManager, ShortcutManager(event_bus, config))

        update_splash(70, "Loading Plugins...")
        plugin_manager = PluginManager(config)
        plugin_manager.discover_and_load()
        plugin_manager.generate_report()
        registry.register(PluginManager, plugin_manager)

        update_splash(80, "Registering AI Framework...")
        registry.register_factory(
            AIManager,
            lambda: AIManager(
                registry.get(EventBus), registry.get(ConfigurationManager)
            ),
        )
        registry.register_factory(
            ZanimeAIAPI, lambda: ZanimeAIAPI(registry.get(AIManager))
        )
        registry.register(ApplicationManager, ApplicationManager(event_bus))

        update_splash(90, "Initializing Main Window...")
        from src.ui.main_window import ZanimeMainWindow

        window_manager = WindowManager(self.app)
        registry.register(WindowManager, window_manager)

        main_window = ZanimeMainWindow(self.app)
        window_manager.set_main_window(main_window)
        layout_manager.main_window = main_window
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()

        if splash:
            splash.finish(main_window)

        # Route to Welcome screen
        registry.get(WorkspaceManager).set_workspace("Welcome")

        update_splash(100, "Starting...")

        return main_window

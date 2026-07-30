"""
Dedicated Application Bootstrap Class for orchestrating ZANIME initialization, manager registration, and teardown.
"""

import logging
import os

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QMessageBox

from src.core.events.event_bus import EventBus
from src.core.managers.application_manager import ApplicationManager
from src.core.managers.asset_manager import AssetManager
from src.core.managers.cache_manager import CacheManager
from src.core.managers.command_manager import CommandManager
from src.core.managers.configuration_manager import ConfigurationManager
from src.core.managers.demo_manager import DemoProjectManager
from src.core.managers.health_check_manager import HealthCheckManager
from src.core.managers.layout_manager import LayoutManager
from src.core.managers.logging_manager import LoggingManager
from src.core.managers.notification_manager import NotificationManager
from src.core.managers.plugin_manager import PluginManager
from src.core.managers.project_manager import ProjectManager
from src.core.managers.shortcut_manager import ShortcutManager
from src.core.managers.selection_manager import SelectionManager
from src.core.managers.theme_engine import ThemeEngine
from src.core.managers.window_manager import WindowManager
from src.core.managers.workspace_manager import WorkspaceManager
from src.core.services.service_registry import registry
from src.ui.splash_screen import SplashScreen

logger = logging.getLogger(__name__)


class ApplicationBootstrap:
    """Dedicated orchestration class for application boot, service initialization, and teardown."""

    def __init__(self, sys_argv: list[str]):
        self.sys_argv = sys_argv
        self.app = None
        self.splash: SplashScreen | None = None

    def initialize_app(self):
        """Instantiates QApplication instance and connects teardown hooks."""
        from src.app import ZanimeApp

        app = ZanimeApp(self.sys_argv)
        self.app = app
        app.aboutToQuit.connect(self.shutdown)
        return app

    def boot(self, splash: SplashScreen | None = None):
        """Executes full application bootstrap sequence and returns main window."""
        if not self.app:
            self.initialize_app()

        self.splash = splash

        def update_splash(val: int, msg: str):
            if self.splash:
                self.splash.update_progress(val, msg)

        update_splash(10, "Running health checks...")
        health_manager = HealthCheckManager()
        registry.register(HealthCheckManager, health_manager)

        fatal_report = health_manager.run_fatal_checks()
        if fatal_report["status"] == "fail":
            msg = "Fatal Pre-Boot Failures:\n\n" + "\n".join(
                f"- {e}" for e in fatal_report["errors"]
            )
            box = QMessageBox()
            box.setWindowTitle("ZANIME Fatal Launch Failure")
            box.setText(msg)
            box.setIcon(QMessageBox.Critical)
            box.exec()
            import sys
            sys.exit(1)

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

        # Launch background health check
        health_manager.start_background_check(event_bus=event_bus)

        registry.register(NotificationManager, NotificationManager(event_bus))

        update_splash(50, "Loading Assets...")
        registry.register(CacheManager, CacheManager())
        registry.register(AssetManager, AssetManager())

        update_splash(55, "Loading Project Manager...")
        project_mgr = ProjectManager(event_bus)
        registry.register(ProjectManager, project_mgr)

        demo_path = DemoProjectManager.ensure_demo_project()

        recents = config.get("recent_projects", [])
        valid_recents = [p for p in recents if os.path.exists(p)]

        opened_auto_demo = False
        if not valid_recents:
            project_mgr.register_recent_project(demo_path)
            logger.info(
                "No recent project found. Automatically opening demo project: %s",
                demo_path,
            )
            project_mgr.open_project(demo_path)
            opened_auto_demo = True

        update_splash(60, "Loading Workspace Manager...")
        layout_manager = LayoutManager(config, None)
        registry.register(LayoutManager, layout_manager)
        registry.register(WorkspaceManager, WorkspaceManager(event_bus, layout_manager))
        registry.register(CommandManager, CommandManager(event_bus))
        registry.register(SelectionManager, SelectionManager(event_bus))
        
        shortcut_manager = ShortcutManager(event_bus, config)
        registry.register(ShortcutManager, shortcut_manager)
        
        # Register core global shortcuts
        shortcut_manager.register("undo", "Ctrl+Z", registry.get(CommandManager).undo)
        shortcut_manager.register("redo", "Ctrl+Y", registry.get(CommandManager).redo)

        update_splash(70, "Loading Plugins...")
        plugin_manager = PluginManager(config)
        plugin_manager.discover_and_load()
        plugin_manager.generate_report()
        registry.register(PluginManager, plugin_manager)

        update_splash(80, "Registering AI Framework...")
        from src.core.ai import AIManager, ZanimeAIAPI
        from src.core.ai.history_manager import AIHistoryManager
        from src.core.ai.consistency_manager import ConsistencyManager

        registry.register_factory(
            AIManager,
            lambda: AIManager(
                registry.get(EventBus), registry.get(ConfigurationManager)
            ),
        )
        registry.register_factory(
            ZanimeAIAPI, lambda: ZanimeAIAPI(registry.get(AIManager))
        )

        ai_history = AIHistoryManager(event_bus)
        registry.register(AIHistoryManager, ai_history)

        consistency = ConsistencyManager()
        registry.register(ConsistencyManager, consistency)

        app_mgr = ApplicationManager(event_bus)
        registry.register(ApplicationManager, app_mgr)

        update_splash(90, "Initializing Main Window...")
        from src.ui.main_window import ZanimeMainWindow

        window_manager = WindowManager(self.app)
        registry.register(WindowManager, window_manager)

        main_window = ZanimeMainWindow(self.app)
        window_manager.set_main_window(main_window)
        layout_manager.main_window = main_window
        registry.get(ShortcutManager).set_main_window(main_window)
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()

        if self.splash:
            self.splash.finish(main_window)

        if opened_auto_demo or project_mgr.current_project_path:
            registry.get(WorkspaceManager).set_workspace("Home", force=True)
        else:
            registry.get(WorkspaceManager).set_workspace("Welcome", force=True)

        update_splash(100, "Starting...")
        app_mgr.startup()

        return main_window

    def shutdown(self):
        """Clean teardown orchestration on application exit."""
        logger.info("ApplicationBootstrap: Orchestrating application shutdown...")
        QThreadPool.globalInstance().waitForDone(3000)

        try:
            app_manager = registry.get(ApplicationManager)
            app_manager.shutdown()
        except KeyError:
            logger.debug("ApplicationManager not found during shutdown")
        except Exception as e:  # noqa: BLE001
            logger.warning("Error shutting down ApplicationManager: %s", e)

        try:
            cache_manager = registry.get(CacheManager)
            cache_manager.clear_cache()
        except KeyError:
            logger.debug("CacheManager not found during shutdown")
        except Exception as e:  # noqa: BLE001
            logger.warning("Error clearing cache: %s", e)

        registry.clear()

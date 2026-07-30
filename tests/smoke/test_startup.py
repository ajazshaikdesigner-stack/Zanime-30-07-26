"""
Smoke tests for application initialization (V2).
"""

from src.ui.splash_screen import SplashScreen
from src.ui.welcome_screen import WelcomeScreen


def test_splash_screen_init(qapp):
    """Verifies that the splash screen initializes without crashing."""
    splash = SplashScreen()
    assert splash is not None


def test_welcome_screen_init(qapp):
    """Verifies that the welcome screen initializes."""
    from src.core.services.service_registry import registry

    registry.clear()

    from src.core.events.event_bus import EventBus
    from src.core.managers.configuration_manager import ConfigurationManager
    from src.core.managers.notification_manager import NotificationManager
    from src.core.managers.project_manager import ProjectManager

    event_bus = EventBus()
    registry.register(EventBus, event_bus)
    registry.register(ConfigurationManager, ConfigurationManager())
    registry.register(ProjectManager, ProjectManager(event_bus))
    # NotificationManager signature may differ in production; attempt to instantiate with event_bus first,
    # falling back to parameterless construction when necessary.
    try:
        registry.register(NotificationManager, NotificationManager(event_bus))
    except TypeError:
        registry.register(NotificationManager, NotificationManager())

    class MockApp:
        pass

    mock_app = MockApp()
    welcome = WelcomeScreen(mock_app)
    assert welcome is not None

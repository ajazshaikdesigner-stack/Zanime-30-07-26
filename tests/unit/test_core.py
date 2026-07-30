"""
Unit tests for core managers (V2).
"""

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.managers.workspace_manager import WorkspaceManager


def test_event_bus_subscription():
    bus = EventBus()
    received = []

    def callback(val):
        received.append(val)

    bus.subscribe(Event.WORKSPACE_CHANGED, callback)
    bus.publish(Event.WORKSPACE_CHANGED, "Story")

    assert len(received) == 1
    assert received[0] == "Story"


def test_workspace_manager():
    bus = EventBus()
    from src.core.managers.configuration_manager import ConfigurationManager
    from src.core.managers.layout_manager import LayoutManager

    cm = ConfigurationManager()
    lm = LayoutManager(cm, None)
    wm = WorkspaceManager(bus, lm)

    assert wm.active_workspace == "Welcome"

    wm.set_workspace("Animation")
    assert wm.active_workspace == "Animation"


def test_project_manager_structure(tmp_path, qapp):
    import os

    from src.core.managers.project_manager import ProjectManager

    bus = EventBus()
    pm = ProjectManager(bus)

    # Mock temp_dir to use pytest tmp_path
    pm.temp_dir = str(tmp_path)

    project_path = os.path.join(tmp_path, "test_proj.zanime")
    pm.create_project("test_proj", project_path)

    extract_path = os.path.join(pm.temp_dir, "test_proj")

    assert os.path.exists(os.path.join(extract_path, "assets"))
    assert os.path.exists(os.path.join(extract_path, "story"))
    assert os.path.exists(os.path.join(extract_path, "cache"))
    assert os.path.exists(os.path.join(extract_path, "autosave"))


def test_project_manager_autosave(tmp_path, qapp):
    import os

    from src.core.managers.project_manager import ProjectManager

    bus = EventBus()
    pm = ProjectManager(bus)
    pm.temp_dir = str(tmp_path)

    project_path = os.path.join(tmp_path, "test_proj_2.zanime")
    pm.create_project("test_proj_2", project_path)

    # Manually trigger autosave
    pm.autosave()

    extract_path = os.path.join(pm.temp_dir, "test_proj_2")
    autosave_path = os.path.join(extract_path, "autosave", "project_autosave.json")

    assert os.path.exists(autosave_path)

import pytest
from unittest.mock import MagicMock
from src.ui.workspace_factory import WorkspaceFactory

class MockWorkspace:
    def __init__(self, app, parent=None):
        self.app = app
        self.parent = parent
        self.state = None
        
    def deleteLater(self):
        pass

    def save_state(self):
        return {"saved": True}
        
    def restore_state(self, state):
        self.state = state

def get_factory():
    factory = WorkspaceFactory(max_cache_size=3)
    for key in factory._registry:
        factory._registry[key] = MockWorkspace
    return factory

def test_workspace_factory_lazy_init():
    factory = get_factory()
    app_mock = MagicMock()
    main_mock = MagicMock()
    main_mock.workspace_stack = MagicMock()
    
    assert len(factory._cache) == 0
    
    ws = factory.get_workspace("Welcome", app_mock, main_window=main_mock)
    assert len(factory._cache) == 1
    assert "Welcome" in factory._cache
    
    ws2 = factory.get_workspace("Welcome", app_mock, main_window=main_mock)
    assert ws is ws2
    assert len(factory._cache) == 1

def test_workspace_factory_cache_limits():
    factory = get_factory()
    app_mock = MagicMock()
    main_mock = MagicMock()
    main_mock.workspace_stack = MagicMock()
    
    factory.get_workspace("Story", app_mock, main_window=main_mock)
    factory.get_workspace("Script", app_mock, main_window=main_mock)
    factory.get_workspace("Animation", app_mock, main_window=main_mock)
    
    assert len(factory._cache) == 3
    
    factory.get_workspace("Music", app_mock, main_window=main_mock)
    
    assert len(factory._cache) == 3
    assert "Music" in factory._cache
    assert "Script" in factory._cache
    assert "Animation" in factory._cache
    assert "Story" not in factory._cache 
    
    main_mock.workspace_stack.removeWidget.assert_called()

def test_workspace_factory_state_restore():
    factory = get_factory()
    app_mock = MagicMock()
    main_mock = MagicMock()
    main_mock.workspace_stack = MagicMock()
    
    ws1 = factory.get_workspace("Story", app_mock, main_window=main_mock)
    assert ws1.state is None
    
    factory.destroy_workspace("Story", main_mock)
    assert "Story" not in factory._cache
    assert "Story" in factory._state_cache
    
    ws2 = factory.get_workspace("Story", app_mock, main_window=main_mock)
    assert ws2 is not ws1
    assert ws2.state == {"saved": True}

def test_workspace_factory_cleanup_memory():
    factory = get_factory()
    app_mock = MagicMock()
    main_mock = MagicMock()
    main_mock.workspace_stack = MagicMock()
    
    factory.get_workspace("Story", app_mock, main_window=main_mock)
    factory.get_workspace("Script", app_mock, main_window=main_mock)
    
    factory.cleanup_memory(main_mock, active_workspace_name="Script")
    
    assert len(factory._cache) == 1
    assert "Script" in factory._cache
    assert "Story" not in factory._cache

def test_workspace_factory_invalid_workspace():
    factory = get_factory()
    with pytest.raises(ValueError):
        factory.get_workspace("InvalidWorkspaceName", None, None)

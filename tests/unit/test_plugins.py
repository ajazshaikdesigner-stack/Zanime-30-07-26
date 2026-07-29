import os
import shutil
import pytest
from unittest.mock import MagicMock
from src.core.managers.plugin_manager import PluginManager

@pytest.fixture
def mock_plugin_env(tmp_path):
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    
    # 1. Valid Plugin
    valid_plugin = plugin_dir / "valid_plugin.py"
    valid_plugin.write_text('''
PLUGIN_METADATA = {"name": "Valid Plugin", "version": "1.0"}
def initialize():
    pass
''', encoding="utf-8")
    
    # 2. Syntax Error Plugin
    syntax_plugin = plugin_dir / "syntax_plugin.py"
    syntax_plugin.write_text('''
PLUGIN_METADATA = {"name": "Syntax"}
def initialize()
    pass # Missing colon
''', encoding="utf-8")

    # 3. Crash Plugin
    crash_plugin = plugin_dir / "crash_plugin.py"
    crash_plugin.write_text('''
PLUGIN_METADATA = {"name": "Crash"}
def initialize():
    raise RuntimeError("Intentional crash")
''', encoding="utf-8")

    # 4. Disabled Plugin
    disabled_plugin = plugin_dir / "disabled_plugin.py"
    disabled_plugin.write_text('''
PLUGIN_METADATA = {"name": "Disabled"}
def initialize():
    pass
''', encoding="utf-8")

    # Mock Config
    config_mock = MagicMock()
    config_mock.get_user.return_value = {
        "disabled_plugin": False
    }

    return str(plugin_dir), config_mock

def test_plugin_lifecycle(mock_plugin_env):
    plugin_dir, config_mock = mock_plugin_env
    
    manager = PluginManager(config_mock, plugin_dir=plugin_dir)
    manager.discover_and_load()
    
    # Generate report
    manager.generate_report()
    
    report = manager.report
    
    assert "valid_plugin" in report["discovered"]
    assert "syntax_plugin" in report["discovered"]
    assert "crash_plugin" in report["discovered"]
    assert "disabled_plugin" in report["discovered"]
    
    # Syntax plugin should NOT be in validated
    assert "valid_plugin" in report["validated"]
    assert "crash_plugin" in report["validated"]
    assert "disabled_plugin" in report["validated"]
    assert "syntax_plugin" not in report["validated"]
    assert "SyntaxError" in report["errors"]["syntax_plugin"]
    
    # Disabled plugin should NOT be in enabled
    assert "valid_plugin" in report["enabled"]
    assert "crash_plugin" in report["enabled"]
    assert "disabled_plugin" not in report["enabled"]
    
    # Crash plugin should NOT be in loaded
    assert "valid_plugin" in report["loaded"]
    assert "crash_plugin" not in report["loaded"]
    assert "Crash during load" in report["errors"]["crash_plugin"]
    
    # Check that report JSON exists
    assert os.path.exists(os.path.join("logs", "plugin_report.json"))

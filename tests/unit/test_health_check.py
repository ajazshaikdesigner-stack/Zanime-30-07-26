import os
import shutil
import sys
from unittest.mock import patch

import pytest

from src.core.managers.health_check_manager import HealthCheckManager


@pytest.fixture
def health_manager():
    return HealthCheckManager()


def test_health_check_pass(health_manager, tmp_path, monkeypatch):
    # Mock everything to pass
    monkeypatch.setattr(sys, "version_info", (3, 11, 0))
    monkeypatch.setattr(shutil, "which", lambda x: "/usr/bin/ffmpeg")

    # Run in tmp_path so directories can be created successfully
    os.chdir(tmp_path)

    report = health_manager.run_all_checks()

    assert report["status"] == "pass"
    assert not report["errors"]
    assert not report["warnings"]

    # Verify directories were created
    assert os.path.exists("config")
    assert os.path.exists("logs")


def test_health_check_fail_python(health_manager, monkeypatch):
    monkeypatch.setattr(sys, "version_info", (3, 8, 0))

    report = health_manager.run_all_checks()
    assert report["status"] == "fail"
    assert any("Python version must be >=" in e for e in report["errors"])


def test_health_check_fail_ffmpeg(health_manager, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda x: None)

    report = health_manager.run_all_checks()
    assert report["status"] == "fail"
    assert any("FFmpeg is not installed" in e for e in report["errors"])


def test_health_check_plugin_warning(health_manager, tmp_path):
    os.chdir(tmp_path)
    os.makedirs("plugins", exist_ok=True)
    with open("plugins/bad_plugin.py", "w") as f:
        f.write("def initialize()\n    pass # Syntax Error")

    # Mock to pass other checks
    with patch("sys.version_info", (3, 11, 0)), patch(
        "shutil.which", return_value="ffmpeg"
    ):
        report = health_manager.run_all_checks()

    assert report["status"] == "warn"
    assert not report["errors"]
    assert any("Plugin syntax error" in w for w in report["warnings"])

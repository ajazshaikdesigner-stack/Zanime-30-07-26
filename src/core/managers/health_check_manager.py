"""
Pre-boot environment validation system.
"""

import ast
import json
import logging
import os
import shutil
import sys

from PySide6.QtCore import QObject, QThread, Signal

from src.core.events.event_types import Event

logger = logging.getLogger(__name__)


class HealthCheckWorker(QThread):
    finished_report = Signal(dict)

    def __init__(self, health_manager, parent=None):
        super().__init__(parent)
        self.health_manager = health_manager

    def run(self):
        report = self.health_manager.run_all_checks()
        try:
            self.finished_report.emit(report)
        except RuntimeError:
            logger.debug("HealthCheckWorker: Signal target deleted before emit")


class HealthCheckManager(QObject):
    report_completed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker: HealthCheckWorker | None = None

    def run_fatal_checks(self) -> dict:
        """Fast pre-boot check strictly reserved for fatal launch failures."""
        report = {"status": "pass", "errors": [], "warnings": []}
        self._check_python_version(report)
        self._check_write_permissions(report)
        if report["errors"]:
            report["status"] = "fail"
        return report

    def run_all_checks(self) -> dict:
        """Runs all health checks and returns a summary report."""
        report = {"status": "pass", "errors": [], "warnings": []}

        self._check_python_version(report)
        self._check_ffmpeg(report)
        self._check_directories(report)
        self._check_write_permissions(report)
        self._check_plugin_integrity(report)

        if report["errors"]:
            report["status"] = "fail"
        elif report["warnings"]:
            report["status"] = "warn"

        self._generate_report(report)
        return report

    def start_background_check(
        self, event_bus=None, notification_manager=None
    ) -> None:
        """Runs health checks asynchronously in a background thread."""
        self._worker = HealthCheckWorker(self)

        def _on_finished(report: dict):
            logger.info(
                "Background health check finished with status '%s'", report["status"]
            )
            self.report_completed.emit(report)
            if event_bus:
                event_bus.publish(Event.HEALTH_CHECK_COMPLETED, report)
            if notification_manager and report.get("warnings"):
                for w in report["warnings"]:
                    notification_manager.show_warning(f"Health Warning: {w}")

        self._worker.finished_report.connect(_on_finished)
        self._worker.start()

    def _check_python_version(self, report):
        if sys.version_info < (3, 9):
            report["errors"].append(
                f"Python version must be >= 3.9 (Found {sys.version_info[0]}.{sys.version_info[1]})"
            )

    def _check_ffmpeg(self, report):
        if not shutil.which("ffmpeg"):
            report["warnings"].append(
                "FFmpeg is not installed or not in PATH. Video/audio export features will be disabled."
            )

    def _check_directories(self, report):
        dirs = ["config", "assets", "cache", "projects", "logs", "models", "plugins"]
        for d in dirs:
            if not os.path.exists(d):
                try:
                    os.makedirs(d)
                except Exception as e:
                    report["errors"].append(
                        f"Failed to create required directory '{d}': {e}"
                    )

    def _check_write_permissions(self, report):
        test_file = os.path.join("logs", ".write_test")
        try:
            if not os.path.exists("logs"):
                os.makedirs("logs", exist_ok=True)
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            report["errors"].append(
                f"Application lacks write permissions in current directory: {e}"
            )

    def _check_plugin_integrity(self, report):
        plugin_dir = "plugins"
        if not os.path.exists(plugin_dir):
            return

        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                filepath = os.path.join(plugin_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()
                    ast.parse(source)
                except SyntaxError as e:
                    report["warnings"].append(f"Plugin syntax error in {filename}: {e}")
                except Exception as e:
                    report["warnings"].append(f"Could not read plugin {filename}: {e}")

    def _generate_report(self, report):
        """Writes the health check report to disk."""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        report_path = os.path.join(log_dir, "health_report.json")
        try:
            with open(report_path, "w") as f:
                json.dump(report, f, indent=4)
        except Exception:
            pass

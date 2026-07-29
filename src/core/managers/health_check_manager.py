"""
Pre-boot environment validation system.
"""
import os
import sys
import shutil
import ast
import json
import logging

logger = logging.getLogger(__name__)

class HealthCheckManager:
    def __init__(self):
        pass

    def run_all_checks(self):
        """Runs all health checks and returns a summary report."""
        report = {
            "status": "pass",
            "errors": [],
            "warnings": []
        }
        
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

    def _check_python_version(self, report):
        if sys.version_info < (3, 9):
            report["errors"].append(f"Python version must be >= 3.9 (Found {sys.version_info[0]}.{sys.version_info[1]})")

    def _check_ffmpeg(self, report):
        if not shutil.which("ffmpeg"):
            report["errors"].append("FFmpeg is not installed or not in PATH. Required for video/audio processing.")

    def _check_directories(self, report):
        dirs = ["config", "assets", "cache", "projects", "logs", "models", "plugins"]
        for d in dirs:
            if not os.path.exists(d):
                try:
                    os.makedirs(d)
                except Exception as e:
                    report["errors"].append(f"Failed to create required directory '{d}': {e}")

    def _check_write_permissions(self, report):
        test_file = os.path.join("logs", ".write_test")
        try:
            if not os.path.exists("logs"):
                os.makedirs("logs", exist_ok=True)
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            report["errors"].append(f"Application lacks write permissions in current directory: {e}")

    def _check_plugin_integrity(self, report):
        plugin_dir = "plugins"
        if not os.path.exists(plugin_dir):
            return
            
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                filepath = os.path.join(plugin_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
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

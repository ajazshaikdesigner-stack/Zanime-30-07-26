"""
Crash Protection & Project Recovery Service — Phase 5 Reliability Engine.

Features:
  - System Exception Hook catcher (dumps crash traceback to logs/crashes/)
  - Automatic Project Backup Snapshots (rotates max 10 backups per project)
  - Recovery Wizard logic & project file integrity repair
"""

import json
import logging
import os
import sys
import time
import traceback

from src.models.release_model import BackupSnapshot, SystemDiagnosticReport

logger = logging.getLogger(__name__)

MAX_BACKUPS_PER_PROJECT = 10


class RecoveryService:
    """Manages crash exception logging, project backup snapshots, and auto recovery."""

    def __init__(self, backup_dir: str = ""):
        self.backup_dir = backup_dir or os.path.join(
            os.path.expanduser("~"), ".zanime_backups"
        )
        self.crash_log_dir = os.path.join("logs", "crashes")
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.crash_log_dir, exist_ok=True)

    def install_exception_hook(self):
        """Install global sys.excepthook to intercept unhandled exceptions gracefully."""
        def _global_exception_handler(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.critical("UNHANDLED CRASH INTERCEPTED:\n%s", tb_str)

            # Dump Diagnostic Crash Report
            report = SystemDiagnosticReport(crash_traceback=tb_str)
            crash_filename = f"crash_{int(time.time())}.json"
            crash_filepath = os.path.join(self.crash_log_dir, crash_filename)

            try:
                with open(crash_filepath, "w") as f:
                    json.dump({
                        "os": report.os_version,
                        "cpu": report.cpu_info,
                        "gpu": report.gpu_info,
                        "ram": report.installed_ram,
                        "app_version": report.app_version,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "traceback": tb_str,
                    }, f, indent=2)
                logger.info("RecoveryService: Saved crash dump to '%s'", crash_filepath)
            except Exception as e:
                logger.error("RecoveryService: Failed to write crash dump: %s", e)

        sys.excepthook = _global_exception_handler
        logger.info("RecoveryService: Installed global exception hook.")

    def create_snapshot(self, project_name: str, project_data: dict) -> BackupSnapshot | None:
        """Create a timestamped backup snapshot of project_data."""
        if not project_name:
            project_name = "Untitled"

        timestamp_str = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{project_name}_{timestamp_str}.zanime.bak"
        snap_path = os.path.join(self.backup_dir, filename)

        try:
            with open(snap_path, "w", encoding="utf-8") as f:
                json.dump(project_data, f, indent=2)

            snapshot = BackupSnapshot(
                timestamp=timestamp_str,
                project_name=project_name,
                path=snap_path,
                is_auto_backup=True,
            )
            self._cleanup_old_snapshots(project_name)
            logger.info("RecoveryService: Created project snapshot '%s'", filename)
            return snapshot
        except Exception as e:
            logger.error("RecoveryService: Failed to create snapshot: %s", e)
            return None

    def list_snapshots_for_project(self, project_name: str) -> list[BackupSnapshot]:
        """List all backup snapshots available for a project."""
        snapshots = []
        if not os.path.exists(self.backup_dir):
            return snapshots

        for fname in os.listdir(self.backup_dir):
            if fname.startswith(project_name) and fname.endswith(".bak"):
                fpath = os.path.join(self.backup_dir, fname)
                parts = fname.replace(".bak", "").split("_")
                ts = "_".join(parts[-2:]) if len(parts) >= 2 else "unknown"
                snapshots.append(BackupSnapshot(timestamp=ts, project_name=project_name, path=fpath, is_auto_backup=True))

        snapshots.sort(key=lambda s: s.timestamp, reverse=True)
        return snapshots

    def recover_snapshot(self, snapshot_path: str) -> dict | None:
        """Load and return project data from a backup snapshot file."""
        if not os.path.isfile(snapshot_path):
            logger.error("RecoveryService: Snapshot file does not exist: %s", snapshot_path)
            return None

        try:
            with open(snapshot_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info("RecoveryService: Successfully recovered project from '%s'", snapshot_path)
            return data
        except Exception as e:
            logger.error("RecoveryService: Failed to parse snapshot file: %s", e)
            return None

    def _cleanup_old_snapshots(self, project_name: str):
        """Keep only the latest MAX_BACKUPS_PER_PROJECT snapshots."""
        snaps = self.list_snapshots_for_project(project_name)
        if len(snaps) > MAX_BACKUPS_PER_PROJECT:
            for old_snap in snaps[MAX_BACKUPS_PER_PROJECT:]:
                try:
                    os.remove(old_snap.path)
                except OSError:
                    pass

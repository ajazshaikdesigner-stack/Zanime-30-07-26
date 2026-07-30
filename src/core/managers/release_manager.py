"""
Release Managers - Handling Backups, Crashes, Updates, and Licensing
"""

import datetime
import logging

from src.models.release_model import BackupSnapshot, LicenseTier, SystemDiagnosticReport

logger = logging.getLogger(__name__)


class BackupManager:
    def __init__(self):
        self.snapshots: list[BackupSnapshot] = []

    def create_backup(self, project_name: str, is_auto: bool = False) -> BackupSnapshot:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        path = f"C:/Backups/Zanime/{project_name}_{timestamp.replace(':', '-')}.zip"
        snap = BackupSnapshot(timestamp, project_name, path, is_auto)
        self.snapshots.append(snap)
        logger.info(f"Created backup snapshot at {path}")
        return snap

    def restore_backup(self, snapshot_uuid: str) -> bool:
        logger.warning(f"Restoring from backup {snapshot_uuid}...")
        return True


class CrashReporter:
    @staticmethod
    def generate_report(traceback_str: str) -> SystemDiagnosticReport:
        report = SystemDiagnosticReport(crash_traceback=traceback_str)
        logger.error(f"Generating Crash Report: {traceback_str}")
        return report


class UpdateManager:
    @staticmethod
    def check_for_updates() -> str:
        logger.info("Checking for Zanime updates...")
        return "You are on the latest version (1.0.0)."


class LicenseManager:
    def __init__(self):
        self.active_tier = LicenseTier.COMMUNITY

    def activate_pro(self):
        self.active_tier = LicenseTier.PROFESSIONAL
        logger.info("Activated Professional Edition.")

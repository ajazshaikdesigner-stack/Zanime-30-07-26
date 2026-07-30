"""
Settings Workspace - Administrative dashboard.
"""

import logging

from PySide6.QtCore import Qt

from src.core.managers.release_manager import (
    BackupManager,
    CrashReporter,
    LicenseManager,
    UpdateManager,
)
from src.core.sdk.base_workspace import BaseWorkspace
from src.ui.docks.settings_nav_dock import SettingsNavDock
from src.ui.widgets.settings_host_widget import SettingsHostWidget

logger = logging.getLogger(__name__)


class SettingsWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Settings & Admin", parent)
        self.app = app

        # Init Managers
        self.backup_mgr = BackupManager()
        self.license_mgr = LicenseManager()

        # UI
        self.host_widget = SettingsHostWidget(self)
        self.setCentralWidget(self.host_widget)

        self.nav_dock = SettingsNavDock(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.nav_dock)

        # Connect Actions
        self.nav_dock.list.currentRowChanged.connect(self.host_widget.switch_to)

        self.host_widget.btn_backup.clicked.connect(self._create_backup)
        self.host_widget.btn_crash.clicked.connect(self._sim_crash)
        self.host_widget.btn_update.clicked.connect(self._check_update)

        self.host_widget.lbl_tier.setText(self.license_mgr.active_tier.value)

    def _create_backup(self):
        self.backup_mgr.create_backup("CurrentProject", False)
        logger.info("Manual backup created.")

    def _sim_crash(self):
        report = CrashReporter.generate_report("Exception: Simulated Division by Zero")
        self.host_widget.diag_log.setText(
            f"Report Generated for OS: {report.os_version}"
        )

    def _check_update(self):
        msg = UpdateManager.check_for_updates()
        logger.info(msg)

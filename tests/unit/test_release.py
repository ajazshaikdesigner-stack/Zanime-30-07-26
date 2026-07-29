import pytest
from src.core.managers.release_manager import BackupManager, LicenseManager
from src.models.release_model import LicenseTier

def test_backup_manager():
    mgr = BackupManager()
    snap = mgr.create_backup("TestProject", True)
    assert len(mgr.snapshots) == 1
    assert snap.project_name == "TestProject"
    assert snap.is_auto_backup == True
    
def test_license_manager():
    mgr = LicenseManager()
    assert mgr.active_tier == LicenseTier.COMMUNITY
    mgr.activate_pro()
    assert mgr.active_tier == LicenseTier.PROFESSIONAL

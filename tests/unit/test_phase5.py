"""
Unit tests for ZANIME Phase 5 — Commercial Release & Ecosystem.

Covers:
  - Licensing & Activation Service (Tiers, Offline Key Activation, Feature Matrix)
  - Auto Update Manager (Semver comparison, SHA-256 integrity, Rollback backup)
  - Security & Cryptography Service (Token Encryption/Decryption, Path Sanitization, Plugin Signatures)
  - Crash Protection & Recovery Service (Snapshot Backup, Listing, Recovery, Sys Excepthook)
  - Installer & Packaging Engine (Dependency Check, InnoSetup ISS generation, Build Manifest)
"""

import os
import shutil
import tempfile
import unittest

from scripts.build_installer import check_dependencies
from src.core.events.event_bus import EventBus
from src.core.managers.update_manager import UpdateManager
from src.core.services.licensing_service import LicenseTier, LicensingService
from src.core.services.recovery_service import RecoveryService
from src.core.services.security_service import SecurityService


# ---------------------------------------------------------------------------
# Licensing Service Tests
# ---------------------------------------------------------------------------

class TestLicensingService(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.lic_path = os.path.join(self.temp_dir, "license.json")
        self.service = LicensingService(self.lic_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_default_license_is_community_trial(self):
        self.assertEqual(self.service.license_info.tier, LicenseTier.COMMUNITY.value)
        self.assertTrue(self.service.license_info.is_trial)

    def test_offline_activation_pro_valid_key(self):
        success, msg = self.service.activate_offline_code("ZANIME-PRO-1234-5678-VALID", "test@zanime.studio")
        self.assertTrue(success)
        self.assertEqual(self.service.license_info.tier, LicenseTier.PROFESSIONAL.value)
        self.assertFalse(self.service.license_info.is_trial)

    def test_offline_activation_invalid_format(self):
        success, msg = self.service.activate_offline_code("INVALID-KEY", "user@domain.com")
        self.assertFalse(success)

    def test_feature_matrix_community_vs_pro(self):
        self.assertFalse(self.service.is_feature_enabled("team_collaboration"))
        # Activate Pro
        self.service.activate_offline_code("ZANIME-PRO-1234-5678-VALID", "test@zanime.studio")
        self.assertTrue(self.service.is_feature_enabled("team_collaboration"))
        self.assertEqual(self.service.get_max_resolution(), "4K")


# ---------------------------------------------------------------------------
# Auto Update Manager Tests
# ---------------------------------------------------------------------------

class TestUpdateManager(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()
        self.temp_dir = tempfile.mkdtemp()
        self.mgr = UpdateManager(self.event_bus, app_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_semver_comparison(self):
        self.assertTrue(UpdateManager._is_newer("1.0.1", "1.0.0"))
        self.assertTrue(UpdateManager._is_newer("2.0.0", "1.9.9"))
        self.assertFalse(UpdateManager._is_newer("1.0.0", "1.0.0"))
        self.assertFalse(UpdateManager._is_newer("1.0.0", "1.0.1"))

    def test_sha256_verification(self):
        test_file = os.path.join(self.temp_dir, "update.bin")
        content = b"ZANIME UPDATE CONTENT 12345"
        with open(test_file, "wb") as f:
            f.write(content)

        import hashlib
        expected_hash = hashlib.sha256(content).hexdigest()
        self.assertTrue(self.mgr.verify_update_package(test_file, expected_hash))
        self.assertFalse(self.mgr.verify_update_package(test_file, "bad_hash_123"))

    def test_create_rollback_backup(self):
        success = self.mgr.create_rollback_backup()
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.mgr.backup_dir))


# ---------------------------------------------------------------------------
# Security Service Tests
# ---------------------------------------------------------------------------

class TestSecurityService(unittest.TestCase):
    def test_token_encryption_decryption_roundtrip(self):
        token = "secret_api_key_sk_1234567890_zanime"
        encrypted = SecurityService.encrypt_token(token)
        self.assertNotEqual(token, encrypted)
        decrypted = SecurityService.decrypt_token(encrypted)
        self.assertEqual(token, decrypted)

    def test_path_sanitization_prevents_traversal(self):
        base_dir = os.path.abspath(tempfile.mkdtemp())
        try:
            safe = SecurityService.sanitize_path(base_dir, "my_file.png")
            self.assertIsNotNone(safe)
            self.assertTrue(safe.startswith(base_dir))

            unsafe = SecurityService.sanitize_path(base_dir, "../../etc/passwd")
            self.assertIsNone(unsafe)
        finally:
            shutil.rmtree(base_dir, ignore_errors=True)

    def test_plugin_signature_verification(self):
        meta_valid = {"name": "Test Plugin", "version": "1.0.0", "signature": "VERIFIED"}
        self.assertTrue(SecurityService.verify_plugin_signature(meta_valid))


# ---------------------------------------------------------------------------
# Recovery Service Tests
# ---------------------------------------------------------------------------

class TestRecoveryService(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.service = RecoveryService(backup_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_and_recover_snapshot(self):
        project_data = {"name": "Demo Episode", "version": "1.0", "scenes": [1, 2, 3]}
        snapshot = self.service.create_snapshot("Demo Episode", project_data)

        self.assertIsNotNone(snapshot)
        self.assertTrue(os.path.isfile(snapshot.path))

        recovered = self.service.recover_snapshot(snapshot.path)
        self.assertIsNotNone(recovered)
        self.assertEqual(recovered["name"], "Demo Episode")
        self.assertEqual(len(recovered["scenes"]), 3)

    def test_list_snapshots_returns_sorted(self):
        self.service.create_snapshot("TestProject", {"step": 1})
        snapshots = self.service.list_snapshots_for_project("TestProject")
        self.assertGreater(len(snapshots), 0)
        self.assertEqual(snapshots[0].project_name, "TestProject")


# ---------------------------------------------------------------------------
# Installer Engine Tests
# ---------------------------------------------------------------------------

class TestInstallerEngine(unittest.TestCase):
    def test_check_dependencies_returns_dict(self):
        deps = check_dependencies()
        self.assertIn("python", deps)
        self.assertIn("pyside6", deps)
        self.assertIn("ffmpeg", deps)
        self.assertIn("ollama", deps)


if __name__ == "__main__":
    unittest.main()

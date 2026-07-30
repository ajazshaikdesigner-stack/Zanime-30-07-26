"""
Data Models for Production Release & Quality Assurance
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum


class LicenseTier(Enum):
    COMMUNITY = "Community Edition"
    PROFESSIONAL = "Professional Edition"
    ENTERPRISE = "Enterprise Edition"


@dataclass
class SystemDiagnosticReport:
    os_version: str = "Windows 11"
    gpu_info: str = "AMD Radeon RX6500M 4GB"
    installed_ram: str = "16GB"
    cpu_info: str = "AMD Ryzen 5 5600H"
    app_version: str = "0.9.9"
    crash_traceback: str = ""


@dataclass
class BackupSnapshot:
    timestamp: str
    project_name: str
    path: str
    is_auto_backup: bool = False
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

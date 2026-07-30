"""
Collaboration Manager — Team Collaboration & Project Review for Phase 4.

Features:
  - Project Locking (.lock file management)
  - Asset Comments & Notes
  - Project Version History tracking
  - Review & Approval Workflow (Draft, In Review, Approved, Rejected)
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    DRAFT = "Draft"
    IN_REVIEW = "In Review"
    APPROVED = "Approved"
    REJECTED = "Changes Requested"


@dataclass
class AssetComment:
    author: str
    text: str
    asset_id: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class VersionNote:
    version_str: str
    author: str
    notes: str
    timestamp: float = field(default_factory=time.time)


class CollaborationManager:
    """Manages project locking, team comments, version notes, and approval status."""

    def __init__(self, project_dir: str = ""):
        self.status = ApprovalStatus.DRAFT
        self.comments: list[AssetComment] = []
        self.version_notes: list[VersionNote] = []
        self._lock_file = ""
        self.set_project_dir(project_dir)

    def set_project_dir(self, p_dir: str):
        self.project_dir = p_dir
        if p_dir:
            self._lock_file = os.path.join(p_dir, ".zanime.lock")

    def acquire_lock(self, user_name: str) -> bool:
        """Acquire lock on project directory for editing."""
        if not self._lock_file:
            return True

        if os.path.isfile(self._lock_file):
            try:
                with open(self._lock_file, "r") as f:
                    data = json.load(f)
                    owner = data.get("owner", "Unknown")
                    logger.warning("Project is currently locked by '%s'", owner)
                    return False
            except Exception:
                pass

        try:
            with open(self._lock_file, "w") as f:
                json.dump({"owner": user_name, "time": time.time()}, f)
            logger.info("CollaborationManager: Lock acquired by '%s'", user_name)
            return True
        except Exception:
            return False

    def release_lock(self):
        if self._lock_file and os.path.isfile(self._lock_file):
            try:
                os.remove(self._lock_file)
                logger.info("CollaborationManager: Lock released.")
            except Exception:
                pass

    def add_comment(self, author: str, text: str, asset_id: str = "") -> AssetComment:
        comment = AssetComment(author=author, text=text, asset_id=asset_id)
        self.comments.append(comment)
        return comment

    def add_version_note(self, version_str: str, author: str, notes: str) -> VersionNote:
        vn = VersionNote(version_str=version_str, author=author, notes=notes)
        self.version_notes.append(vn)
        return vn

    def set_approval_status(self, status: ApprovalStatus):
        self.status = status
        logger.info("CollaborationManager: Project approval status updated to '%s'", status.value)

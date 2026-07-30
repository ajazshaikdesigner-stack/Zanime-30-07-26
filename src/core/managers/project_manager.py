"""
Project Manager for handling .zanime files and state.
"""

import json
import logging
import os
import shutil
import tempfile
import zipfile

from PySide6.QtCore import QFileSystemWatcher, QObject, QTimer

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.models.base import ProjectModel

logger = logging.getLogger(__name__)


class ProjectManager(QObject):
    def __init__(self, event_bus: EventBus):
        super().__init__()
        self.event_bus = event_bus
        self.current_project_path: str | None = None
        self.temp_dir = os.path.join(tempfile.gettempdir(), "zanime_projects")
        self.project_model: ProjectModel | None = None
        self._is_processing = False

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.setInterval(5 * 60 * 1000)  # 5 minutes

        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.directoryChanged.connect(self._on_directory_changed)
        self.file_watcher.fileChanged.connect(self._on_file_changed)

    def _ensure_temp_dir(self):
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def _enforce_structure(self, extract_path: str):
        directories = [
            "story",
            "script",
            "characters",
            "backgrounds",
            "props",
            "storyboard",
            "scenes",
            "timeline",
            "voice",
            "music",
            "render",
            "cache",
            "autosave",
            "logs",
            "exports",
            "assets",
            "thumbnails",
        ]
        for d in directories:
            os.makedirs(os.path.join(extract_path, d), exist_ok=True)

    def _on_directory_changed(self, path: str):
        logger.debug(f"File watcher: Directory changed {path}")

    def _on_file_changed(self, path: str):
        logger.debug(f"File watcher: File changed {path}")

    def create_project(self, name: str, path: str) -> None:
        """Initializes a new empty project."""
        logger.info(f"Creating project '{name}' at {path}")
        self.current_project_path = path
        self.project_model = ProjectModel(name=name)

        self._ensure_temp_dir()

        project_name = os.path.basename(path).replace(".zanime", "")
        extract_path = os.path.join(self.temp_dir, project_name)
        self._enforce_structure(extract_path)

        self.save_project()
        self.autosave_timer.start()
        self.file_watcher.addPath(extract_path)
        self.event_bus.publish(Event.PROJECT_OPENED, path)

    def open_project(self, path: str) -> None:
        """Extracts .zanime to cache and loads state."""
        logger.info(f"Opening project from {path}")
        if not os.path.exists(path):
            logger.error(f"Project not found: {path}")
            return

        self._ensure_temp_dir()

        # Unzip to a specific folder
        project_name = os.path.basename(path).replace(".zanime", "")
        extract_path = os.path.join(self.temp_dir, project_name)

        with zipfile.ZipFile(path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        # Parse project.json
        project_json_path = os.path.join(extract_path, "project.json")
        if os.path.exists(project_json_path):
            try:
                with open(project_json_path, "r") as f:
                    data = json.load(f)
                    self.project_model = ProjectModel(
                        name=data.get("name", "Unknown"),
                        version=data.get("version", "1.0"),
                        resolution=tuple(data.get("resolution", (1920, 1080))),
                        fps=data.get("fps", 24),
                        author=data.get("author", ""),
                        description=data.get("description", ""),
                    )
            except Exception as e:
                logger.error(f"Failed to read project.json: {e}")
        else:
            self.project_model = ProjectModel(name=project_name)

        self._enforce_structure(extract_path)
        self.current_project_path = path
        self.autosave_timer.start()

        # Check if recovery is needed
        self._check_recovery(extract_path)

        self.file_watcher.addPath(extract_path)
        self.event_bus.publish(Event.PROJECT_OPENED, path)

    def _check_recovery(self, extract_path: str):
        autosave_path = os.path.join(extract_path, "autosave", "project_autosave.json")
        project_json_path = os.path.join(extract_path, "project.json")
        if os.path.exists(autosave_path) and os.path.exists(project_json_path):
            if os.path.getmtime(autosave_path) > os.path.getmtime(project_json_path):
                logger.warning(
                    "Autosave is newer than project.json. Recovery might be needed."
                )
                # We could prompt user or auto-recover here.

    def autosave(self) -> None:
        """Serializes current state to the autosave directory without zipping."""
        if not self.current_project_path or not self.project_model:
            return

        logger.info("Auto-saving project state...")
        project_name = os.path.basename(self.current_project_path).replace(
            ".zanime", ""
        )
        extract_path = os.path.join(self.temp_dir, project_name)

        autosave_path = os.path.join(extract_path, "autosave", "project_autosave.json")
        with open(autosave_path, "w") as f:
            json.dump(self.project_model.__dict__, f, indent=4)

    def save_project(self) -> None:
        """Zips the temp directory back to the .zanime file."""
        if not self.current_project_path:
            logger.warning("Attempted to save with no open project.")
            return

        logger.info(f"Saving project to {self.current_project_path}")
        self._ensure_temp_dir()

        project_name = os.path.basename(self.current_project_path).replace(
            ".zanime", ""
        )
        extract_path = os.path.join(self.temp_dir, project_name)

        self._enforce_structure(extract_path)

        # Purge cache before zipping
        cache_path = os.path.join(extract_path, "cache")
        for item in os.listdir(cache_path):
            item_path = os.path.join(cache_path, item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

        # Write project.json
        project_json_path = os.path.join(extract_path, "project.json")
        with open(project_json_path, "w") as f:
            json.dump(self.project_model.__dict__, f, indent=4)

        # Zip it up (excluding cache and autosave to save space/time)
        with zipfile.ZipFile(
            self.current_project_path, "w", zipfile.ZIP_DEFLATED
        ) as zipf:
            for root, dirs, files in os.walk(extract_path):
                # Optionally filter out cache/autosave here if we truly don't want them in the zip
                if "cache" in dirs:
                    dirs.remove("cache")
                if "autosave" in dirs:
                    dirs.remove("autosave")

                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, extract_path)
                    zipf.write(file_path, arcname)

        self.event_bus.publish(Event.PROJECT_SAVED, self.current_project_path)

    def save_as(self, new_path: str) -> None:
        if not self.current_project_path:
            return
        self.current_project_path = new_path
        self.save_project()

    def close_project(self) -> None:
        if not self.current_project_path:
            return
        self.autosave_timer.stop()
        if self.file_watcher.directories():
            self.file_watcher.removePaths(self.file_watcher.directories())
        self.current_project_path = None
        self.project_model = None

    def delete_project(self, path: str) -> None:
        if self.current_project_path == path:
            self.close_project()
        if os.path.exists(path):
            os.remove(path)

    def rename_project(self, old_path: str, new_path: str) -> None:
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
        if self.current_project_path == old_path:
            self.current_project_path = new_path

    def duplicate_project(self, path: str, new_path: str) -> None:
        if os.path.exists(path):
            shutil.copy2(path, new_path)

    def backup_project(self, backup_dir: str) -> None:
        if self.current_project_path and os.path.exists(self.current_project_path):
            name = os.path.basename(self.current_project_path)
            backup_path = os.path.join(backup_dir, f"{name}.bak")
            shutil.copy2(self.current_project_path, backup_path)

    def restore_project(self, backup_path: str, target_path: str) -> None:
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, target_path)

    def validate_project(self) -> bool:
        """Returns True if project meets missing asset detection requirements."""
        if not self.current_project_path:
            return False
        project_name = os.path.basename(self.current_project_path).replace(
            ".zanime", ""
        )
        extract_path = os.path.join(self.temp_dir, project_name)

        directories = [
            "story",
            "script",
            "characters",
            "backgrounds",
            "props",
            "storyboard",
            "scenes",
            "timeline",
            "voice",
            "music",
            "render",
            "cache",
            "autosave",
            "logs",
            "exports",
            "assets",
            "thumbnails",
        ]
        for d in directories:
            if not os.path.exists(os.path.join(extract_path, d)):
                logger.error(f"Validation failed: missing directory {d}")
                return False
        return True

    from contextlib import contextmanager

    @contextmanager
    def processing_lock(self):
        self._is_processing = True
        try:
            yield
        finally:
            self._is_processing = False

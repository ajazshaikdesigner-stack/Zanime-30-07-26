"""
Story Workspace - The main environment for Phase 5.
"""

import logging
import time

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)

from src.core.ai import ZanimeAIAPI
from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.managers.project_manager import ProjectManager
from src.core.sdk.base_workspace import BaseWorkspace
from src.core.services.service_registry import registry
from src.core.services.story_validator import StoryValidator
from src.models.story_model import StoryModel, StoryVersion
from src.ui.docks.ai_console_dock import AIConsoleDock
from src.ui.docks.story_analysis_dock import StoryAnalysisDock
from src.ui.docks.story_history_dock import StoryHistoryDock
from src.ui.docks.story_settings_dock import StorySettingsDock
from src.ui.widgets.story_editor import StoryEditor


class StoryWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Story Studio", parent)
        self.app = app
        self.story_model = StoryModel()

        # Center Widget
        self.editor = StoryEditor()
        self.setCentralWidget(self.editor)

        # Docks
        self.settings_dock = StorySettingsDock(self)
        self.analysis_dock = StoryAnalysisDock(self)
        self.history_dock = StoryHistoryDock(self)
        self.console_dock = AIConsoleDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.settings_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.analysis_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.history_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)

        self.tabifyDockWidget(self.analysis_dock, self.history_dock)
        self.analysis_dock.raise_()

        # Connect AI signals
        registry.get(EventBus).subscribe(Event.AI_TASK_COMPLETED, self._on_ai_completed)

        # Connect Editor Actions
        self.editor.action_rewrite.triggered.connect(
            lambda: self._generate_text("Rewrite")
        )
        self.editor.action_expand.triggered.connect(
            lambda: self._generate_text("Expand")
        )
        self.editor.action_continue.triggered.connect(
            lambda: self._generate_text("Continue")
        )

        self.settings_dock.generate_btn.clicked.connect(
            lambda: self._generate_text("Generate New Story")
        )
        self.settings_dock.lock_btn.clicked.connect(self.lock_story)

        # Connect text changes for validation
        self.editor.text_edit.textChanged.connect(self._on_text_changed)

        # Auto-save timer
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave_story)
        self.autosave_timer.start(30 * 1000)  # 30 seconds

    def _on_text_changed(self):
        self.story_model.content = self.editor.text_edit.toPlainText()
        warnings = StoryValidator.validate(self.story_model)
        self.analysis_dock.update_analysis(self.story_model, warnings)

    def _generate_text(self, action: str):
        prompt = self.settings_dock.prompt_edit.toPlainText()
        genre = self.settings_dock.genre_combo.currentText()
        if action == "Generate New Story":
            full_prompt = f"Write a {genre} story about: {prompt}"
        else:
            full_prompt = (
                f"{action} this text: {self.editor.text_edit.toPlainText()[:500]}"
            )

        registry.get(ZanimeAIAPI).generate_story(full_prompt, {})

    def _on_ai_completed(self, data: dict):
        # We assume result has 'text'
        res = data.get("result", {}).get("text", "")
        if res:
            self.story_model.content = res
            self.editor.text_edit.setPlainText(res)

            # Save history
            ver = StoryVersion(
                version_id=data.get("id", ""),
                timestamp=time.time(),
                ai_model="llama3:8b",
                prompt="UI Prompt",
                result=res,
            )
            self.story_model.history.append(ver)
            self.history_dock.update_history(self.story_model.history)

            # Validate
            warnings = StoryValidator.validate(self.story_model)
            self.analysis_dock.update_analysis(self.story_model, warnings)

    def autosave_story(self):
        if registry.get(ProjectManager).current_project_path:
            import json
            import os

            pm = registry.get(ProjectManager)
            project_name = os.path.basename(pm.current_project_path).replace(
                ".zanime", ""
            )
            story_path = os.path.join(
                pm.temp_dir, project_name, "story", "story_data.json"
            )

            os.makedirs(os.path.dirname(story_path), exist_ok=True)

            # Simple dict serialization (in real prod, use marshmallow/dataclasses.asdict)
            data = {
                "title": self.story_model.title,
                "content": self.story_model.content,
                "is_locked": self.story_model.is_locked,
            }
            try:
                with open(story_path, "w") as f:
                    json.dump(data, f, indent=4)
            except Exception:
                logger.exception(f"Failed to save story to {story_path}")

    def lock_story(self):
        self.story_model.is_locked = True
        self.editor.set_locked(True)
        self.settings_dock.generate_btn.setDisabled(True)
        QMessageBox.information(
            self, "Story Locked", "This story has been locked for future phases."
        )

    def get_required_docks(self):
        return []

    def get_hidden_docks(self):
        return [
            "Properties",
            "Timeline",
            "ProjectExplorer",
            "Console",
            "AssetBrowser",
            "NotificationCenter",
            "History",
            "Preview",
        ]

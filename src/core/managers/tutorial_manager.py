"""
Tutorial Manager - Controls the state of the interactive learning system.
"""

import logging

from PySide6.QtCore import QObject, Signal

from src.models.tutorial_model import Achievement, TutorialProgress, TutorialStep

logger = logging.getLogger(__name__)


class TutorialManager(QObject):
    step_changed = Signal(TutorialStep)
    achievement_unlocked = Signal(Achievement)
    progress_updated = Signal(int, int)  # current, total

    def __init__(self):
        super().__init__()
        self.progress = TutorialProgress()
        self.steps = self._build_steps()
        self._init_achievements()

    def _build_steps(self) -> list[TutorialStep]:
        return [
            TutorialStep(
                0,
                "Welcome to Zanime",
                "Let's build 'The Crystal Forest'. Click Next to begin.",
                "Story",
            ),
            TutorialStep(
                1,
                "Story Studio",
                "Here you write prompts. The AI will generate a story for Zehak.",
                "Story",
            ),
            TutorialStep(
                2,
                "Character Studio",
                "Meet Zehak and Lumi. Here you manage their DNA and outfits.",
                "Characters",
            ),
            TutorialStep(
                3, "World Builder", "This is the Crystal Forest environment.", "World"
            ),
            TutorialStep(
                4,
                "Movie Composer",
                "Place characters into the scene using the timeline.",
                "SceneComposer",
            ),
            TutorialStep(
                5, "Animation Director", "Add a walk cycle to Zehak.", "Animation"
            ),
            TutorialStep(
                6,
                "Camera Director",
                "Frame the shot using the Rule of Thirds.",
                "Camera",
            ),
            TutorialStep(7, "Voice Studio", "Generate dialogue for Zehak.", "Voice"),
            TutorialStep(
                8, "Production Renderer", "Render your 20-second movie!", "Renderer"
            ),
        ]

    def _init_achievements(self):
        self.progress.achievements = [
            Achievement("first_story", "First Story", "Generated your first story."),
            Achievement("first_character", "First Character", "Created Zehak."),
            Achievement(
                "demo_complete",
                "Demo Completed",
                "Finished The Crystal Forest tutorial.",
            ),
        ]

    def next_step(self):
        if self.progress.current_step_index < len(self.steps) - 1:
            self.progress.current_step_index += 1
            self._emit_state()

            # Mock achievement unlock
            if self.progress.current_step_index == 1:
                self.unlock_achievement("first_story")
            elif self.progress.current_step_index == 8:
                self.unlock_achievement("demo_complete")

    def prev_step(self):
        if self.progress.current_step_index > 0:
            self.progress.current_step_index -= 1
            self._emit_state()

    def get_current_step(self) -> TutorialStep:
        return self.steps[self.progress.current_step_index]

    def _emit_state(self):
        self.step_changed.emit(self.get_current_step())
        self.progress_updated.emit(
            self.progress.current_step_index + 1, len(self.steps)
        )

    def unlock_achievement(self, ach_id: str):
        for ach in self.progress.achievements:
            if ach.id == ach_id and not ach.unlocked:
                ach.unlocked = True
                self.achievement_unlocked.emit(ach)
                logger.info(f"Achievement Unlocked: {ach.name}")
                break

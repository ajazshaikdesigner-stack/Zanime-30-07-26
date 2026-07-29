# Interactive Tutorial System

The Interactive Tutorial System acts as a "Meta-Workspace". Instead of navigating between disjointed studios, the `TutorialWorkspace` wraps around the standard UI flow and forces the user into a specific sequence, providing instructional overlays.

## Architecture
- **TutorialWorkspace**: Inherits from `BaseWorkspace` but utilizes a central `QStackedWidget` (`TutorialHostWidget`). As the user clicks "Next Step", the `TutorialManager` emits a signal telling the host widget to swap the active UI (e.g., from `StoryWorkspace` to `CharacterWorkspace`).
- **TutorialManager**: The state machine driving the experience. It tracks the current step, fires `achievement_unlocked` signals, and manages overall progress.
- **TutorialStep**: Data class defining the `instruction_text` and the `target_workspace`.

By encapsulating the entire Zanime app inside this tutorial shell, first-time users can build an entire mock movie without ever getting lost in the navigation menus.

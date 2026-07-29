# ZANIME Developer Guide

## Architecture
ZANIME follows a strict MVC / Clean Architecture pattern.
- **Core Managers**: Handle state (e.g., `WorkspaceManager`, `ProjectManager`, `CommandManager`). Found in `src/core/managers`.
- **UI Components**: Build the interface in `src/ui`. Separated into Docks, Widgets, and Workspaces.
- **Events**: Global communication is handled via the `EventBus` singleton (`src/core/events/event_bus.py`).
- **Commands**: All mutations should extend `ICommand` (`src/core/commands/base.py`) to support Undo/Redo.

## Adding a Workspace
1. Create a new subclass of `BaseWorkspace` in `src/ui/workspaces/`.
2. Define `get_required_docks()` and `get_hidden_docks()`.
3. Optionally define `save_state()` and `restore_state(state)` for caching.
4. Register it in `src/ui/workspace_factory.py` under `_registry`.
5. Add a button in `src/ui/widgets/sidebar.py`.

## Adding a Dock
1. Extend `QDockWidget`.
2. Instantiate it in `ZanimeMainWindow._setup_docks`.
3. Map it to the relevant Workspaces.

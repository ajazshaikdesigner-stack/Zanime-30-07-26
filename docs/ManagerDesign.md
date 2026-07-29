# Manager Design

Managers are Singleton-like services registered within the `ZanimeApp` context. They handle specific domains of the application lifecycle and state.

## Current Managers (Refined)
- **ApplicationManager**: Orchestrates startup/shutdown sequences and global state.
- **SettingsManager**: (Migrated to ConfigurationManager)
- **ThemeManager**: (Migrated to ThemeEngine)
- **ProjectManager**: Handles `.zanime` zip serialization, parsing `project.json`, autosaves, and recent files.
- **AssetManager**: Loads and caches media (images, audio) and UI icons into memory.
- **PluginManager**: Discovers, loads, and sandboxes 3rd party `.py` plugins.
- **CacheManager**: Manages temporary disk space (e.g., audio waveforms, proxy renders).
- **LoggingManager**: Initializes log rotators for different subsystems.
- **EventBus**: Central pub/sub broker for cross-manager and UI communication.
- **WindowManager**: Handles dialog spawning, z-indexing, and window geometry restoration.

## New Managers Added for Commercial Scalability
- **CommandManager (Undo/Redo)**: Maintains the Undo and Redo stacks. Executes `ICommand` objects. Limits stack size to prevent RAM bloat (16GB RAM constraint).
- **ShortcutManager**: Maps keyboard chords (e.g., `Ctrl+Shift+Z`) to actions or Events. Allows user remapping.
- **NotificationManager**: Queues and displays non-blocking toast notifications in the UI (e.g., "Autosaved", "Render Complete") without interrupting workflow.
- **WorkspaceManager**: Manages the lifecycle of UI Workspaces (Story, Animation). Handles hiding/showing docks based on the active workspace.
- **SelectionManager**: Tracks what the user has currently selected (e.g., a timeline keyframe, a canvas layer) and broadcasts `SelectionChanged` events. Essential for the Properties dock.
- **UpdateManager**: Background thread that checks for software updates or AI model updates.

## Why Each Manager Exists
By decoupling responsibilities into highly specific Managers, we ensure that:
1. Memory leaks are easier to trace.
2. We adhere to the Single Responsibility Principle.
3. The UI components remain extremely lightweight—they simply query a Manager or publish an Event.

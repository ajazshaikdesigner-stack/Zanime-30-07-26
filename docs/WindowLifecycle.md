# Window Lifecycle

## Boot Sequence
1. **Initialize Frameworks**: The `StartupManager` boots core services.
2. **Main Window Creation**: `ZanimeMainWindow` is instantiated.
3. **State Restoration**: The window immediately reads `QSettings` to restore its exact physical geometry and dock configuration from the last session.
4. **Initial Display**: The central workspace container defaults to displaying the `WelcomeWorkspace` or restoring the last opened workspace.

## Shutdown Sequence
1. **closeEvent Triggered**: When the user closes the application, the `closeEvent` is intercepted.
2. **Save Geometry**: The exact pixel layout of the window is serialized to `QSettings`.
3. **Save State**: The arrangement and size of all dock widgets are serialized.
4. **Cache Purge**: The `WorkspaceFactory` initiates a full `cleanup_memory` pass, actively destroying cached workspaces and saving their final states.
5. **Exit**: The application terminates cleanly.

# Plugin SDK Framework

Zanime is highly modular. Developers can inject custom Docks into any Workspace using the `WorkspaceManager`.

## API Hooks
To build a plugin:
1. Subclass `BaseDock`.
2. Connect to the global `ZanimeProject` event bus.
3. Call `WorkspaceManager.get_workspace("Target").addDockWidget(...)`

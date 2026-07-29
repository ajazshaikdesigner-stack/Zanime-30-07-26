# Welcome Workflow

When the application boots:
1. `WelcomeWorkspace` is instantiated by the `WorkspaceFactory` (or restored from `QSettings`).
2. The UI reads project data (currently mocked) and generates `ProjectCard` widgets.
3. Users can type in the search box to instantly filter projects.
4. Clicking a project or Quick Action dispatches an event to the `WorkspaceManager` to transition out of the Welcome state and into the core Editor.

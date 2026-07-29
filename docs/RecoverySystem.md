# Recovery System

The `ProjectManager` runs a `QTimer` that triggers a fast JSON serialization to `autosave/project_autosave.json`. 

If the application crashes, the next time `open_project()` extracts the `.zanime` file to `temp/`, the manager compares the Modified Timestamp of `project.json` against `project_autosave.json`. If autosave is newer, the user can safely recover the state.

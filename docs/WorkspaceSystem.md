# Workspace System

The Workspace System is responsible for managing context switching in ZANIME. 

## Features
- **Instant Switching**: Workspaces are held in a `QStackedWidget` loaded once at boot (Lazy loading will be introduced for heavy modules).
- **Layout Preservation**: Thanks to `LayoutManager`, when you leave the "Animation" workspace and come back, your resized Timeline and dragged Property Inspector are restored exactly as you left them.

## Creating a Workspace
Inherit from `BaseWorkspace` in `src.core.sdk.base_workspace`. Implement `get_required_docks()` returning a list of dock IDs (e.g., `["Properties", "Timeline"]`).

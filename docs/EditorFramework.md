# Editor Framework

ZANIME's Phase 2 Editor Framework provides the robust base SDK upon which all future AI and Animation tools are built.

## Architecture
The framework resides in `src/core/sdk/` and provides:
- **BaseWorkspace**: Controls a single visual mode (e.g., Animation vs. Library).
- **BaseEditor**: The central canvas widget for a workspace.
- **BaseDock**: Reusable, layout-managed side panels.
- **BaseUI (Toolbars/Panels)**: Unified styled components.

## Data Flow
Each Workspace defines which Docks to show or hide via `get_required_docks()` and `get_hidden_docks()`. The `WorkspaceManager` and `LayoutManager` coordinate to hide/show and restore previously saved splitter states (sizes/positions) from the user's `config.json`.

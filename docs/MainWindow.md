# Main Window Layout

The `ZanimeMainWindow` is the root structural component of ZANIME v2. It acts as a rigid, standardized layout container ensuring UI consistency across all 17 available workspaces.

## Structure

1. **Top**: Global Menu Bar & ToolBar
2. **Left**: Global Navigation Sidebar
3. **Center**: `QStackedWidget` (Workspace Container)
4. **Right**: Property Panel, Project Explorer, Asset Browser (Hidden by default, requested by workspaces)
5. **Bottom**: Timeline, Console, Notifications (Dynamic Dock Area)

## State Persistence

The Main Window uses `QSettings` to continuously track and automatically restore:
- Exact window size and monitor position
- Fullscreen / maximized states
- The dimensions of all dragged and resized dock panels (e.g., Timeline height)

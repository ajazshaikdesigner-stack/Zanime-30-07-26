# CHANGELOG

## [Phase 3] - Foundation Optimization
- **Refactored**: `WelcomeWorkspace` completely redesigned with professional Quick Actions, Demo Cards, and live Search Filtering for Mock Projects.
- **Added**: Custom `ProjectCard` and `DemoProjectCard` PySide6 UI widgets.
- **Refactored**: `ZanimeMainWindow` upgraded with full QSettings state persistence.
- **Refactored**: `WorkspaceFactory` now isolates initialization crashes via `WorkspaceErrorWidget`.
- **Refactored**: `ZanimeStatusBar` features live CPU and RAM telemetry using psutil.

## [Phase 2] - Editor Framework
- **Added**: `src/core/sdk/` with `BaseWorkspace`, `BaseEditor`, `BaseDock`.
- **Added**: `LayoutManager` for saving/restoring QMainWindow byte states.
- **Added**: `ShortcutManager` configuration binding.
- **Added**: Comprehensive mock Docks (Asset Browser, Property Inspector, Timeline, Notification, History, Preview).
- **Refactored**: All Phase 1 Workspaces updated to use `BaseWorkspace`.
- **Refactored**: `ZanimeMainWindow` registers all docks using a loop over `self.docks`.

## [Phase 1] - Core Architecture
- Foundation managers, EventBus, Zip Project handling.

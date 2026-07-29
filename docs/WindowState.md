# Window State Persistence

ZANIME implements zero-configuration state persistence across sessions.

## QSettings
We utilize Qt's native `QSettings` registry (stored securely in the OS's preferred app data directory).

### Variables Tracked
- **geometry**: The binary representation of the window's physical location, multiple-monitor offset, and size constraints.
- **windowState**: The binary map of the `DockManager` configuration. It remembers which docks were floating, docked, resized, or hidden.

## Restoring State
On startup, before the window even flashes on screen, `restoreGeometry()` and `restoreState()` are called. This eliminates visual jitter and guarantees that if a user left their timeline expanded to half the screen height, it will be exactly that way when they return.

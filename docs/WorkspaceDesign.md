# Main Window & Workspace Design

The ZANIME Main Window takes inspiration from industry standards (VS Code, Blender, Premiere) but simplifies the UX for beginners.

## Complete UI Hierarchy

```text
QMainWindow (ZanimeMainWindow)
├── QMenuBar (Global Actions: File, Edit, View, Help)
├── QToolBar (Top - Global Tools: Save, Undo, Redo, Render, Play)
├── QToolBar (Left/Vertical - Workspace Switcher)
│   ├── [Icon] Home
│   ├── [Icon] Story
│   ├── [Icon] Script
│   ├── [Icon] Characters
│   ├── [Icon] Backgrounds
│   ├── [Icon] Storyboard
│   ├── [Icon] Animation
│   ├── [Icon] Voice
│   ├── [Icon] Music
│   └── [Icon] Render
├── QWidget (Central Area)
│   └── QStackedWidget (Managed by WorkspaceManager)
│       ├── HomeWorkspaceWidget
│       ├── AnimationWorkspaceWidget (Contains Canvas/Viewport)
│       └── ...
├── QDockWidget (Managed dynamically by active Workspace)
│   ├── PropertiesDock (Right)
│   ├── AssetBrowserDock (Left)
│   ├── TimelineDock (Bottom)
│   ├── PreviewDock (Right/Floating)
│   ├── ConsoleDock (Bottom/Hidden)
│   ├── NotificationsDock (Floating overlay)
│   ├── AIAssistantDock (Right)
│   └── ProjectExplorerDock (Left)
└── QStatusBar (Bottom - Render progress, Selection info, Version)
```

## Modular Workspace System

To prevent UI clutter, ZANIME uses a modular workspace system.

1. **`WorkspaceManager`**: Listens for `WorkspaceChanged` events (triggered by the left vertical toolbar).
2. **`BaseWorkspace`**: An abstract interface. Each workspace (e.g., `AnimationWorkspace`) inherits this. It defines:
   - `get_central_widget()`: Returns the main view (e.g., the drawing canvas).
   - `get_required_docks()`: Returns a list of docks it needs (e.g., Timeline, Properties).
   - `get_hidden_docks()`: Docks that should be explicitly hidden.
3. **Switching Logic**: When switching from "Story" to "Animation", the `WorkspaceManager`:
   - Hides the Story central widget.
   - Shows the Animation central widget in the `QStackedWidget`.
   - Re-arranges the `QDockWidgets` (showing Timeline, hiding Text Editor).

## Dock Widget Responsibilities

- **Properties**: Context-sensitive. If a layer is selected, shows opacity/blend modes. If a keyframe is selected, shows easing curves. Driven by the `SelectionManager`.
- **Asset Browser**: Library of imported images, sounds, and generated AI assets. Drag-and-drop enabled.
- **Timeline**: Tracks layers, keyframes, and audio tracks. Essential for the Animation workspace. Highly optimized drawing required for the 16GB RAM constraint.
- **Console**: Hidden by default. Shows python `print()` and logger outputs for advanced users/debugging.
- **Notifications**: Not a traditional dock, but an overlay for non-intrusive toasts.
- **AI Assistant**: A chat-like interface dock where users can prompt the AI for story ideas or asset generation.
- **Project Explorer**: Tree view of the `.zanime` project structure.
- **Preview**: A small floating or docked window showing the current camera view, regardless of workspace.

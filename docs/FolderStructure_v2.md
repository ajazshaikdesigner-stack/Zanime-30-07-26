# Folder Structure v2

To ensure ZANIME scales to a commercial level, we have refined the folder structure. The previous structure grouped all logic into just `core` and `app`. As the application grows to include features like animation timelines, AI integrations, and varied workspaces, a more granular structure is required.

## Improved Structure

```text
zanime/
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Testing and linting tools
├── run.py                   # Main entry point (simplified from main.py)
├── .env.example             # Environment variables template
├── docs/                    # Architecture and developer documentation
├── assets/                  # Shipped application assets (default themes, core icons)
├── config/                  # Shipped default configurations
├── plugins/                 # 3rd party plugins directory
├── logs/                    # Runtime logs (git-ignored)
├── tests/                   # Pytest suite (smoke, unit, integration, e2e)
└── src/                     # Core application source
    ├── __init__.py
    ├── app.py               # ZanimeApp class and lifecycle
    ├── core/                # Core Managers and Systems
    │   ├── managers/        # Project, Cache, Asset, Plugin, etc.
    │   ├── commands/        # Undo/Redo command pattern classes
    │   ├── events/          # EventBus and Event types
    │   └── utils/           # Helper functions
    ├── config/              # Configuration schemas and parsers
    ├── logging/             # Specialized loggers (AI, Render, Crash)
    ├── models/              # Data structures (Project, Layer, Timeline)
    ├── services/            # Interfaces for future AI/Render engines
    ├── ui/                  # All PySide6 Visual Components
    │   ├── main_window.py
    │   ├── workspaces/      # Specialized UI layouts (Story, Animation, etc.)
    │   ├── docks/           # Reusable dockable widgets
    │   ├── dialogs/         # Popups (Settings, Welcome)
    │   ├── widgets/         # Custom granular Qt widgets (Buttons, Sliders)
    │   └── theme/           # QSS, Color palettes, Scaling logic
```

## Why These Improvements?
1. **`src/models/`**: Separates data structures (like what a "Layer" or "Project" is) from the UI and Managers, enforcing MVC/Clean Architecture.
2. **`src/services/`**: Provides a clear boundary for complex subsystems like the rendering engine or AI inference APIs.
3. **`src/ui/workspaces/`**: Accommodates Task 4 (Workspace System). Instead of dumping all UI into `main_window`, the main window just hosts active workspaces.
4. **`src/core/commands/`**: Dedicated namespace for the Command pattern (Undo/Redo), which will become massive as features are added.

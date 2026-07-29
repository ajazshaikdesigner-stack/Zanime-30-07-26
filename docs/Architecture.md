# Architecture

ZANIME follows a Clean Architecture approach with Dependency Injection and an Event Bus pattern.

## Core Principles

1. **Separation of Concerns**: UI components do not handle business logic. Business logic does not depend on UI components.
2. **Event-Driven**: Components communicate via an Event Bus, reducing direct coupling.
3. **Modular**: Features are encapsulated in plugins or specific core modules.

## Key Modules

- **Application (`src.app`)**: Handles the bootstrap process, initializing managers, and setting up the main window.
- **Core (`src.core`)**: 
  - `ProjectManager`: Handles loading/saving of `project.json` and recent projects.
  - `SettingsManager`: Manages application-wide settings in `config/default_settings.json`.
  - `EventBus`: Central pub/sub system for decoupled communication.
  - `Logger`: Centralized logging setup.
- **UI (`src.ui`)**: Contains all PySide6 widgets, windows, and styles. Uses Qt QSS for styling.

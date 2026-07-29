# Configuration Design

ZANIME configurations are decoupled into separate domains to prevent monolithic, brittle config files and allow easy resets of specific areas.

## Config Hierarchy

1. **`app_config.json`**: Global installation settings. (Hardware acceleration toggles, crash reporting preferences). Read-only for standard users, requires admin to change.
2. **`user_config.json`**: User preferences (Recent files list, default author name, API keys for AI services). Stored in `%APPDATA%/Zanime/`.
3. **`theme_config.json`**: Active theme selection, custom accent colors, font scaling factors.
4. **`workspace_config.json`**: Serialized states of `QDockWidgets` (which docks are open, their sizes, custom layouts). Allows users to save "Custom Workspaces".
5. **`project/config.json`**: Resides *inside* the `.zanime` file. Contains project-specific settings like default FPS, target resolution, and aspect ratio.

## Resolution Logic
If a setting exists in multiple places (e.g., "default_resolution"), the `ConfigurationManager` resolves them in this priority order:
Project Config > User Config > App Config.

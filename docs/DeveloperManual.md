# Zanime Developer Manual

## Architecture Overview
Zanime utilizes a Model-View-Controller (MVC) pattern deeply tied to PySide6.
- **Core SDK**: `src/core/sdk/` contains the base classes (`BaseWorkspace`, `BaseDock`) all modules inherit from.
- **Managers**: `src/core/managers/` operate as Singletons handling logic (e.g. `ProjectManager`, `AssetManager`).

## Testing Framework
All code must pass `pytest tests/`. 
Integration tests are located in `tests/integration/test_smoke.py`, which validates the architectural spine by loading all core managers sequentially.

## Caching
Developers must respect the `CacheManager`. Do not hold heavy textures in memory indefinitely.

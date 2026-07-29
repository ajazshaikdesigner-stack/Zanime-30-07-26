# Architecture Reference

Zanime uses a strictly decoupled, highly scalable architecture tailored for PySide6.

## The Triad
1. **Models**: Plain Python Dataclasses for strict typing (e.g. `CharacterModel`, `StoryboardModel`).
2. **Managers**: Global services implementing core logic (e.g. `ProjectManager`, `AssetManager`).
3. **UI Views**: PySide6 Workspaces and Docks.

No direct communication occurs between UI components; everything flows through the underlying singleton Managers or the central `EventBus`.

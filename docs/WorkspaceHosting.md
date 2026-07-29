# Workspace Hosting System

Instead of a monolithic initialization where every UI element is instantiated at boot, ZANIME uses a dynamic **Workspace Hosting System**.

## The Factory Mechanism
The central area of the Main Window is an empty `QStackedWidget`. All workspaces are generated and managed by the `WorkspaceFactory`.

When a user selects a workspace via the Sidebar:
1. The Factory checks the LRU cache.
2. If it doesn't exist, it is cleanly instantiated (`Lazy Loading`).
3. If the instantiation crashes, the Factory swallows the exception and renders a `WorkspaceErrorWidget` containing the traceback, ensuring the Main Window remains stable.
4. The Workspace is pushed to the `QStackedWidget` and made active.

## Crash Proofing
A single broken python script in a specific workspace (e.g., a bad script in the Character Studio) will never bring down the entire application. The Factory guarantees isolation.

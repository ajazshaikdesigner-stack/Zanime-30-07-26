# Architecture v2 - ZANIME

## Overview
Phase 1 - Step 2 focuses on refining the foundation of ZANIME to support commercial-scale 2D animation and future AI integration. We are migrating from a basic prototype structure to a highly modular, event-driven **Clean Architecture**.

## Architectural Pillars

1. **Strict Decoupling**: UI components do not process data. They only dispatch Commands or publish Events.
2. **Command Pattern**: All mutating actions (drawing a line, adding a layer, changing a setting) are encapsulated in `ICommand` objects. This allows a unified Undo/Redo stack and future macro recording.
3. **Workspace Modularity**: The UI is divided into context-specific Workspaces (Story, Animation, Render). This keeps the interface clean for beginners while remaining powerful for professionals.
4. **Service-Oriented Core**: Future AI modules (Character, Voice) will be integrated as Services that run asynchronously, communicating via the `EventBus` to prevent UI freezing.
5. **Optimized for Target Hardware**: Designed specifically to run efficiently on AMD Ryzen 5 5600H and AMD Radeon RX6500M with 16GB RAM. Memory mapping, caching, and lazy-loading are prioritized over loading entire projects into RAM.

## System Diagram (Conceptual)

```
[ UI Layer (PySide6) ] <----(Events/Data)----> [ Core Managers ]
      |                                              |
      v                                              v
[ CommandManager ]                             [ Services / AI ]
      |                                              |
      +-------------> [ Models & Data ] <------------+
```

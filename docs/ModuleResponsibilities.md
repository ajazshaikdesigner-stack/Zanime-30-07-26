# Module Responsibilities

To ensure maintainability, each module in the `src/` directory has a strictly defined responsibility.

## `src.core`
- **`managers/`**: Lifecycle managers for specific domains (Projects, Assets, Plugins).
- **`commands/`**: Implementations of the Command pattern. E.g., `AddLayerCommand`, `DeleteAssetCommand`.
- **`events/`**: The `EventBus` and definitions of all cross-system events.

## `src.models`
Defines the pure data structures. These classes contain NO UI logic and NO complex business logic—only data and serialization methods.
- `ProjectModel`: Stores metadata, resolution, framerate.
- `LayerModel`: Stores layer visibility, blend mode, z-index.
- `KeyframeModel`: Stores time and value interpolations.

## `src.services`
Interfaces for heavy computations or external APIs.
- `RenderService`: Interfaces with ffmpeg or the custom rendering engine.
- `AIService` (Future): Interfaces with local or cloud AI models.

## `src.ui`
Strictly presentation.
- **`workspaces/`**: High-level layouts that swap out the central widget.
- **`docks/`**: Reusable side panels (Timeline, Properties).
- **`widgets/`**: Custom, highly-styled basic components (e.g., `ZanimeSlider`, `ZanimeButton`) to ensure visual consistency across the app.

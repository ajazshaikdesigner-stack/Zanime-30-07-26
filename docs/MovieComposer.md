# Movie Composer Studio

The Movie Composer Studio is the central environment where assets from the World Builder and Character Studio are physically mapped onto a 2D canvas according to the Storyboard's timing plan.

## Architecture
- **LayerType Enum**: Strictly defines rendering Z-order (e.g. `BACKGROUND` always draws behind `CHARACTERS`, which draws behind `UI`).
- **ComposerObject**: The base physical representation of an asset. Stores `x`, `y`, `scale_x`, `scale_y`, `rotation`, and `layer`.
- **MovieCanvas**: The specialized `QGraphicsView` which houses the objects. Supports drag/drop manipulations.

## Docks
1. **SceneHierarchyDock**: A tree widget visualizing the parent-child relationships from `Movie -> Scene -> Shot -> Layers -> Objects`.
2. **ComposerPropertiesDock**: A dynamic form that binds to the selected `ComposerObject`, exposing manual float-value entry for precision placement.
3. **ComposerTimelineDock**: Visualizes overlapping layered elements across the active shot's duration.

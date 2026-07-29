# World Builder Studio

The World Builder Studio is a unified workspace for generating and managing both Environments (backgrounds, sets) and Props (weapons, furniture, magic items).

## UI Layout
- **WorldWorkspace**: Central Workspace inheriting from `BaseWorkspace`.
- **WorldLibraryDock**: Left panel utilizing a Tab Widget to switch between Environments and Props lists.
- **WorldPropertiesDock**: Right panel with a `QStackedWidget` that swaps out data-entry forms depending on if you are editing an Environment or a Prop.
- **WorldPreview**: A visualizer that simulates Time of Day, Weather, and Season via overlay combinations.

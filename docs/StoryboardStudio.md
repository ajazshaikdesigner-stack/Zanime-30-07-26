# Storyboard Studio

The Storyboard Studio organizes the chronological sequence of a Zanime production. It binds Character, Prop, and Environment assets to specific time intervals (Shots), grouping them into logical blocks (Scenes).

## Structural Breakdown
- **StoryboardModel**: The root container for a full film/episode timeline.
- **SceneModel**: A segment of action occurring in a single Environment with a cohesive lighting/weather setup.
- **ShotModel**: A specific camera cut within a Scene (e.g. Medium Shot, 4.5 seconds).

## Viewports
1. **SceneListDock**: Provides a collapsible tree structure of the entire script layout.
2. **StoryboardCanvas**: Generates visual thumbnail cards representing the framing and duration of every shot in the active scene.
3. **StoryboardTimelineDock**: Mimics a Non-Linear Editor (NLE) horizontally mapping out blocks proportionate to their exact seconds.

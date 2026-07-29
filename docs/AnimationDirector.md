# Animation Director Studio

The Animation Director Studio handles timeline-based interpolation for `ComposerObjects`. It operates entirely independently of the final renderer.

## Data Structures
- **AnimationTimeline**: The root container for a scene's animation data, defining global `fps` and `total_frames`.
- **AnimationTrack**: A layer in the timeline bound to a specific `target_object_uuid`.
- **AnimationClip**: A designated block of time (e.g., frames 0-24) containing an array of keyframes. Can be set to loop.
- **Keyframe**: Stores a precise `frame` integer, the targeted `property_name` (e.g., "rotation"), a `value`, and the `interpolation` algorithm (Linear, Bezier, Hold).

## Core UI Components
1. **AnimationLibraryDock**: Stores pre-baked clips (Walk cycles, laughs) that can be dragged directly onto tracks.
2. **AnimationViewport**: The QGraphicsView where animation is previewed visually in real-time.
3. **AnimationPropertiesDock**: The inspector panel for modifying Bezier curves and exact keyframe values.
4. **AnimationTimelineDock**: A multi-track layout showing blocks of clips distributed across frames.

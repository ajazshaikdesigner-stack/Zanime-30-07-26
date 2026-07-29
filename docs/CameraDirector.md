# Camera Director Studio

The Camera Director Studio manages framing, simulated lens parameters, and cinematic transitions overlaid across the scene's timeline.

## Data Structures
- **Camera**: Defines the physical lens state (e.g., `depth_of_field` (f-stop), `lens_type` (50mm), `focus_distance`, and `aspect_ratio`).
- **CameraTimeline**: Tracks camera shots and transitions across a fixed frame count.
- **CameraClip**: Specifically dictates the `shot_type` (Wide, Close Up) and `movement_type` (Pan, Whip Pan), along with `composition_rule` guides.

## Composition System
The Camera Viewport natively draws `QPainter` overlays onto the `QGraphicsScene` depending on the active clip's composition requirement:
- **Rule of Thirds**: Standard 3x3 grid dividing the 1920x1080 canvas.
- **Center**: Simple vertical and horizontal crosshair for symmetrical setups.

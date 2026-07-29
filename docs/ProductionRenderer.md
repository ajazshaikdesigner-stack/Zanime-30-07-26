# Production Renderer

The Production Renderer is the final node in the Zanime pipeline. It is responsible for compiling all layout, animation, camera, and voice tracks into a final video file.

## Data Structures
- **RenderSettings**: Holds the desired output config (`resolution`, `fps`, `output_format`, `quality`).
- **RenderJob**: Represents a queued task for a specific scene or movie, tracking its `status` and `progress`.
- **RenderManager**: A specialized `QThread` engine. It processes `RenderJob` items sequentially in the background, allowing the user to continue using the application while renders progress.

## The Pipeline
1. **Validation**: The `ProductionValidator` checks for critical missing data (like no Camera or Animation).
2. **Frame Generation**: `RenderWorker` steps through the scene frame by frame, triggering the `QGraphicsScene` to render to an image.
3. **Encoding (Future)**: The rendered images and the audio tracks are handed off to FFmpeg to be multiplexed into the final MP4/MOV container.

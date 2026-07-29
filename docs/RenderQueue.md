# Render Queue Architecture

Zanime implements a robust, background-threaded render queue.

## Concurrency
Rendering heavily tasks the CPU and GPU. If we run rendering operations on the Main UI Thread, PySide6 will freeze and the OS will declare the application "Not Responding".

To solve this, `RenderManager` instantiates a `RenderWorker` which subclasses `QThread`. 
- **QThread** operates independently.
- **Signals** (`progress`, `finished`) are emitted safely across the thread boundary back to the main UI to update the progress bars and logs.

## Controls
Users can actively interact with the `RenderWorker` via:
- **Pause/Resume**: Sleeps the thread temporarily.
- **Cancel**: Aborts the rendering loop early, setting the job status to `FAILED`.

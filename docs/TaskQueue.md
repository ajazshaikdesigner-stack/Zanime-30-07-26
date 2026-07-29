# AITaskQueue

The AI Task Queue utilizes `PySide6.QtCore.QThreadPool` to ensure the main UI thread never blocks during generation.

## Features
- **Job Cancellation**: Abort running tasks immediately via atomic flags.
- **Job Pausing**: Pause background thread loops safely.
- **Signals**: Connects directly to the `EventBus` to notify the `AIConsoleDock` of progress.

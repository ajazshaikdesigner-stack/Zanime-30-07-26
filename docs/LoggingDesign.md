# Logging Design

To ensure maintainability and debuggability in a commercial setting, ZANIME uses specialized loggers instead of a single massive log file.

## Log Streams

1. **Application Log** (`app.log`): UI interactions, Manager initializations, EventBus routing, file I/O operations.
2. **Renderer Log** (`renderer.log`): Frame generation times, GPU memory usage, ffmpeg encoding outputs. Critical for debugging the AMD Radeon RX6500M performance.
3. **Plugin Log** (`plugin.log`): Sandboxed output from 3rd party scripts. Kept separate so broken plugins don't obscure core app issues.
4. **AI Log** (`ai.log`): Prompts sent, API response times, model inference times, token usage.
5. **Crash Log** (`crash.log`): Only populated upon critical unhandled exceptions. Contains full traceback and system state dump.
6. **Performance Log** (`perf.log`): CSV formatted telemetry (FPS, RAM usage, CPU load) for internal profiling.

## Mechanism
- Handled by the `LoggingManager`.
- Utilizes Python's `logging.handlers.TimedRotatingFileHandler` to prevent log bloat on the user's disk (keeps 7 days of logs max).

# Performance Manager & Resource Monitoring

Because Zanime operates heavily on ML tasks and 2D texture rendering, Memory and VRAM constraints are extremely strict. The `PerformanceManager` actively monitors these to prevent application crashes.

## ResourceMonitor QThread
This background thread loops constantly while the `PerformanceWorkspace` is active. It polls the system for CPU, RAM, and GPU load. 
*(Note: As we are mocking deep OS calls in this prototype, `SystemMetrics` uses simulated constraints representing the AMD Ryzen 5 / RX6500M 4GB limit).*

## Diagnostics
The metrics are passed via Qt Signals directly to the `LiveDashboardWidget`, which visualizes the load using simple progress bars. If RAM exceeds a dangerous threshold (e.g., >85%), the UI reacts by turning the progress bar red, prompting the user to clear their caches.

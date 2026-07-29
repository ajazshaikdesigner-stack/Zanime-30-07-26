# AI Framework

The AI Framework serves as the underlying backbone for all future generative modules in ZANIME. It strictly limits resource exhaustion and provides a unified background execution environment.

## Sub-Systems
- **AIManager**: High-level orchestration and memory tracking.
- **ModelManager**: Verification of local tensor weights.
- **AITaskQueue**: Background threading for heavy jobs.
- **DownloadManager**: Asynchronous model downloading.

## Target Hardware
Designed to run stably on **AMD Ryzen 5 5600H, RX6500M (4GB VRAM), 16GB RAM**. The system enforces a strict 3.5GB limit, forcefully unloading idle providers when a new provider requests memory.

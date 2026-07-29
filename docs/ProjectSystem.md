# Project System

The Project System is the overarching architecture responsible for maintaining ZANIME projects across disk and memory.

## Capabilities
- 18-folder `.zanime` internal serialization format.
- Seamless `QFileSystemWatcher` to detect external asset manipulation.
- Fast `save_as`, `duplicate_project`, and `backup_project` functionalities via `ProjectManager`.

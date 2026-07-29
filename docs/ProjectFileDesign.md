# Project File Design

A `.zanime` file is essentially a renamed `.zip` archive containing the entire project context. This ensures all assets travel with the project, preventing missing media errors.

## Internal Folder Structure of `.zanime`
When unzipped (or loaded into temporary cache), the structure looks like:

```text
my_animation.zanime/
├── project.json         # Core metadata, layer hierarchy, workspace state
├── config.json          # Project-specific configurations (fps, resolution)
├── history.json         # Serialized undo/redo stack (if persisted)
├── assets/              # Imported images, audio, generated AI images
│   ├── audio/
│   ├── backgrounds/
│   └── characters/
├── cache/               # Render caches, proxy files (cleared on clean save)
├── autosave/            # Background backups of project.json
└── versioning/          # Snapshot diffs for complex project recovery
```

## Optimization for 16GB RAM constraints
- Unzipping the entire `.zanime` into RAM is forbidden.
- The `ProjectManager` extracts the archive to `tempfile.gettempdir()/zanime/project_hash/`.
- Assets are streamed from disk via `AssetManager` as needed. 
- Large media files are memory-mapped or downscaled (proxy rendering) to ensure the 16GB limit is never breached during intense editing sessions on the target hardware.

# Project Manager

`src/core/managers/project_manager.py` handles parsing `.zanime` zip files and maintaining `ProjectModel` state.

## Advanced Operations
- **Save As**: `save_as(new_path)`
- **Backup**: `backup_project(dir)`
- **Restore**: `restore_project(bak_path, target)`
- **Validate**: `validate_project()` ensures the 18-folder format is strictly respected before allowing modifications.

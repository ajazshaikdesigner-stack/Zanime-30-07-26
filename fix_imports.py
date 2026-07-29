import os
import glob

workspace_files = glob.glob('src/ui/workspaces/*_workspace.py')
for file in workspace_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace(
        "from src.ui.workspaces.base_workspace import BaseWorkspace",
        "from src.core.sdk.base_workspace import BaseWorkspace"
    )
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print("Imports updated.")

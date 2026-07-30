import os

workspaces = [
    "Story",
    "Script",
    "Characters",
    "Backgrounds",
    "Props",
    "Storyboard",
    "SceneComposer",
    "Voice",
    "Music",
    "Render",
    "Library",
    "Settings",
]

template = """\"\"\"
{name} workspace.
\"\"\"
from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from src.ui.workspaces.base_workspace import BaseWorkspace

class {class_name}Workspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__(app, parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("{display_name} Workspace")
        title.setStyleSheet("font-size: 24pt; color: #777;")
        layout.addWidget(title)

    def get_required_docks(self):
        return []

    def get_hidden_docks(self):
        return ["Properties", "Timeline", "ProjectExplorer", "Console"]
"""

for ws in workspaces:
    filename = f"{ws.lower()}_workspace.py"
    if ws == "SceneComposer":
        filename = "scene_composer_workspace.py"

    # Format class name (e.g. SceneComposer)
    class_name = ws
    # Format display name (e.g. Scene Composer)
    display_name = ws if ws != "SceneComposer" else "Scene Composer"

    filepath = os.path.join("src", "ui", "workspaces", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(
            template.format(
                name=display_name, class_name=class_name, display_name=display_name
            )
        )

print("Workspaces generated.")

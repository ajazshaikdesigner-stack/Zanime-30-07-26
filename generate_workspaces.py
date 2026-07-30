import argparse
import logging
import os

logger = logging.getLogger(__name__)

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
from src.core.sdk.base_workspace import BaseWorkspace

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
        return [
            "Properties",
            "Timeline",
            "ProjectExplorer",
            "Console",
            "AssetBrowser",
            "NotificationCenter",
            "History",
            "Preview",
        ]
"""


def main():
    parser = argparse.ArgumentParser(
        description="Generates missing ZANIME workspace templates."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing workspace files if confirmed.",
    )
    args = parser.parse_args()

    created_count = 0
    skipped_count = 0

    for ws in workspaces:
        filename = f"{ws.lower()}_workspace.py"
        if ws == "SceneComposer":
            filename = "scene_composer_workspace.py"

        class_name = ws
        display_name = ws if ws != "SceneComposer" else "Scene Composer"

        filepath = os.path.join("src", "ui", "workspaces", filename)

        if os.path.exists(filepath) and not args.force:
            print(f"[SKIP] Workspace file already exists: {filepath}")
            skipped_count += 1
            continue

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(
                template.format(
                    name=display_name,
                    class_name=class_name,
                    display_name=display_name,
                )
            )
        print(f"[CREATED] {filepath}")
        created_count += 1

    print(
        f"\nWorkspace Generation Complete: {created_count} created, {skipped_count} skipped."
    )


if __name__ == "__main__":
    main()

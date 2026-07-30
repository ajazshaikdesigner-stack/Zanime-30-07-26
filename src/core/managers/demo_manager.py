import json
import logging
import os
import shutil
import zipfile

from src.models.base import ProjectModel

logger = logging.getLogger(__name__)


class DemoProjectManager:
    @staticmethod
    def create_crystal_forest_demo() -> ProjectModel:
        logger.info("Bootstrapping Demo Project: The Crystal Forest")
        proj = ProjectModel(name="The Crystal Forest")

        # In a real app, this would deeply populate models for Story, Characters, etc.
        # For this implementation, we just set the high level project data.
        proj.resolution = (1920, 1080)
        proj.fps = 24

        return proj

    @staticmethod
    def generate_demo_project(output_path: str = "projects/demo_project.zanime") -> str:
        """Generates the demo project archive if missing or requested."""
        abs_output = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(abs_output), exist_ok=True)

        demo_dir = os.path.join(os.path.dirname(abs_output), "demo_project")
        os.makedirs(demo_dir, exist_ok=True)

        project_data = {
            "name": "The Crystal Forest (Demo)",
            "project_version": "1.0.0",
            "version": "1.0.0",
            "resolution": [1920, 1080],
            "fps": 24,
            "author": "ZANIME Studios",
            "description": "An epic 2D anime fantasy production demo set in the enchanted realm of Eldoria.",
            "art_style": "Anime",
            "language": "English",
        }

        subdirs = {
            "story": {
                "story.json": {
                    "title": "The Crystal Forest",
                    "logline": "A young warrior and a mystic guide journey into the heart of Eldoria to prevent the eclipse of the Crystal Tree.",
                    "act_1": "Akira discovers an ancient glowing relic at the edge of the Whispering Forest.",
                    "act_2": "Guided by Sakura, they navigate the ruins of Eldoria while pursued by Kael's shadow knights.",
                    "act_3": "At the Crystal Altar, Akira restores the light, saving Eldoria from eternal darkness.",
                }
            },
            "script": {
                "screenplay.json": {
                    "scenes": [
                        {
                            "scene_num": 1,
                            "slugline": "EXT. ANCIENT RUINS - DAY",
                            "dialogue": [
                                {
                                    "character": "AKIRA",
                                    "line": "Look at these glowing runes... Eldoria is waking up.",
                                },
                                {
                                    "character": "SAKURA",
                                    "line": "Be careful, Akira. The shadow knights are near.",
                                },
                            ],
                        }
                    ]
                }
            },
            "characters": {
                "characters.json": [
                    {
                        "name": "Akira",
                        "role": "Protagonist",
                        "height_cm": 175,
                        "palette": ["#ff4500", "#1e90ff", "#ffffff"],
                    },
                    {
                        "name": "Sakura",
                        "role": "Mystic Guide",
                        "height_cm": 165,
                        "palette": ["#ffb6c1", "#8a2be2", "#f0fff0"],
                    },
                    {
                        "name": "Kael",
                        "role": "Shadow Knight",
                        "height_cm": 188,
                        "palette": ["#2f4f4f", "#8b0000", "#000000"],
                    },
                ]
            },
            "backgrounds": {
                "worlds.json": [
                    {"name": "Whispering Forest Canopy", "tod": "Day", "biome": "Enchanted Forest"},
                    {"name": "Crystal Altar Ruins", "tod": "Night", "biome": "Ancient Sanctuary"},
                ]
            },
            "props": {
                "props.json": [
                    {"name": "Eldoria Crystal Staff", "category": "Weapons"},
                    {"name": "Ancient Relic Map", "category": "Artifacts"},
                    {"name": "Spirit Pendant", "category": "Accessories"},
                ]
            },
            "storyboard": {
                "storyboard.json": [
                    {"shot_id": "SHOT-01", "shot_type": "Wide", "action": "Akira walks into ancient ruins"},
                    {"shot_id": "SHOT-02", "shot_type": "Close-Up", "action": "Sakura warns of shadow knights"},
                ]
            },
            "scenes": {
                "scenes.json": [
                    {"scene_name": "Forest Gateway", "layers": ["BG_Forest", "Akira_Walk", "FG_Leaves"]}
                ]
            },
            "voice": {
                "dialogue_audio.json": [
                    {"speaker": "Akira", "file": "akira_line_01.wav", "duration_sec": 3.2}
                ]
            },
            "music": {
                "soundtrack.json": [
                    {"track_name": "Crystal Forest Theme", "bpm": 90, "genre": "Orchestral Anime"}
                ]
            },
            "render": {
                "settings.json": {
                    "format": "MP4",
                    "codec": "H.264",
                    "resolution": "1080p",
                    "framerate": 24
                }
            },
            "assets": {},
            "thumbnails": {},
        }

        # Write project.json
        with open(os.path.join(demo_dir, "project.json"), "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=4)

        # Write domain JSONs inside demo_dir
        for sub, files in subdirs.items():
            sub_path = os.path.join(demo_dir, sub)
            os.makedirs(sub_path, exist_ok=True)
            for fname, content in files.items():
                with open(os.path.join(sub_path, fname), "w", encoding="utf-8") as f:
                    json.dump(content, f, indent=4)

        # Create zip package
        with zipfile.ZipFile(abs_output, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(demo_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, demo_dir)
                    zipf.write(file_path, arcname)

        if os.path.exists(demo_dir):
            shutil.rmtree(demo_dir)

        logger.info("Complete Demo Project package generated at %s", abs_output)
        return abs_output

    @staticmethod
    def ensure_demo_project(output_path: str = "projects/demo_project.zanime") -> str:
        """Ensures that the demo project archive exists on disk, generating it if necessary."""
        abs_output = os.path.abspath(output_path)
        if not os.path.exists(abs_output):
            return DemoProjectManager.generate_demo_project(output_path)
        return abs_output


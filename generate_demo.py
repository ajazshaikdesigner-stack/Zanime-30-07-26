import os
import zipfile
import json
import shutil

demo_dir = "projects/demo_project"
os.makedirs(demo_dir, exist_ok=True)

project_data = {
    "name": "Demo Project",
    "version": "1.0",
    "resolution": [1920, 1080],
    "fps": 24
}

with open(os.path.join(demo_dir, "project.json"), "w") as f:
    json.dump(project_data, f, indent=4)

with zipfile.ZipFile("projects/demo_project.zanime", 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(os.path.join(demo_dir, "project.json"), "project.json")

shutil.rmtree(demo_dir)
print("demo_project.zanime generated.")

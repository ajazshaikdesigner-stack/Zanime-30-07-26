import os
import zipfile


def zip_project(source_dir, output_filename):
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Exclude venv and __pycache__
            dirs[:] = [
                d
                for d in dirs
                if d not in ("venv", "__pycache__", ".git", ".pytest_cache")
            ]

            for file in files:
                if file.endswith(".pyc") or file == output_filename.split("/")[-1]:
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)


if __name__ == "__main__":
    zip_project("e:/Zanime", "e:/Zanime_Project.zip")
    print("Project zipped successfully to e:/Zanime_Project.zip")

"""
Commercial Installer & Packaging Builder — Phase 5 Release Pipeline.

Generates:
  1. InnoSetup Installer script (.iss) with .zanime file association & shortcuts
  2. Portable ZIP Distribution packager
  3. Dependency Checker (PySide6, Qt6, FFmpeg, Ollama)
"""

import json
import os
import shutil
import sys
import zipfile

INNO_SETUP_SCRIPT_TEMPLATE = (
    "[Setup]\n"
    "AppName=ZANIME Desktop Animation Studio\n"
    "AppVersion=1.0.0\n"
    "AppPublisher=ZANIME Team\n"
    "AppPublisherURL=https://zanime.studio\n"
    "DefaultDirName={autopf}\\ZanimeStudio\n"
    "DefaultGroupName=ZANIME Studio\n"
    "OutputBaseFilename=zanime-1.0.0-windows-installer\n"
    "Compression=lzma2/ultra64\n"
    "SolidCompression=yes\n"
    "WizardStyle=modern\n"
    "ChangesAssociations=yes\n\n"
    "[Languages]\n"
    'Name: "english"; MessagesFile: "compiler:Default.isl"\n\n'
    "[Tasks]\n"
    'Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked\n'
    'Name: "fileassoc"; Description: "Associate .zanime project files with ZANIME Studio"; GroupDescription: "File Associations"\n\n'
    "[Files]\n"
    'Source: "dist\\ZanimeStudio\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs\n\n'
    "[Icons]\n"
    'Name: "{group}\\ZANIME Studio"; Filename: "{app}\\ZanimeStudio.exe"\n'
    'Name: "{group}\\Uninstall ZANIME Studio"; Filename: "{uninstallexe}"\n'
    'Name: "{autodesktop}\\ZANIME Studio"; Filename: "{app}\\ZanimeStudio.exe"; Tasks: desktopicon\n\n'
    "[Registry]\n"
    'Root: HKCR; Subkey: ".zanime"; ValueType: string; ValueName: ""; ValueData: "ZanimeProjectFile"; Flags: uninsdeletevalue; Tasks: fileassoc\n'
    'Root: HKCR; Subkey: "ZanimeProjectFile"; ValueType: string; ValueName: ""; ValueData: "ZANIME Project File"; Flags: uninsdeletekey; Tasks: fileassoc\n'
    'Root: HKCR; Subkey: "ZanimeProjectFile\\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\\ZanimeStudio.exe,0"; Tasks: fileassoc\n'
    'Root: HKCR; Subkey: "ZanimeProjectFile\\shell\\open\\command"; ValueType: string; ValueName: ""; ValueData: """"{app}\\ZanimeStudio.exe"" """"%1"""""; Tasks: fileassoc\n'
)


def check_dependencies() -> dict:
    """Verify presence of core system dependencies for installation."""
    report = {
        "python": sys.version.split()[0],
        "pyside6": False,
        "ffmpeg": False,
        "ollama": False,
    }

    try:
        import PySide6
        report["pyside6"] = True
    except ImportError:
        pass

    ffmpeg_path = shutil.which("ffmpeg")
    report["ffmpeg"] = bool(ffmpeg_path)

    ollama_path = shutil.which("ollama")
    report["ollama"] = bool(ollama_path)

    return report


def build_installer():
    print("==================================================")
    print(" ZANIME 1.0 GOLD MASTER -- COMMERCIAL BUILD ENGINE ")
    print("==================================================")

    # 1. Dependency Check
    print("[1/5] Checking System & Build Dependencies...")
    deps = check_dependencies()
    for k, v in deps.items():
        status = "[OK] Installed" if v else "[WARN] Missing (Fallback mode)"
        print(f"      * {k.upper()}: {status}")

    # 2. InnoSetup Script Generation
    iss_path = "zanime_installer.iss"
    print(f"[2/5] Generating InnoSetup Script '{iss_path}'...")
    with open(iss_path, "w", encoding="utf-8") as f:
        f.write(INNO_SETUP_SCRIPT_TEMPLATE.strip())
    print("      [OK] Created file association for .zanime extension")
    print("      [OK] Added Start Menu & Desktop Shortcut definitions")
    print("      [OK] Added registry uninstaller keys")

    # 3. Portable Edition Packager
    portable_zip = "dist/zanime-1.0.0-portable.zip"
    os.makedirs("dist", exist_ok=True)
    print(f"[3/5] Packaging Portable Edition '{portable_zip}'...")

    with zipfile.ZipFile(portable_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add core launcher and configs
        for root, dirs, files in os.walk("src"):
            for file in files:
                filepath = os.path.join(root, file)
                zipf.write(filepath, os.path.relpath(filepath, "."))
        if os.path.isfile("run.py"):
            zipf.write("run.py")
        if os.path.isfile("launch.bat"):
            zipf.write("launch.bat")

    print("      [OK] Created portable ZIP package")


    # 4. Generate Build Summary JSON
    manifest = {
        "app_name": "ZANIME Desktop Animation Studio",
        "version": "1.0.0",
        "build_date": "2026-07-30",
        "installer_iss": iss_path,
        "portable_zip": portable_zip,
        "dependencies": deps,
    }
    with open("dist/build_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print("[4/5] Saved Build Manifest to 'dist/build_manifest.json'")
    print("[5/5] BUILD COMPLETE. Ready for Release Distribution.")
    print("==================================================")


if __name__ == "__main__":
    build_installer()

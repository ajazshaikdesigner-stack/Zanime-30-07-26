[Setup]
AppName=ZANIME Desktop Animation Studio
AppVersion=1.0.0
AppPublisher=ZANIME Team
AppPublisherURL=https://zanime.studio
DefaultDirName={autopf}\ZanimeStudio
DefaultGroupName=ZANIME Studio
OutputBaseFilename=zanime-1.0.0-windows-installer
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ChangesAssociations=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "fileassoc"; Description: "Associate .zanime project files with ZANIME Studio"; GroupDescription: "File Associations"

[Files]
Source: "dist\ZanimeStudio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ZANIME Studio"; Filename: "{app}\ZanimeStudio.exe"
Name: "{group}\Uninstall ZANIME Studio"; Filename: "{uninstallexe}"
Name: "{autodesktop}\ZANIME Studio"; Filename: "{app}\ZanimeStudio.exe"; Tasks: desktopicon

[Registry]
Root: HKCR; Subkey: ".zanime"; ValueType: string; ValueName: ""; ValueData: "ZanimeProjectFile"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCR; Subkey: "ZanimeProjectFile"; ValueType: string; ValueName: ""; ValueData: "ZANIME Project File"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCR; Subkey: "ZanimeProjectFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\ZanimeStudio.exe,0"; Tasks: fileassoc
Root: HKCR; Subkey: "ZanimeProjectFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """"{app}\ZanimeStudio.exe"" """"%1"""""; Tasks: fileassoc
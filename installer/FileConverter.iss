; File Converter - Inno Setup script
;
; Packages the PyInstaller folder build into a single FileConverter-Setup.exe.
; Build dist\FileConverter first, then compile this file with ISCC.exe.

#define MyAppName "File Converter"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Muhammad Abdullah"
#define MyAppExeName "FileConverter.exe"
#define MyAppUrl "https://github.com/abdullah200514/file-converter"

; Parent key for the per-extension right-click entries.
#define MenuRoot "Software\Classes\SystemFileAssociations"

[Setup]
; Identifies this app to Windows across upgrades. Never change it after release.
; The doubled opening brace is Inno Setup's escape for a literal "{".
AppId={{16084D09-35A9-4962-BC03-906393C30AAF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppUrl}
AppSupportURL={#MyAppUrl}

; Per-user install: no administrator prompt. With this setting {autopf}
; resolves to %LOCALAPPDATA%\Programs rather than Program Files.
PrivilegesRequired=lowest
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes

; Paths are relative to this script, which lives in installer\.
OutputDir=..\installer_output
OutputBaseFilename=FileConverter-Setup

Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

; Tells Explorer to refresh after the file-type menu entries change.
ChangesAssociations=yes

[Files]
; The whole PyInstaller output: the exe plus its _internal folder.
Source: "..\dist\FileConverter\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; FFmpeg goes next to the exe, which is where find_ffmpeg() looks first.
; vendor\ is ignored by Git: the exe is too large for GitHub. The exact build
; and its checksum are recorded in THIRD_PARTY_NOTICES.txt.
Source: "..\vendor\ffmpeg\ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\vendor\ffmpeg\LICENSE.txt"; DestDir: "{app}\licenses"; DestName: "LGPL-3.0.txt"; Flags: ignoreversion
Source: "..\vendor\ffmpeg\GPL-3.0.txt"; DestDir: "{app}\licenses"; Flags: ignoreversion
Source: "THIRD_PARTY_NOTICES.txt"; DestDir: "{app}"; Flags: ignoreversion

; No [Icons] section: the app needs a file passed to it, so a Start Menu
; shortcut would open nothing. It is launched from the right-click menu.

[Registry]
; uninsdeletekey is set only on our own FileConverter key. Setting it on the
; parent "shell" key could remove other applications' menu entries.
Root: HKCU; Subkey: "{#MenuRoot}\.mp4\shell\FileConverter"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Convert to..."; Flags: uninsdeletekey
Root: HKCU; Subkey: "{#MenuRoot}\.mp4\shell\FileConverter\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

Root: HKCU; Subkey: "{#MenuRoot}\.mp3\shell\FileConverter"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Convert to..."; Flags: uninsdeletekey
Root: HKCU; Subkey: "{#MenuRoot}\.mp3\shell\FileConverter\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

Root: HKCU; Subkey: "{#MenuRoot}\.wav\shell\FileConverter"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Convert to..."; Flags: uninsdeletekey
Root: HKCU; Subkey: "{#MenuRoot}\.wav\shell\FileConverter\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

Root: HKCU; Subkey: "{#MenuRoot}\.png\shell\FileConverter"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Convert to..."; Flags: uninsdeletekey
Root: HKCU; Subkey: "{#MenuRoot}\.png\shell\FileConverter\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

Root: HKCU; Subkey: "{#MenuRoot}\.docx\shell\FileConverter"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Convert to..."; Flags: uninsdeletekey
Root: HKCU; Subkey: "{#MenuRoot}\.docx\shell\FileConverter\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

Root: HKCU; Subkey: "{#MenuRoot}\.pptx\shell\FileConverter"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Convert to..."; Flags: uninsdeletekey
Root: HKCU; Subkey: "{#MenuRoot}\.pptx\shell\FileConverter\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

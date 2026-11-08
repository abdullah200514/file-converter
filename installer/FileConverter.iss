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

; Pinned LibreOffice download. The archive link stays valid after this version
; stops being the current release; the checksum proves the file is the right one.
#define LibreOfficeUrl "https://downloadarchive.documentfoundation.org/libreoffice/old/26.8.2.2/win/x86_64/LibreOffice_26.8.2.2_Win_x86-64.msi"
#define LibreOfficeSha256 "ff4b911403b67ee9e6249f820f9782c44bb32c94fdaa45b0da53a8e419e5307a"

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

; The bundled FFmpeg and LibreOffice download are both 64-bit.
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

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

[Tasks]
; Only offered when LibreOffice is missing. Ticked by default because two of
; the six file types need it; the label states the download size.
Name: "libreoffice"; Description: "Install LibreOffice (required for Word and PowerPoint conversion, 376 MB download, needs administrator approval)"; Check: not LibreOfficeInstalled

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

[Code]
var
  DownloadPage: TDownloadWizardPage;
  LibreOfficeDownloaded: Boolean;

// Checks the same locations as find_libreoffice() in converter/convert.py.
function LibreOfficeInstalled: Boolean;
begin
  Result := FileExists(ExpandConstant('{commonpf64}\LibreOffice\program\soffice.exe'))
    or FileExists(ExpandConstant('{commonpf32}\LibreOffice\program\soffice.exe'));
end;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage(
    'Downloading LibreOffice',
    'This can take several minutes, depending on your connection.', nil);
  DownloadPage.ShowBaseNameInsteadOfUrl := True;
end;

// Download before installing starts, so the user can still cancel. A failure
// only skips LibreOffice: the rest of the app works without it.
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if (CurPageID = wpReady) and WizardIsTaskSelected('libreoffice') then
  begin
    DownloadPage.Clear;
    DownloadPage.Add('{#LibreOfficeUrl}', 'LibreOffice.msi', '{#LibreOfficeSha256}');
    DownloadPage.Show;
    try
      try
        DownloadPage.Download;
        LibreOfficeDownloaded := True;
        Log('LibreOffice download verified.');
      except
        Log('LibreOffice download failed: ' + GetExceptionMessage);
        if not DownloadPage.AbortedByUser then
          SuppressibleMsgBox(
            'LibreOffice could not be downloaded, so it will be skipped.' + #13#10#13#10 +
            'File Converter will still be installed. Word and PowerPoint ' +
            'conversion will need LibreOffice from libreoffice.org.',
            mbInformation, MB_OK, IDOK);
      end;
    finally
      DownloadPage.Hide;
    end;
  end;
end;

procedure InstallLibreOffice;
var
  Params: String;
  ResultCode: Integer;
begin
  WizardForm.StatusLabel.Caption := 'Installing LibreOffice. This can take several minutes...';
  WizardForm.ProgressGauge.Style := npbstMarquee;
  try
    // REGISTER_NO_MSO_TYPES=1 leaves the user's Word and PowerPoint file
    // associations alone. Setup itself stays per-user: "runas" asks for
    // administrator approval for this one step only.
    Params := '/i "' + ExpandConstant('{tmp}\LibreOffice.msi') + '"' +
      ' /qb /norestart ALLUSERS=1 CREATEDESKTOPLINK=0 REGISTER_NO_MSO_TYPES=1' +
      ' QUICKSTART=0 RebootYesNo=No REBOOT=ReallySuppress' +
      ' /l* "' + ExpandConstant('{%TEMP}\FileConverter-LibreOffice-install.log') + '"';
    if ShellExec('runas', 'msiexec.exe', Params, '', SW_SHOWNORMAL,
      ewWaitUntilTerminated, ResultCode) then
      Log('msiexec finished with code ' + IntToStr(ResultCode))
    else
      Log('msiexec could not start, or approval was refused: ' + IntToStr(ResultCode));
  finally
    WizardForm.ProgressGauge.Style := npbstNormal;
  end;

  // Trust the result on disk rather than an exit code.
  if LibreOfficeInstalled then
    Log('LibreOffice install confirmed on disk.')
  else
  begin
    Log('LibreOffice was not found after installing.');
    SuppressibleMsgBox(
      'LibreOffice was not installed, so Word and PowerPoint conversion will ' +
      'not work yet. Everything else is ready.' + #13#10#13#10 +
      'You can install it at any time from libreoffice.org.',
      mbInformation, MB_OK, IDOK);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssPostInstall) and LibreOfficeDownloaded then
    InstallLibreOffice;
end;

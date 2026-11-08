
# File Converter - Windows Context Menu Installer

$ErrorActionPreference = "Stop"

# Locate project files
$ProjectRoot = $PSScriptRoot

$PythonwPath = Join-Path $ProjectRoot ".venv\Scripts\pythonw.exe"
$GuiPath = Join-Path $ProjectRoot "converter\gui.py"

# Check required files exist
if (-not (Test-Path -LiteralPath $PythonwPath)) {
    throw "pythonw.exe not found. Check your virtual environment."
}

if (-not (Test-Path -LiteralPath $GuiPath)) {
    throw "gui.py not found."
}

# Supported input extensions
$Extensions = @(
    ".mp4",
    ".mp3",
    ".wav",
    ".png",
    ".docx",
    ".pptx"
)

# Register the context menu for each extension
foreach ($Extension in $Extensions) {

    $MenuPath = "HKCU:\Software\Classes\SystemFileAssociations\$Extension\shell\FileConverter"
    $CommandPath = Join-Path $MenuPath "command"

    # Create registry keys
    New-Item -Path $CommandPath -Force | Out-Null

    # Set menu display name
    New-ItemProperty `
        -Path $MenuPath `
        -Name "MUIVerb" `
        -Value "Convert to..." `
        -PropertyType String `
        -Force | Out-Null

    # Build the command Windows will execute
    $Command = '"{0}" "{1}" "%1"' -f $PythonwPath, $GuiPath

    # Set the default command
    Set-Item -Path $CommandPath -Value $Command -Type String

    Write-Host "Registered Convert to... for $Extension"
}

Write-Host ""
Write-Host "File Converter context menu installed successfully!"

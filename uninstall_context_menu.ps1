
# File Converter - Windows Context Menu Uninstaller

$ErrorActionPreference = "Stop"

# Supported input extensions
$Extensions = @(
    ".mp4",
    ".mp3",
    ".wav",
    ".png",
    ".docx",
    ".pptx"
)

# Remove the context menu entries
foreach ($Extension in $Extensions) {

    $MenuPath = "HKCU:\Software\Classes\SystemFileAssociations\$Extension\shell\FileConverter"

    if (Test-Path $MenuPath) {

        Remove-Item -Path $MenuPath -Recurse -Force

        Write-Host "Removed Convert to... for $Extension"
    }
    else {
        Write-Host "No registration found for $Extension"
    }
}

Write-Host ""
Write-Host "File Converter context menu uninstalled successfully!"

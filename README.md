# File Converter

A Windows file converter that lives in the File Explorer right-click menu. Right-click a file, choose **Convert to...**, pick an output format, and the converted file is saved next to the original.

![File Converter window](docs/screenshot.png)

## How it works for the user

1. Right-click a supported file in Windows Explorer (on Windows 11, under **Show more options**).
2. Choose **Convert to...**.
3. A small window opens showing the file and only the formats it can be converted to.
4. Choose a format and press **Convert**. The window shows live progress, then **Open file** and **Show in folder** buttons.
5. If the output file already exists, the app asks before replacing it.

## Status

Working on Windows 11. This is a learning and portfolio project, and it has not been packaged for other users yet.

### Supported conversions

Every route below has been tested through the Explorer right-click workflow.

| Input | Output | Tool |
|---|---|---|
| MP4 | MP3, WAV | FFmpeg |
| MP3 | WAV | FFmpeg |
| WAV | MP3 | FFmpeg |
| PNG | JPG, WebP | FFmpeg |
| DOCX | PDF | LibreOffice |
| PPTX | PDF | LibreOffice |

Also tested: filenames and folder names containing spaces, and the overwrite confirmation.

## Architecture

The conversion engine is independent of the interface.

- `converter/convert.py` is the engine. `convert_file()` validates the input, looks up the tool in the `CONVERSIONS` table, runs it with `subprocess`, and returns the output path or raises a meaningful error. An optional `on_status` callback reports progress.
- `converter/gui.py` is a Tkinter window. It reads the supported formats from the same `CONVERSIONS` table, runs conversions on a background thread so the window stays responsive, and shows the engine's status messages.
- `install_context_menu.ps1` and `uninstall_context_menu.ps1` add and remove the Explorer menu entries. They write to `HKCU`, so no administrator rights are needed, and they launch the GUI through `pythonw.exe` so no console window appears.

The actual conversion is done by existing tools, not custom code:

- [FFmpeg](https://ffmpeg.org/) for audio, video and images.
- [LibreOffice](https://www.libreoffice.org/) in headless mode for Office documents.

## Requirements

- Windows 10 or 11
- Python 3.10 or newer
- FFmpeg on PATH
- LibreOffice

Install the external tools with winget:

```powershell
winget install Gyan.FFmpeg
winget install -e --id TheDocumentFoundation.LibreOffice
```

The code expects LibreOffice at `C:\Program Files\LibreOffice\program\soffice.exe`. If yours is elsewhere, change `LIBREOFFICE_PATH` in `converter/convert.py`.

There are no Python packages to install. The project uses only the standard library.

## Setup

```powershell
git clone https://github.com/abdullah200514/file-converter.git
cd file-converter
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Add the right-click menu entries:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\install_context_menu.ps1
```

Remove them again with `.\uninstall_context_menu.ps1`. The entries point at this folder's virtual environment, so run the installer again if you move the project.

## Command-line use

The engine also works without the GUI:

```powershell
python converter\convert.py "path\to\video.mp4" mp3
python converter\convert.py "path\to\document.docx" pdf
```

To open the GUI directly:

```powershell
python -m converter.gui "path\to\file.mp4"
```

## Running tests

```powershell
python -m unittest discover -s tests -v
```

The five tests cover missing arguments, a nonexistent input file, an unsupported conversion, MP4 to WAV, and DOCX to PDF. The MP4 test generates its own one-second file with FFmpeg, and the DOCX fixture is in `tests/fixtures/`. FFmpeg and LibreOffice must be installed for the integration tests to pass.

The GUI and the Explorer integration are tested manually.

## Project structure

```text
file-converter/
├── converter/
│   ├── __init__.py
│   ├── convert.py
│   └── gui.py
├── docs/
│   └── screenshot.png
├── tests/
│   ├── fixtures/
│   │   └── test.docx
│   └── test_convert.py
├── samples/                       # local test files, excluded from Git
├── install_context_menu.ps1
├── uninstall_context_menu.ps1
├── .gitignore
├── README.md
└── requirements.txt
```

## How this was built

I used Claude (an AI assistant) throughout this project, mainly as a learning tool. It explained the concepts and the reasoning behind each step, and I worked through the engine step by step, making changes and testing them myself.

The front end is different: **the GUI (`converter/gui.py`) was written by Claude.** The design direction was mine. I chose the minimal look, the "from → to" layout, the live status messages instead of popups, the Open file and Show in folder buttons, and asking before overwriting an existing file. I also tweaked parts of the code myself. I tested each version through the real Explorer right-click workflow and sent back screenshots and errors until it matched what I wanted.

I'm being upfront about this because I want the repo to show what I built and what I'm still learning. The problems I hit and fixed along the way are in the commit messages. Examples: a console window appearing on every conversion, a stale file causing a keyword-argument error, and a progress bar that left a block behind after finishing.

## Planned

- Logging.
- More audio, video, image and document formats.
- PDF to editable DOCX and OCR for scanned PDFs.
- Batch conversion.
- Packaging with an installer, so it can be used without a Python setup.

## Author

Built by Muhammad Abdullah as a learning and portfolio project.
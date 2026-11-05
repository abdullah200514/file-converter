# File Converter

A Windows file-conversion tool built with Python. The goal is to let users right-click a file in Windows Explorer, select **Convert to...**, choose an output format, and have the converted file saved alongside the original.

The project currently has a working command-line converter. Windows Explorer integration and the format-selection interface are planned.

## Status

**Working CLI prototype.** FFmpeg and LibreOffice are integrated, and automated tests cover the main conversion workflows.

## Supported conversions

| Input format | Output format | Conversion tool |
|---|---|---|
| MP4 | MP3, WAV | FFmpeg |
| MP3 | WAV | FFmpeg |
| WAV | MP3 | FFmpeg |
| PNG | JPG, WebP | FFmpeg |
| DOCX | PDF | LibreOffice |
| PPTX | PDF | LibreOffice |

Some configured conversion routes still require additional testing.

## Features

- Detects input file types using their extensions.
- Validates requested output formats.
- Automatically selects the appropriate conversion tool.
- Saves converted files next to the original file.
- Handles missing arguments, nonexistent files and conversion failures.
- Includes automated tests using Python's `unittest` framework.

## How it works

The application is written in Python and delegates the actual conversion work to established external tools.

- [FFmpeg](https://ffmpeg.org/) handles audio, video and image conversions.
- [LibreOffice](https://www.libreoffice.org/) handles Office document conversions in headless mode.

Python identifies the input extension, checks the requested output format against a conversion lookup table, selects the appropriate tool and executes it using `subprocess`.

The planned Windows integration will use registry entries to add a **Convert to...** option to the Windows Explorer context menu.

## Requirements

- Windows 10 or 11.
- Python 3.10 or newer.
- Git.
- FFmpeg installed and available on PATH.
- LibreOffice installed.

**Note:** The current implementation expects LibreOffice at:

`C:\Program Files\LibreOffice\program\soffice.exe`

If LibreOffice is installed elsewhere, update `LIBREOFFICE_PATH` in `converter/convert.py`.

The project currently uses Python's standard library and does not require additional Python packages.

## Setup

Clone the repository:

```powershell
git clone https://github.com/abdullah200514/file-converter.git
cd file-converter
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Verify the external tools are accessible:

```powershell
ffmpeg -version
```

LibreOffice can be checked using:

```powershell
& "C:\Program Files\LibreOffice\program\soffice.exe" --version
```

## Usage

Run the converter from the project root:

```powershell
python converter\convert.py "path\to\input_file.mp4" mp3
```

For a Word document:

```powershell
python converter\convert.py "path\to\document.docx" pdf
```

The output file is saved in the same directory as the original, using the requested extension.

## Running tests

The project uses Python's built-in `unittest` framework.

Run the automated test suite:

```powershell
python -m unittest discover -s tests -v
```

The tests cover:

- Missing command-line arguments.
- Nonexistent input files.
- Unsupported conversions.
- MP4 to WAV conversion.
- DOCX to PDF conversion.

FFmpeg and LibreOffice must be installed to run the full integration test suite.

**Test sample requirement:** The current MP4 integration tests use `samples/00081.mp4`. The `samples/` directory is excluded from Git, so a fresh clone must supply an MP4 at that location before running the full suite. The generic DOCX fixture is included in `tests/fixtures/`.

## Project structure

```text
file-converter/
├── converter/
│   ├── __init__.py
│   └── convert.py
├── tests/
│   ├── fixtures/
│   │   └── test.docx
│   └── test_convert.py
├── samples/              # Local test files, excluded from Git
├── .gitignore
├── README.md
└── requirements.txt
```

## Planned features

- Windows Explorer right-click context menu integration.
- A popup interface for selecting output formats.
- Expanded image, audio and video conversion support.
- Additional document conversion formats.
- Improved error handling and conversion reliability.
- More comprehensive automated tests.

## Author

Built by Muhammad Abdullah as a learning and portfolio project.

[GitHub Repository](https://github.com/abdullah200514/file-converter)
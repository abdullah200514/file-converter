# File Converter

A right-click file converter for Windows. Right-click any file, choose what you want it converted to, and get the result saved next to the original (for example Word to PDF, or MP4 to MP3).

> **Status:** early development. The project structure is set up and the first conversions are being built.

## Planned features

- Convert video to audio (MP4 to MP3) and between common video and audio formats
- Convert documents to PDF (DOCX, PPTX)
- Convert between image formats
- Windows Explorer right-click menu integration
- Only offer output formats that make sense for the selected file

## How it works

The project is a Python program that detects the type of the file it is given and hands the actual conversion to an established tool:

- [FFmpeg](https://ffmpeg.org/) for audio, video and images
- [LibreOffice](https://www.libreoffice.org/) (headless mode) for documents

A set of Windows registry entries adds the "Convert to..." option to the right-click menu and passes the selected file's path to the program.

## Requirements

- Windows 10 or 11
- Python 3.10 or newer
- FFmpeg available on your PATH

## Setup

```
git clone https://github.com/abdullah200514/file-converter.git
cd file-converter
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Project structure

```
file-converter/
├── converter/      # conversion code
├── tests/          # tests
├── requirements.txt
└── README.md
```

## Author

Built by Muhammad Abdullah as a learning project. [GitHub](https://github.com/abdullah200514)
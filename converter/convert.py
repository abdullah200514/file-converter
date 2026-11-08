import sys
import subprocess
from pathlib import Path


# Path to LibreOffice executable
LIBREOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"


# Supported conversions and conversion tools
CONVERSIONS = {
    ".mp4": {
        "tool": "ffmpeg",
        "outputs": ["mp3", "wav"],
    },
    ".mp3": {
        "tool": "ffmpeg",
        "outputs": ["wav"],
    },
    ".wav": {
        "tool": "ffmpeg",
        "outputs": ["mp3"],
    },
    ".png": {
        "tool": "ffmpeg",
        "outputs": ["jpg", "webp"],
    },
    ".docx": {
        "tool": "libreoffice",
        "outputs": ["pdf"],
    },
    ".pptx": {
        "tool": "libreoffice",
        "outputs": ["pdf"],
    },
}


# Main conversion function.
# on_status is optional: a function that receives progress messages.
def convert_file(input_path, target_format, on_status=None):

    def report(message):
        if on_status is not None:
            on_status(message)

    report("Checking file...")

    input_path = Path(input_path)
    target_format = target_format.lower().lstrip(".")

    # Check whether input file exists
    if not input_path.is_file():
        raise FileNotFoundError(f"File not found: {input_path}")

    # Detect input format
    input_format = input_path.suffix.lower()

    # Validate input format
    if input_format not in CONVERSIONS:
        raise ValueError(f"Unsupported input format: {input_format}")

    # Validate target format
    supported_formats = CONVERSIONS[input_format]["outputs"]

    if target_format not in supported_formats:
        raise ValueError(
            f"Cannot convert {input_format} to {target_format}.\n"
            f"Supported formats: {supported_formats}"
        )

    # Select conversion tool
    selected_tool = CONVERSIONS[input_format]["tool"]

    # Generate output path
    output_path = input_path.with_suffix(f".{target_format}")

    # Run the appropriate conversion tool
    try:
        if selected_tool == "ffmpeg":
            report("Converting with FFmpeg...")

            subprocess.run(
                [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel", "error",
                    "-y",
                    "-i", str(input_path),
                    str(output_path)
                ],
                check=True,
                capture_output=True,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

        elif selected_tool == "libreoffice":
            report("Converting with LibreOffice (can take a few seconds)...")

            subprocess.run(
                [
                    LIBREOFFICE_PATH,
                    "--headless",
                    "--convert-to", target_format,
                    "--outdir", str(output_path.parent),
                    str(input_path)
                ],
                check=True,
                capture_output=True,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

        report("Checking output...")

        if not output_path.is_file():
            raise RuntimeError("Conversion finished but output file was not created.")

    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            "Conversion failed. Please check your input file and target format."
        ) from error

    except FileNotFoundError as error:
        raise RuntimeError(
            f"Required conversion tool not found: {selected_tool}"
        ) from error

    return output_path


# Command-line interface
def main():

    if len(sys.argv) != 3:
        print("Usage: python convert.py <input_file> <target_format>")
        return 1

    try:
        output_path = convert_file(sys.argv[1], sys.argv[2], on_status=print)
        print(f"Conversion successful: {output_path}")
        return 0

    except (FileNotFoundError, ValueError, RuntimeError) as error:
        print(error)
        return 1


# Only run main when this file is executed directly
if __name__ == "__main__":
    sys.exit(main())
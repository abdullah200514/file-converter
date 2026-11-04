import sys
import subprocess
from pathlib import Path

# Get input file and target format
input_path = Path(sys.argv[1])
target_format = sys.argv[2].lower()

# Detect input file extension
input_format = input_path.suffix.lower()

# Supported conversions
CONVERSIONS = {
    ".mp4": ["mp3", "wav"],
    ".mp3": ["wav"],
    ".wav": ["mp3"],
    ".png": ["jpg", "webp"],
}

# Validate input format
if input_format not in CONVERSIONS:
    print(f"Unsupported input format: {input_format}")
    sys.exit(1)

# Validate target format
if target_format not in CONVERSIONS[input_format]:
    print(f"Cannot convert {input_format} to {target_format}.")
    print("Supported formats:", CONVERSIONS[input_format])
    sys.exit(1)

# Generate output path
output_path = input_path.with_suffix(f".{target_format}")

# Run FFmpeg
subprocess.run(
    ["ffmpeg", "-y", "-i", str(input_path), str(output_path)],
    check=True
)
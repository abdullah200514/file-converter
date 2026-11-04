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

# Display supported output formats
print("Input format:", input_format)
print("Supported output formats:", CONVERSIONS[input_format])

# Generate output path
output_path = input_path.with_suffix(f".{target_format}")

# Run FFmpeg
subprocess.run(
    ["ffmpeg", "-y", "-i", str(input_path), str(output_path)],
    check=True
)
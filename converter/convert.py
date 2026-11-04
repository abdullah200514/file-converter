import sys
import subprocess
from pathlib import Path

# Get input file and target format
input_path = Path(sys.argv[1])
target_format = sys.argv[2].lower()

# Detect input file extension
input_format = input_path.suffix.lower()

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
}

# Validate input format
if input_format not in CONVERSIONS:
    print(f"Unsupported input format: {input_format}")
    sys.exit(1)

# Validate target format
if target_format not in CONVERSIONS[input_format]["outputs"]:
    print(f"Cannot convert {input_format} to {target_format}.")
    print("Supported formats:", CONVERSIONS[input_format]["outputs"])
    sys.exit(1)

# Select conversion tool
selected_tool = CONVERSIONS[input_format]["tool"]
print("Selected conversion tool:", selected_tool)

# Generate output path
output_path = input_path.with_suffix(f".{target_format}")

# Run FFmpeg
subprocess.run(
    ["ffmpeg", "-y", "-i", str(input_path), str(output_path)],
    check=True
)
import sys
import subprocess
from pathlib import Path

# Get input file and target format
input_path = Path(sys.argv[1])
target_format = sys.argv[2]

# Generate output path
output_path = input_path.with_suffix(f".{target_format}")

# Run FFmpeg
subprocess.run(
    ["ffmpeg", "-y", "-i", str(input_path), str(output_path)],
    check=True
)
import sys
import subprocess
from pathlib import Path

input_path = Path(sys.argv[1])
output_path = input_path.with_suffix(".mp3")

subprocess.run(
    ["ffmpeg", "-y", "-i", str(input_path), str(output_path)],
    check=True
)
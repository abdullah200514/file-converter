import subprocess

subprocess.run(
    ["ffmpeg", "-i", "samples/00081.mp4", "samples/00081.mp3"],
    check=True,
)

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


# Locate our project and converter script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONVERT_SCRIPT = PROJECT_ROOT / "converter" / "convert.py"


class TestConverter(unittest.TestCase):

    # Test 1: Missing command-line arguments
    def test_missing_arguments(self):
        result = subprocess.run(
            [sys.executable, str(CONVERT_SCRIPT)],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Usage:", result.stdout)

    # Test 2: Input file does not exist
    def test_file_does_not_exist(self):
        result = subprocess.run(
            [
                sys.executable,
                str(CONVERT_SCRIPT),
                "samples/nonexistent.mp4",
                "mp3"
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("File not found:", result.stdout)

    # Test 3: Unsupported conversion
    def test_unsupported_conversion(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            input_file = Path(temp_dir) / "test.mp4"
            input_file.touch()

            result = subprocess.run(
                [
                    sys.executable,
                    str(CONVERT_SCRIPT),
                    str(input_file),
                    "pdf"
                ],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "Cannot convert .mp4 to pdf.",
                result.stdout
            )

    # Test 4: Successful MP4 to WAV conversion
    def test_mp4_to_wav(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            # Generate a temporary MP4 using FFmpeg
            input_file = Path(temp_dir) / "test.mp4"

            subprocess.run(
                [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel", "error",
                    "-y",
                    "-f", "lavfi",
                    "-i", "sine=frequency=1000:duration=1",
                    "-c:a", "aac",
                    str(input_file)
                ],
                check=True,
                capture_output=True,
                text=True
            )

            # Run our converter
            result = subprocess.run(
                [
                    sys.executable,
                    str(CONVERT_SCRIPT),
                    str(input_file),
                    "wav"
                ],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )

            # Check whether the WAV was created
            output_file = input_file.with_suffix(".wav")

            self.assertEqual(
                result.returncode,
                0,
                msg=result.stdout + result.stderr
            )

            self.assertTrue(output_file.exists())

    # Test 5: Successful DOCX to PDF conversion
    def test_docx_to_pdf(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            # Copy our test document into a temporary folder
            input_file = Path(temp_dir) / "test.docx"

            fixture = PROJECT_ROOT / "tests" / "fixtures" / "test.docx"

            input_file.write_bytes(fixture.read_bytes())

            # Run our converter
            result = subprocess.run(
                [
                    sys.executable,
                    str(CONVERT_SCRIPT),
                    str(input_file),
                    "pdf"
                ],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )

            # Check whether the PDF was created
            output_file = input_file.with_suffix(".pdf")

            self.assertEqual(
                result.returncode,
                0,
                msg=result.stdout + result.stderr
            )

            self.assertTrue(output_file.exists())


if __name__ == "__main__":
    unittest.main()

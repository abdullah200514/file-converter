import subprocess
import sys
import unittest
import shutil
import tempfile
from pathlib import Path

# Locate our project and converter script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONVERT_SCRIPT = PROJECT_ROOT / "converter" / "convert.py"


class TestCommandLineArguments(unittest.TestCase):

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
            [sys.executable, str(CONVERT_SCRIPT), "samples/nonexistent.mp4", "mp3"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("File not found:", result.stdout)

    # Test 3: Unsupported conversion
    def test_unsupported_conversion(self):
        result = subprocess.run(
            [sys.executable, str(CONVERT_SCRIPT), "samples/00081.mp4", "pdf"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Cannot convert .mp4 to pdf.", result.stdout)

    # Test 4: Successful MP4 to WAV conversion
    def test_mp4_to_wav(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary copy of the input video
            input_file = Path(temp_dir) / "test.mp4"

            shutil.copy2(
                PROJECT_ROOT / "samples" / "00081.mp4",
                input_file
            )

            # Run our converter
            result = subprocess.run(
                [sys.executable, str(CONVERT_SCRIPT), str(input_file), "wav"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )

            # Check whether the output file was created
            output_file = input_file.with_suffix(".wav")

            self.assertEqual(result.returncode, 0)
            self.assertTrue(output_file.exists())


if __name__ == "__main__":
    unittest.main()
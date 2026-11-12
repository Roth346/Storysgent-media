import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shorts"))
from clipper import build_command, clip


class ClipperTests(unittest.TestCase):
    def test_vertical_crop(self):
        cmd = build_command(Path("input.mov"), Path("short.mp4"), 2, 8, 1280, "crop")
        self.assertIn("crop=720:1280", cmd[cmd.index("-vf") + 1])
        self.assertIn("0:a:0?", cmd)

    def test_vertical_pad(self):
        cmd = build_command(Path("input.mov"), Path("short.mp4"), 2, 8, 640, "pad")
        self.assertIn("pad=360:640", cmd[cmd.index("-vf") + 1])

    def test_rights_required(self):
        with self.assertRaisesRegex(ValueError, "Rights confirmation"):
            clip(Path("missing.mp4"), Path("out.mp4"), 0, 5, 640, "crop", False, "")


if __name__ == "__main__":
    unittest.main()

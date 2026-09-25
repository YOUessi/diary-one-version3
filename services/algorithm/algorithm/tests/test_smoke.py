import json
import tempfile
import unittest
from pathlib import Path

from diary_one_ci.core import FRAME_OFFSETS_MS, run_smoke


class SmokePathTests(unittest.TestCase):
    def test_e00_is_reproducible_and_logical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = run_smoke(None, root)
            first_manifest = json.loads((first / "manifest.json").read_text())
            second = run_smoke(None, root)
            self.assertEqual(first, second)
            assets = json.loads((first / "logical_assets.json").read_text())
            frames = json.loads((first / "frames.json").read_text())
            self.assertTrue(all(not a["materialized_video"] for a in assets))
            self.assertEqual(len(frames), len(assets) * 3)
            self.assertEqual(sorted({f["offset_ms"] for f in frames}), list(FRAME_OFFSETS_MS))
            self.assertFalse(first_manifest["leaderboard_eligible"])
            validation = json.loads((first / "validation.json").read_text())
            self.assertTrue(validation["passed"])
            self.assertTrue((first / "artifact_index.json").exists())


if __name__ == "__main__":
    unittest.main()

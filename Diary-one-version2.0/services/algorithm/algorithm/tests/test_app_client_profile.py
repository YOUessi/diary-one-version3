# -*- coding: utf-8 -*-
import json
import tempfile
import unittest
from pathlib import Path

from diary_one_ci import app_client_profile as acp


class AppClientProfileTests(unittest.TestCase):
    def test_normalize_and_infer_from_lines(self):
        profile = acp.normalize_profile(
            {
                "memory_preferences": [
                    "Preferred content: Prefer writing about: Daily life, Travel & adventure.",
                    "Interest tags: Boost these tags when evidence exists: Coffee, Family.",
                    "Writing style: Writing style: Empathetic and warm. Soft tone.",
                    "Avoid: Work stress detail: Do not emphasize workplace stress.",
                ]
            }
        )
        self.assertTrue(profile["present"])
        self.assertIn("Coffee", profile["boost_tags"])
        self.assertIn("Family", profile["boost_tags"])
        self.assertEqual(profile["writing_style"], "Empathetic and warm")
        self.assertTrue(any("Work stress" in a or "stress" in a.lower() for a in profile["avoid_topics"]))
        self.assertTrue(profile["preferred_categories"])

    def test_soft_reorder_boost_before_avoid(self):
        profile = acp.normalize_profile(
            {
                "boost_tags": ["Coffee"],
                "avoid_topics": ["commuting"],
            }
        )
        chapters = [
            {"memory_id": "a", "title": "Long commuting"},
            {"memory_id": "b", "title": "Morning Coffee"},
            {"memory_id": "c", "title": "Quiet desk"},
        ]
        ordered, audit = acp.apply_soft_editorial(chapters, profile)
        self.assertEqual(ordered[0]["memory_id"], "b")
        self.assertEqual(ordered[-1]["memory_id"], "a")
        self.assertTrue(audit["applied"])

    def test_write_and_load_beside_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "bundle.json"
            manifest.write_text("{}", encoding="utf-8")
            raw = json.dumps(
                {
                    "schema_version": "APP_CLIENT_PROFILE_V01",
                    "memory_preferences": ["Interest tags: Boost these tags when evidence exists: Pets."],
                    "boost_tags": ["Pets"],
                }
            ).encode("utf-8")
            written = acp.write_profile(root, raw)
            self.assertTrue(written["present"])
            loaded = acp.load_beside_manifest(manifest)
            self.assertIn("Pets", loaded["boost_tags"])
            self.assertTrue(acp.prompt_instruction(loaded))

    def test_invalid_http_profile_never_replaces_saved_profile(self):
        invalid_values = [
            [], None, "cycling",
            {"schema_version": "APP_CLIENT_PROFILE_V99", "writing_style": "warm"},
            {"schema_version": None},
            {"writing_style": 4},
        ]
        for key in ("memory_preferences", "boost_tags", "avoid_topics", "preferred_categories"):
            invalid_values.extend([{key: "cycling"}, {key: ["cycling", 3]}, {key: None}])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            acp.write_profile(root, b'{"boost_tags":["cycling"]}')
            path = root / acp.PROFILE_FILENAME
            before = path.read_bytes()
            for value in invalid_values:
                with self.subTest(value=value):
                    with self.assertRaises(ValueError):
                        acp.write_profile(root, json.dumps(value).encode("utf-8"))
                    self.assertEqual(path.read_bytes(), before)

    def test_legacy_upload_lines_and_empty_profile_are_still_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy = acp.write_profile(root, b'{"memory_preferences":["Writing style: Warm"]}')
            self.assertEqual(legacy["writing_style"], "Warm")
            self.assertFalse(acp.write_profile(root, b'{}')["present"])
            self.assertFalse(acp.write_profile(root, b'{"writing_style":null}')["present"])


if __name__ == "__main__":
    unittest.main()

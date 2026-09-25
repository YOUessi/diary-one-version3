"""Technical regression checks; recorded text is not visual-quality ground truth."""

import copy
import json
import unittest
from pathlib import Path

from diary_one_ci import x02


EXCERPT_PATH = Path(__file__).parent / "fixtures" / "codex_x02_real_run_data_excerpt.json"


class ExampleRuleCleanupTests(unittest.TestCase):
    def setUp(self):
        self.excerpt = json.loads(EXCERPT_PATH.read_text(encoding="utf-8"))
        self.observation = self.excerpt["observation"]
        self.fact_ids = [fact["fact_id"] for fact in self.observation["facts"]]
        self.context = {
            "locale": "zh-Hans",
            "writer_grounding_policy": x02.X02_WRITER_GROUNDING_POLICY,
            "memories": [{
                "candidate_id": "recorded-memory",
                "memory_type": "AHA",
                "event_kind": self.observation["event_kind"],
                "subject_codes": self.observation["subject_codes"],
                "motifs": self.observation["motifs"],
                "event_fact_ids": self.fact_ids,
                "facts": self.observation["facts"],
            }],
        }
        self.output = {
            "chapters": [],
            "ahas": [{
                "candidate_id": "recorded-memory",
                **self.excerpt["recorded_surface"],
                "claim_ids": self.fact_ids,
            }],
        }

    def test_recorded_surface_is_checked_for_format_not_exact_copy(self):
        self.assertNotEqual(
            self.output["ahas"][0]["text"], self.observation["facts"][0]["text"]
        )
        accepted, audit, invalid = x02._validate_writer_output(self.output, self.context)
        self.assertEqual(invalid, [])
        self.assertIn("recorded-memory", accepted)
        self.assertEqual(
            audit[0]["validation_scope"],
            "FORMAT_AND_REFERENCES_ONLY_NOT_SEMANTIC_VERIFICATION",
        )
        self.assertNotIn("source_bindings", audit[0])

    def test_recorded_fact_scope_does_not_require_scene_word_hits(self):
        self.assertEqual(x02._supported_aha_fact_ids(self.observation), self.fact_ids)

    def test_long_recorded_fact_is_not_replaced_by_a_category_template(self):
        self.assertGreater(
            x02._visible_length(self.observation["facts"][0]["text"]),
            x02.AHA_MOMENT_LINE_VISIBLE_MAX,
        )
        output, audit = x02._deterministic_writer_fallback(self.context)
        self.assertEqual(output["ahas"], [])
        self.assertEqual(audit[0]["validation_status"], "REJECTED")

    def test_missing_fact_reference_remains_an_interface_error(self):
        output = copy.deepcopy(self.output)
        output["ahas"][0]["claim_ids"] = ["missing-fact-id"]
        accepted, audit, invalid = x02._validate_writer_output(output, self.context)
        self.assertEqual(accepted, {})
        self.assertEqual(invalid, ["recorded-memory"])
        self.assertIn("WRITER_CLAIM_REFERENCE_INVALID", audit[0]["reason_codes"])

    def test_writer_revision_is_distinct_and_compact_policy_has_no_category_allowlist(self):
        self.assertEqual(
            x02.X02_WRITER_SURFACE_POLICY_VERSION, "DIARY_ONE_X02_WRITER_SURFACE_V02"
        )
        policy = x02.X02_STORYLINE_CONTRACT["compact_two_member_policy"]
        self.assertFalse(policy["category_restriction"])
        self.assertNotIn("allowed_focus_codes", policy)

    def test_ownership_check_follows_model_core_references_not_category_names(self):
        # ID/role plumbing only: no invented scene or semantic-quality label.
        candidate = {"source_asset_id": "source-1", "event_fact_ids": ["fact-1"]}
        chapter = {
            "source_asset_ids": ["source-1"],
            "proposal_source": "MODEL_STORYLINE_PROPOSAL",
            "storyline_identity": {
                "beat_map": [{"beat_role": "PEAK", "fact_ids": ["fact-1"]}]
            },
        }
        self.assertEqual(
            x02._aha_chapter_conflict(candidate, chapter),
            "SAME_MODEL_ASSIGNED_CHAPTER_CORE_FACTS",
        )
        chapter["proposal_source"] = "DETERMINISTIC_FOCUS_EPISODE_PARTITION"
        self.assertIsNone(x02._aha_chapter_conflict(candidate, chapter))
        chapter["proposal_source"] = "MODEL_STORYLINE_PROPOSAL"
        chapter["storyline_identity"]["beat_map"][0]["fact_ids"] = ["fact-2"]
        self.assertIsNone(x02._aha_chapter_conflict(candidate, chapter))


if __name__ == "__main__":
    unittest.main()

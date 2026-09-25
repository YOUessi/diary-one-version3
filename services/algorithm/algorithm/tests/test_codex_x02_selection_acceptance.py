"""Real-response regression and interface checks; no invented scene rules."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from diary_one_ci import codex_chapter_media as media
from diary_one_ci import x02
from test_codex_x02_chapter_media import MediaGateway
from test_x02 import make_x02_bundle_v03


class SubsetMediaGateway(MediaGateway):
    """Vary only the returned ID list in the existing interface fixture."""

    def call(self, stage, prompt, schema, evidence=(), context=None):
        run = super().call(stage, prompt, schema, evidence, context)
        if stage.startswith("S10_CHAPTER_VISUAL_SELECTION_"):
            self.proposed_ids = list(reversed(run.output["ranked_observation_ids"]))[:self.display_count]
            run.output["ranked_observation_ids"] = self.proposed_ids
        return run


class SelectionAcceptanceTests(unittest.TestCase):
    def setUp(self):
        fixture = Path(__file__).parent / "fixtures/codex_v1_48_s10_partial_ranking_real.json"
        self.record = json.loads(fixture.read_text(encoding="utf-8"))
        self.members = self.record["members"]
        self.output = self.record["model_output"]
        self.proposed = self.output["ranked_observation_ids"]

    def test_exact_real_reply_keeps_three_chosen_items_and_does_not_invent_tail_ranking(self):
        original = copy.deepcopy(self.record)
        choice = media.choose_display(self.members, self.output)
        self.assertEqual(choice["selected_observation_ids"], self.proposed)
        self.assertEqual(
            [self.record["material_labels"][value] for value in choice["selected_observation_ids"]],
            ["M04", "M08", "M11"],
        )
        self.assertEqual(choice["ranked_observation_ids"], self.proposed)
        self.assertEqual(choice["ranking_scope"], "RETURNED_SUBSET")
        self.assertEqual(len(choice["omitted_observation_ids"]), 6)
        self.assertEqual(choice["selection_source"], "MODEL_VISUAL_SELECTION")
        self.assertEqual(choice["model_reason"], self.output["reason"])
        self.assertEqual(choice["fallback_reason"], "")
        self.assertEqual(choice["response_acceptance_version"], media.RESPONSE_ACCEPTANCE_VERSION)
        self.assertFalse(choice["candidate_membership_changed"])
        self.assertEqual(self.record, original)

    def test_full_ranking_remains_supported(self):
        # Recorded IDs, mechanically extended for interface compatibility only.
        rank = self.proposed + [m["id"] for m in self.members if m["id"] not in self.proposed]
        for count in (3, 4, 5):
            with self.subTest(count=count):
                choice = media.choose_display(self.members, dict(self.output, ranked_observation_ids=rank, display_count=count))
                self.assertEqual(choice["selected_observation_ids"], rank[:count])
                self.assertEqual(choice["ranked_observation_ids"], rank)
                self.assertEqual(choice["ranking_scope"], "ALL_MEMBERS")
                self.assertEqual(choice["selection_source"], "MODEL_VISUAL_SELECTION")

    def test_count_normalization_never_fills_with_unranked_members(self):
        for count in (1, 3, 4, 5, 99):
            with self.subTest(count=count):
                choice = media.choose_display(self.members, dict(self.output, display_count=count))
                self.assertEqual(choice["selected_observation_ids"], self.proposed)
                self.assertEqual(choice["count_adjusted_to_display_contract"], count != 3)
                self.assertEqual(choice["selection_source"], "MODEL_VISUAL_SELECTION")

    def test_invalid_ids_and_types_still_use_explicit_fallback(self):
        # Structural mutations, not semantic counterexamples or new content rules.
        invalid_outputs = [
            dict(self.output, ranked_observation_ids=self.proposed[:2]),
            dict(self.output, ranked_observation_ids=self.proposed[:2] + self.proposed[:1]),
            dict(self.output, ranked_observation_ids=self.proposed[:2] + ["unknown-id"]),
            dict(self.output, ranked_observation_ids=self.proposed[:2] + [None]),
            dict(self.output, display_count=True),
            dict(self.output, display_count="3"),
        ]
        for output in invalid_outputs:
            with self.subTest(output=output):
                choice = media.choose_display(self.members, output)
                self.assertEqual(choice["selection_source"], "QUALITY_ONLY_FALLBACK_NOT_DEDUP_VERIFIED")
                self.assertEqual(choice["fallback_reason"], "MODEL_SELECTION_REFERENCES_OR_COUNT_INVALID")
                self.assertEqual(len(choice["selected_observation_ids"]), 3)

    def test_subset_reaches_selected_media_and_writer_without_extra_s10_calls(self):
        for count in (3, 4, 5):
            with self.subTest(count=count), tempfile.TemporaryDirectory() as temporary:
                gateway = SubsetMediaGateway(display_count=count)
                result = x02.run_x02(make_x02_bundle_v03(Path(temporary)), gateway)
                chapter = result["chapters"][0]
                entry = result["decision_trace"]["s10_chapter_media"][0]
                self.assertEqual(entry["candidate_content_unit_count"], 5)
                self.assertEqual(entry["final_media_count"], count)
                self.assertEqual(entry["display_selection"]["selected_observation_ids"], gateway.proposed_ids)
                self.assertEqual(entry["display_selection"]["selection_source"], "MODEL_VISUAL_SELECTION")
                self.assertEqual({m["observation_id"] for m in chapter["selected_media"]}, set(gateway.proposed_ids))
                self.assertEqual(next(m["observation_id"] for m in entry["media"] if m["role"] == "HERO"), gateway.proposed_ids[0])
                memory = next(
                    memory for call in gateway.calls if call["stage"] == "S11_WRITER_ATTEMPT_1"
                    for memory in call["context"]["memories"] if memory["candidate_id"] == chapter["candidate_id"]
                )
                expected_facts = {
                    f["fact_id"] for o in result["observations"] if o["id"] in gateway.proposed_ids for f in o["facts"]
                }
                self.assertEqual({f["fact_id"] for f in memory["facts"]}, expected_facts)
                self.assertEqual(len(result["observations"]), 5)
                self.assertEqual(sum(c["stage"].startswith("S10_CHAPTER_VISUAL_SELECTION_") for c in gateway.calls), 1)


if __name__ == "__main__":
    unittest.main()

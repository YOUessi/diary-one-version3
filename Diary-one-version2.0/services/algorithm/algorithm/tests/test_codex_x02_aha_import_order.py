"""Real selection replay; order variations test metadata, not invented scenes."""

import copy
import json
import unittest
from pathlib import Path

from diary_one_ci import x02


class AhaImportOrderTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).parent / "fixtures/codex_v1_48_aha_selection_real.json"
        self.record = json.loads(path.read_text(encoding="utf-8"))
        self.labels = self.record["candidate_material_labels"]
        self.by_label = {self.labels[c["candidate_id"]]: c for c in self.record["candidates"]}

    def select(self, value_first=True):
        ledger = copy.deepcopy(self.record["candidate_ledger"])
        selected, audit = x02._select_aha_set(
            self.record["candidates"], ledger, self.record["selected_chapters"],
            [], self.record["asset_order"], value_first=value_first,
        )
        return selected, audit, ledger

    def test_real_stone_and_river_are_not_vetoed_by_shared_categories_and_import_proximity(self):
        stone, river = self.by_label["M13"], self.by_label["M14"]
        self.assertFalse(self.record["time_reliability"]["capture_time_reliable"])
        self.assertEqual(stone["episode_code"], river["episode_code"])
        self.assertEqual(stone["event_kind"], river["event_kind"])
        self.assertTrue(set(stone["subject_codes"]) & set(river["subject_codes"]))
        self.assertFalse(set(stone["motifs"]) & set(river["motifs"]))
        self.assertEqual(
            self.record["historical_selection_audit"]["rejections"][river["candidate_id"]],
            "SAME_LOCAL_EVENT_SIGNATURE",
        )
        self.assertIsNone(x02._aha_pair_conflict(stone, river, self.record["asset_order"]))

    def test_import_position_changes_do_not_change_real_pair_relation(self):
        stone, river = self.by_label["M13"], self.by_label["M14"]
        for positions in ((12, 13), (13, 12), (0, 19), (19, 0)):
            with self.subTest(positions=positions):
                order = dict(self.record["asset_order"])
                order[stone["source_asset_id"]], order[river["source_asset_id"]] = positions
                self.assertIsNone(x02._aha_pair_conflict(stone, river, order))

    def test_exact_repeated_asset_still_has_duplicate_evidence(self):
        for candidate in self.record["candidates"]:
            with self.subTest(candidate=self.labels[candidate["candidate_id"]]):
                self.assertEqual(
                    x02._aha_pair_conflict(candidate, copy.deepcopy(candidate), self.record["asset_order"]),
                    "SAME_OBSERVATION_AHA_DUPLICATE",
                )

    def test_real_full_selection_changes_membership_not_scores_or_capacity(self):
        original = copy.deepcopy(self.record)
        selected, audit, ledger = self.select()
        old = self.record["historical_selection_audit"]
        self.assertEqual([self.labels[c["candidate_id"]] for c in selected], ["M09", "M13", "M14"])
        self.assertEqual(len(selected), len(old["selected_candidate_ids"]))
        self.assertEqual(audit["candidate_rank_inputs"], old["candidate_rank_inputs"])
        self.assertEqual(audit["ranked_candidate_ids"], old["ranked_candidate_ids"])
        self.assertEqual(audit["chapter_conflicts"], old["chapter_conflicts"])
        self.assertEqual(audit["eligible_candidate_count"], old["eligible_candidate_count"])
        self.assertEqual(audit["pair_conflict_policy_version"], x02.X02_AHA_PAIR_CONFLICT_POLICY_VERSION)
        self.assertEqual(audit["rejections"][self.by_label["M03"]["candidate_id"]], "AHA_PREVIEW_CAPACITY_REACHED")
        self.assertEqual(audit["rejections"][self.by_label["M12"]["candidate_id"]], "SAME_MODEL_ASSIGNED_CHAPTER_CORE_FACTS")
        pair_ids = {self.by_label[name]["candidate_id"] for name in ("M13", "M14")}
        pair = next(p for p in audit["pair_ledger"] if {p["candidate_a_id"], p["candidate_b_id"]} == pair_ids)
        self.assertEqual(pair["relation"], "NO_CONFLICT_EVIDENCE")
        self.assertEqual(pair["selection_effect"], "ALLOW_COSELECT")
        self.assertEqual(pair["same_memory_evidence"], [])
        self.assertEqual(pair["distinct_memory_evidence"], [])
        river = next(a for a in ledger if a["candidate_id"] == self.by_label["M14"]["candidate_id"])
        self.assertEqual(river["selection_status"], "SELECTED")
        self.assertNotIn("suppressed_by_candidate_id", river)
        self.assertEqual(self.record, original)

    def test_legacy_selection_branch_remains_unchanged(self):
        selected, audit, _ = self.select(value_first=False)
        self.assertEqual([self.labels[c["candidate_id"]] for c in selected], ["M03", "M09", "M12"])
        self.assertEqual(audit["search_contract"], "EVENT_AND_DISCOVERY_AHA_PATHS_V01")
        self.assertNotIn("pair_conflict_policy_version", audit)


if __name__ == "__main__":
    unittest.main()

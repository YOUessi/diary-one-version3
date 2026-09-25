"""Grouping ownership and data plumbing, never synthetic semantic-quality gold."""

import copy
import json
import tempfile
import unittest
import uuid
from pathlib import Path

from diary_one_ci import x02
from test_x02 import ScriptedGateway, assert_json_schema_instance, make_x02_bundle


ROOT = Path(__file__).resolve().parents[1]


class ModelOwnedGroupingTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "tests/fixtures/codex_x02_grouping_reference_data.json").read_text())
        self.observations = self.data["observations"]
        self.roles = self.data["roles"]
        self.order = self.data["asset_order"]
        by_id = {item["id"]: item for item in self.observations}
        self.proposals = []
        for recorded in self.data["recorded_proposals"]:
            members = [by_id[value] for value in recorded["observation_ids"]]
            self.proposals.append({
                "key": recorded["candidate_key"],
                "storyline_basis": recorded.get("basis_normalization", {}).get("supplied", recorded["storyline_basis"]),
                "thesis": "",  # Unavailable in the real log; do not invent it.
                "observation_ids": [item["id"] for item in members],
                "fact_ids": [fact["fact_id"] for item in members for fact in item["facts"]],
                "beat_map": [{
                    "observation_id": item["id"],
                    "beat_role": "PROGRESSION",  # ID scaffolding, not a recorded semantic role.
                    "fact_ids": [fact["fact_id"] for fact in item["facts"]],
                    "contribution": "",  # No reconstructed model explanation.
                } for item in members],
            })

    def build(self, proposals=None, order=None):
        return x02._build_storyline_candidates(
            uuid.NAMESPACE_URL, self.observations, self.roles, [],
            {"storyline_proposals": self.proposals if proposals is None else proposals},
            self.order if order is None else order,
        )

    def test_recorded_member_groups_survive_without_fixed_focus_or_auto_groups(self):
        candidates, ledger = self.build()
        self.assertEqual(len(candidates), len(self.proposals))
        self.assertEqual(
            {frozenset(item["observation_ids"]) for item in candidates},
            {frozenset(item["observation_ids"]) for item in self.proposals},
        )
        for candidate, proposal, entry in zip(candidates, self.proposals, ledger):
            self.assertEqual(candidate["proposal_source"], "MODEL_STORYLINE_PROPOSAL")
            self.assertEqual(candidate["storyline_basis"], proposal["storyline_basis"])
            self.assertEqual(candidate["focus_code"], "")
            self.assertNotIn("basis_normalization", entry)
            self.assertEqual(candidate["storyline_identity"]["continuity_evidence"], [])
            self.assertEqual(
                candidate["storyline_identity"]["one_story_gate"]["validation_scope"],
                "STRUCTURE_AND_REFERENCES_ONLY_NOT_SEMANTIC_VERIFICATION",
            )

    def test_empty_model_grouping_has_no_tag_fallback_and_does_not_remove_aha_input(self):
        self.assertEqual(self.build([]), ([], []))
        observation = self.observations[-1]
        facts = [fact["fact_id"] for fact in observation["facts"]]
        candidates, _ = x02._build_aha_candidates(
            uuid.NAMESPACE_URL, self.observations, self.roles,
            [{"id": "reference-" + item["id"], "observation_ids": [item["id"]]} for item in self.observations],
            {"storyline_proposals": [], "aha_proposals": [{
                "key": "reference-only", "observation_id": observation["id"],
                "event_fact_ids": facts, "narrative_duty": "Reference routing test.",
            }]}, self.order, value_first=True,
        )
        self.assertTrue(any(item["observation_id"] == observation["id"] for item in candidates))

    def test_explanation_is_preserved_without_category_rewriting_or_length_rejection(self):
        proposals = copy.deepcopy(self.proposals)
        contribution = "x" * 301  # Field-length probe, not a made-up scene.
        proposals[0]["beat_map"][0]["contribution"] = contribution
        proposals[0]["reason"] = "Recorded here as a plumbing probe only."
        candidates, ledger = self.build(proposals)
        self.assertEqual(candidates[0]["storyline_identity"]["beat_map"][0]["contribution"], contribution)
        self.assertEqual(ledger[0]["model_grouping_reason"], proposals[0]["reason"])

    def test_annotation_does_not_change_identity_pair_relation_or_selection(self):
        candidates, ledger = self.build()
        selected, audit = x02._select_storyline_set(candidates, ledger, self.observations, self.order)
        for annotations in (("tag-a", "tag-a"), ("tag-a", "tag-b")):
            proposals = [{**proposal, "focus_code": annotation} for proposal, annotation in zip(self.proposals, annotations)]
            changed, changed_ledger = self.build(proposals)
            self.assertEqual([item["candidate_id"] for item in changed], [item["candidate_id"] for item in candidates])
            chosen, changed_audit = x02._select_storyline_set(changed, changed_ledger, self.observations, self.order)
            self.assertEqual([item["candidate_id"] for item in chosen], [item["candidate_id"] for item in selected])
            self.assertEqual(changed_audit["objective"], audit["objective"])
            self.assertEqual(changed_audit["pair_ledger"], audit["pair_ledger"])
            for pair in changed_audit["pair_ledger"]:
                self.assertEqual(pair["same_memory_evidence"], [])
                self.assertEqual(pair["distinct_memory_evidence"], [])
        self.assertNotIn("primary_focus_diversity", audit["objective"])
        self.assertEqual(x02._storyline_pair_conflict(candidates[0], candidates[0], self.order), "CHAPTER_RAW_ASSET_CONFLICT")

    def test_same_members_are_one_identity_even_with_different_annotations(self):
        first = self.proposals[0]
        candidates, ledger = self.build([first, {**first, "focus_code": "tag-b"}])
        self.assertEqual(len(candidates), 1)
        self.assertIn("DUPLICATE_STORYLINE_IDENTITY", ledger[1]["reason_codes"])

    def test_import_positions_are_diagnostics_not_capture_time_or_grouping_authority(self):
        candidates, _ = self.build()
        # Reposition the same recorded IDs only; this does not create a semantic day.
        order = {key: index * 20 for index, key in enumerate(reversed(self.order))}
        reordered, _ = self.build(order=order)
        self.assertEqual({item["candidate_id"] for item in candidates}, {item["candidate_id"] for item in reordered})
        for candidate in reordered:
            gate = candidate["storyline_identity"]["one_story_gate"]
            self.assertEqual(gate["decision"], "PASS")
            self.assertEqual(gate["split_challenge"]["decision"], "NOT_PROGRAMMATICALLY_EVALUATED")

    def test_compact_support_contract_does_not_claim_to_verify_distinctness(self):
        supported = [{"facts": [{"support_grade": grade}]} for grade in ("STRONG", "MODERATE")]
        self.assertTrue(x02._compact_storyline_eligible(supported))
        supported[1]["facts"][0]["support_grade"] = "WEAK"
        self.assertFalse(x02._compact_storyline_eligible(supported))

    def test_integration_uses_one_structure_call_and_retains_retrieval_tags(self):
        gateway = ScriptedGateway(storyline_groups=[[0, 1, 2], [3, 4, 5]])
        with tempfile.TemporaryDirectory() as directory:
            result = x02.run_x02(make_x02_bundle(Path(directory), 6), gateway)
        structure_calls = [item for item in gateway.calls if item["stage"] == "S05_S07_STRUCTURE_PROPOSAL"]
        self.assertEqual(len(structure_calls), 1)
        self.assertEqual(result["storyline_contract_version"], "DIARY_ONE_X02_STORYLINE_V03")
        self.assertEqual(len(result["chapters"]), 2)
        for item in structure_calls[0]["context"]["observations"]:
            self.assertIn("subject_codes", item)
            self.assertIn("facts", item)
            self.assertNotIn("primary_storyline_focus", item)
            self.assertNotIn("storyline_focus_candidates", item)
        schema = json.loads((ROOT / "contracts/codex_x02_staged_preview_v04_1_media_v01.schema.json").read_text())
        assert_json_schema_instance(self, schema, result)
        self.assertNotIn("chapter_independence", result["decision_trace"]["aha_set_selection"]["rank_fields"])
        proposal_schema = x02.STRUCTURE_SCHEMA["properties"]["storyline_proposals"]["items"]
        self.assertNotIn("focus_code", proposal_schema["required"])
        self.assertNotIn("enum", proposal_schema["properties"]["focus_code"])
        self.assertNotIn("focus_codes", x02.X02_STORYLINE_CONTRACT)


if __name__ == "__main__":
    unittest.main()

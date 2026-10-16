"""Field handling against recorded member data, not model or visual-quality evaluation."""

import copy
import json
import unittest
import uuid
from pathlib import Path

from diary_one_ci import x02
from test_x02 import assert_json_schema_instance


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "codex_x02_recorded_storyline_members.json"


class StorylineThesisIsolationTests(unittest.TestCase):
    def setUp(self):
        self.recorded = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.observations = self.recorded["observations"]
        self.roles = self.recorded["roles"]
        self.order = self.recorded["asset_order"]
        rejection = self.recorded["recorded_rejection"]
        self.proposal = {
            "key": rejection["candidate_key"],
            "storyline_basis": rejection["storyline_basis"],
            "focus_code": rejection["focus_code"],
            "observation_ids": rejection["observation_ids"],
            "fact_ids": [fact["fact_id"] for item in self.observations for fact in item["facts"]],
            # Neutral field probes and role scaffolding, not reconstructed model text.
            "thesis": "xx",
            "beat_map": [{
                "observation_id": item["id"],
                "beat_role": "PROGRESSION",
                "fact_ids": [fact["fact_id"] for fact in item["facts"]],
                "contribution": "field-handling test",
            } for item in self.observations],
        }

    def build(self, proposals):
        # Model-only grouping no longer needs the V1.34 isolation patch.
        return x02._build_storyline_candidates(
            uuid.NAMESPACE_URL, self.observations, self.roles, [],
            {"storyline_proposals": proposals}, self.order,
        )

    def test_length_only_changes_diagnostics_not_members_facts_or_writer_handoff(self):
        schema = json.loads((ROOT / "contracts" / "codex_x02_staged_preview_v04_1_media_v01.schema.json").read_text())
        identity_schema = {
            "$defs": schema["$defs"], "$ref": "#/$defs/storylineIdentity",
        }
        reference, _ = self.build([self.proposal])
        self.assertEqual(len(reference), 1)
        for raw in ("", " \n ", "x", "xx", "x" * 160, "x" * 161, "  " + "x" * 200 + "  "):
            with self.subTest(length=len(raw)):
                proposal = {**self.proposal, "thesis": raw}
                candidates, ledger = self.build([proposal])
                self.assertEqual(len(candidates), 1)
                self.assertEqual(ledger[0]["validation_status"], "PASSED")
                candidate = candidates[0]
                expected = copy.deepcopy(reference[0])
                expected["storyline_identity"]["thesis"] = raw.strip()
                self.assertEqual(candidate, expected)
                self.assertEqual(ledger[0]["thesis_field_audit"], {
                    "supplied_text": raw,
                    "character_count": len(raw.strip()),
                    "within_length_guidance": 2 <= len(raw.strip()) <= 160,
                    "candidate_eligibility_effect": "NONE",
                })
                assert_json_schema_instance(self, identity_schema, candidate["storyline_identity"])
                media = {candidate["candidate_id"]: {"media": [
                    {"observation_id": item["id"]} for item in self.observations
                ]}}
                context = x02._writer_context(
                    candidates, [], media, {}, self.observations, storyline_v04=True,
                )
                self.assertEqual(context["memories"][0]["storyline_identity"]["thesis"], raw.strip())
                self.assertEqual(
                    {fact["fact_id"] for fact in context["memories"][0]["facts"]},
                    set(self.proposal["fact_ids"]),
                )

    def test_core_reference_and_role_checks_are_not_bypassed(self):
        for field, replacement, reason in (
            ("observation_ids", ["missing-id", *self.proposal["observation_ids"][1:]], "UNKNOWN_OBSERVATION_REFERENCE"),
            ("fact_ids", ["missing-fact-id"], "STORYLINE_FACT_REFERENCE_INVALID"),
            ("beat_map", self.proposal["beat_map"][:-1], "STORYLINE_BEAT_COVERAGE_INCOMPLETE"),
        ):
            with self.subTest(field=field):
                candidates, ledger = self.build([{**self.proposal, "thesis": "", field: replacement}])
                self.assertEqual(candidates, [])
                self.assertIn(reason, ledger[0]["reason_codes"])
        self.roles[0]["role"] = "CONTEXT_ONLY"
        candidates, ledger = self.build([{**self.proposal, "thesis": ""}])
        self.assertEqual(candidates, [])
        self.assertIn("NON_KEEP_MEMBER", ledger[0]["reason_codes"])

    def test_missing_or_non_string_field_keeps_existing_interface_error(self):
        missing = copy.deepcopy(self.proposal)
        del missing["thesis"]
        for proposal in (missing, {**self.proposal, "thesis": None}, {**self.proposal, "thesis": 160}):
            candidates, ledger = self.build([proposal])
            self.assertEqual(candidates, [])
            self.assertEqual(ledger[0]["detail"], "storyline.thesis must be a string")

    def test_later_duplicate_rejection_preserves_explanation_diagnostics(self):
        proposals = [self.proposal, {**self.proposal, "thesis": "x" * 161}]
        candidates, ledger = self.build(proposals)
        self.assertEqual(len(candidates), 1)
        self.assertIn("DUPLICATE_STORYLINE_IDENTITY", ledger[1]["reason_codes"])
        self.assertEqual(ledger[1]["thesis"], "x" * 161)
        self.assertEqual(ledger[1]["thesis_field_audit"]["supplied_text"], "x" * 161)
        self.assertFalse(ledger[1]["thesis_field_audit"]["within_length_guidance"])


if __name__ == "__main__":
    unittest.main()

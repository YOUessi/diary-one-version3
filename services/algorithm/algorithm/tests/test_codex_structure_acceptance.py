"""Recorded response regression: field acceptance, not a semantic-quality score."""

import copy
import json
import unittest
import uuid
from pathlib import Path

from diary_one_ci import x02
from diary_one_ci import codex_content_brief as content_handoff


FIXTURE = Path(__file__).parent / "fixtures/codex_v1_65_recorded_structure.json"


class RecordedStructureAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.cases = {
            (case["pack"], case["round"]): case
            for case in json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]
        }

    def build(self, case):
        arguments = (
            uuid.UUID(case["session_id"]), case["observations"], case["roles"],
            case["moments"], case["structure_output"], case["asset_order"],
        )
        chapters, chapter_ledger = x02._build_storyline_candidates(*arguments)
        ahas, aha_ledger = x02._build_aha_candidates(*arguments, value_first=True)
        return chapters, chapter_ledger, ahas, aha_ledger

    def test_recorded_football_summary_omission_does_not_drop_valid_members(self):
        case = self.cases[(3, 3)]
        original = copy.deepcopy(case)
        chapters, ledger, _, _ = self.build(case)
        self.assertEqual(len(chapters), 1)
        chapter = chapters[0]
        proposal = case["structure_output"]["storyline_proposals"][0]
        self.assertEqual(len(chapter["observation_ids"]), 9)
        self.assertEqual(set(chapter["observation_ids"]), set(proposal["observation_ids"]))
        self.assertEqual(chapter["storyline_identity"]["beat_map"], proposal["beat_map"])
        self.assertEqual(set(chapter["fact_ids"]), {
            fact_id for beat in proposal["beat_map"] for fact_id in beat["fact_ids"]
        })
        audit = ledger[0]["fact_summary_audit"]
        self.assertEqual(audit["added_from_validated_beats"], [
            "1812a6dd-f76d-5a13-98a3-801060ea16cd"
        ])
        self.assertFalse(audit["membership_changed"])
        self.assertFalse(audit["fact_text_changed"])
        self.assertEqual(case, original)

    def test_recorded_city_reference_mismatch_is_not_repaired(self):
        _, ledger, _, _ = self.build(self.cases[(3, 3)])
        city = next(e for e in ledger if e["candidate_key"] == "urban_architectural_discovery_series")
        self.assertEqual(city["validation_status"], "REJECTED")
        self.assertIn("STORYLINE_FACT_REFERENCE_INVALID", city["reason_codes"])
        self.assertNotIn("fact_summary_audit", city)

    def test_recorded_24_member_group_is_not_truncated_or_accepted(self):
        case = self.cases[(3, 2)]
        original = copy.deepcopy(case)
        chapters, ledger, _, _ = self.build(case)
        self.assertEqual(chapters, [])
        self.assertIn("STORYLINE_CONTENT_UNIT_COUNT_INVALID", ledger[0]["reason_codes"])
        self.assertEqual(len(case["structure_output"]["storyline_proposals"][0]["observation_ids"]), 24)
        self.assertEqual(case, original)

    def test_recorded_long_explanations_survive_without_losing_other_checks(self):
        case = self.cases[(2, 2)]
        _, _, candidates, ledger = self.build(case)
        model_entries = {
            e["candidate_key"]: e for e in ledger
            if e["proposal_source"] == "MODEL_STRUCTURE_PROPOSAL"
        }
        self.assertEqual({key for key, entry in model_entries.items()
                          if entry["validation_status"] == "PASSED"}, {
            "eos_70d_discovery", "deer_photographer_interaction"
        })
        for proposal in case["structure_output"]["aha_proposals"][:2]:
            entry = model_entries[proposal["key"]]
            candidate = next(c for c in candidates if c["candidate_id"] == entry["candidate_id"])
            self.assertEqual(candidate["narrative_duty"], proposal["narrative_duty"].strip())
            self.assertEqual(entry["narrative_duty_field_audit"]["supplied_text"], proposal["narrative_duty"])
            self.assertFalse(entry["narrative_duty_field_audit"]["within_legacy_length_limit"])
            self.assertEqual(entry["narrative_duty_field_audit"]["candidate_eligibility_effect"], "NONE")
        self.assertIn("EVENT_KIND_NOT_INDEPENDENT_PEAK", model_entries["camel_rider_detail"]["reason_codes"])
        self.assertIn("EVENT_SALIENCE_TOO_LOW", model_entries["raw_meat_platter_surprise"]["reason_codes"])

    def test_recorded_aha_fact_mismatch_remains_rejected(self):
        _, _, _, ledger = self.build(self.cases[(3, 3)])
        entry = next(e for e in ledger if e["candidate_key"] == "golden_temple_reflection")
        self.assertEqual(entry["validation_status"], "REJECTED")
        self.assertIn("EVENT_FACT_REFERENCE_INVALID", entry["reason_codes"])

    def test_empty_and_non_string_explanations_are_interface_errors(self):
        # Type/empty-field probes only; no invented scene or semantic gold label.
        for value in (None, "", " \n ", 120, []):
            with self.subTest(value=value):
                case = copy.deepcopy(self.cases[(2, 2)])
                case["structure_output"]["aha_proposals"][0]["narrative_duty"] = value
                _, _, _, ledger = self.build(case)
                entry = next(e for e in ledger if e["candidate_key"] == "eos_70d_discovery")
                self.assertEqual(entry["validation_status"], "REJECTED")
                self.assertIn("AHA_CONTRACT_INVALID", entry["reason_codes"])

    def test_explanations_remain_hints_not_extra_facts_in_writer_handoff(self):
        case = self.cases[(2, 2)]
        _, _, candidates, _ = self.build(case)
        candidate = next(c for c in candidates if c["proposal_source"] == "MODEL_STRUCTURE_PROPOSAL")
        app_ids = {o["source_asset_id"]: o["asset_id"] for o in case["observations"]}
        media = {candidate["candidate_id"]: x02._select_aha_media(candidate, case["observations"], app_ids)}
        context = x02._writer_context([], [candidate], {}, media, case["observations"], storyline_v04=True)
        projected = content_handoff.writer_input(context)
        self.assertEqual(projected["guidance_scope"], "EDITORIAL_HINTS_NOT_FACT_EVIDENCE")
        memory = projected["memories"][0]
        self.assertEqual(memory["content_brief"]["moment_hint"], candidate["narrative_duty"])
        observation = next(o for o in case["observations"] if o["id"] == candidate["observation_id"])
        self.assertEqual(memory["facts"], [
            {"fact_id": f["fact_id"], "text": f["text"]} for f in observation["facts"]
            if f["fact_id"] in candidate["fact_ids"]
        ])
        self.assertEqual(set(memory["event_fact_ids"]), set(candidate["fact_ids"]))

    def test_model_and_event_sources_still_share_one_observation_candidate(self):
        _, _, candidates, ledger = self.build(self.cases[(2, 2)])
        self.assertEqual(len({c["observation_id"] for c in candidates}), len(candidates))
        self.assertTrue(any(e["proposal_source"] == "DETERMINISTIC_EVENT_PEAK" for e in ledger))
        self.assertTrue(any(e.get("alias_of_candidate_id") for e in ledger))

    def test_runtime_receipt_identifies_the_new_acceptance_policy(self):
        self.assertEqual(x02.x02_runtime_policies()["structure_acceptance"],
                         "DIARY_ONE_X02_STRUCTURE_ACCEPTANCE_V01")


if __name__ == "__main__":
    unittest.main()

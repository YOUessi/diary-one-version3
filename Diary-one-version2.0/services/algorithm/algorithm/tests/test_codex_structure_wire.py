"""Recorded wire replay and type/reference boundaries, not semantic quality gold.

Legacy-to-new projection below is test-only and does not call a model. In the
explicit pack-3 replay, a legacy native key may map to its one recorded native
observation. Runtime normalization must never perform that alias lookup.
"""

import copy
import json
import unittest
import uuid
from pathlib import Path

from diary_one_ci import codex_editorial_allocation as allocation
from diary_one_ci import codex_structure_wire as wire
from diary_one_ci import x02


FIXTURE = Path(__file__).parent / "fixtures/codex_v1_67_recorded_structure_wire.json"


def project_recorded_legacy_wire(case, *, replay_native_keys=False):
    """Mechanical test adapter, never a runtime repair or semantic annotation."""
    output = copy.deepcopy(case["structure_output"])
    rows = output.pop("chapter_aha_relations")
    native_by_key = {}
    for aha in output["aha_proposals"]:
        native_by_key.setdefault(aha["key"], []).append(aha["observation_id"])
    valid_observations = {observation["id"] for observation in case["observations"]}
    chapter_keys = [chapter["key"] for chapter in output["storyline_proposals"]]
    assert len(chapter_keys) == len(set(chapter_keys))
    assert all(row["chapter_key"] in chapter_keys for row in rows)
    for chapter in output["storyline_proposals"]:
        chapter.pop("observation_ids")
        chapter.pop("fact_ids")
        chapter["aha_relations"] = []
        for original in rows:
            if original["chapter_key"] != chapter["key"]:
                continue
            row = copy.deepcopy(original)
            row.pop("chapter_key")
            observation_id = row.pop("aha_observation_id")
            if replay_native_keys and observation_id not in valid_observations:
                # Explicit legacy replay only: require an unambiguous recorded
                # native key; do not match text, facts, title, role or scenery.
                matches = native_by_key.get(observation_id, [])
                assert len(matches) == 1
                observation_id = matches[0]
                assert observation_id in valid_observations
            row["observation_id"] = observation_id
            chapter["aha_relations"].append(row)
    for aha in output["aha_proposals"]:
        aha.pop("key")
    return output


def build(case, output):
    args = (uuid.UUID(case["namespace"]), case["observations"], case["roles"],
            case["moments"], output, case["asset_order"])
    chapters, chapter_ledger = x02._build_storyline_candidates(*args)
    ahas, aha_ledger = x02._build_aha_candidates(*args, value_first=True)
    return chapters, chapter_ledger, ahas, aha_ledger


def ledger_entry(ledger, key):
    return next(entry for entry in ledger if entry["candidate_key"] == key)


class StructureWireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {case["pack"]: case for case in
                     json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]}

    def test_schema_is_copied_and_has_one_membership_and_relation_authority(self):
        legacy = copy.deepcopy(x02.STRUCTURE_SCHEMA)
        base = allocation.structure_schema(x02.STRUCTURE_SCHEMA)
        before = copy.deepcopy(base)
        schema = wire.response_schema(base)
        self.assertEqual(base, before)
        self.assertEqual(x02.STRUCTURE_SCHEMA, legacy)
        self.assertNotIn("chapter_aha_relations", schema["properties"])
        self.assertNotIn("chapter_aha_relations", schema["required"])
        chapter = schema["properties"]["storyline_proposals"]["items"]
        for name in ("observation_ids", "fact_ids"):
            self.assertNotIn(name, chapter["properties"])
            self.assertNotIn(name, chapter["required"])
        self.assertEqual(chapter["properties"]["beat_map"]["maxItems"],
                         before["properties"]["storyline_proposals"]["items"]
                         ["properties"]["observation_ids"]["maxItems"])
        relation = chapter["properties"]["aha_relations"]["items"]
        self.assertIn("aha_relations", chapter["required"])
        self.assertIn("observation_id", relation["required"])
        self.assertNotIn("chapter_key", relation["properties"])
        self.assertNotIn("aha_observation_id", relation["properties"])
        native = schema["properties"]["aha_proposals"]["items"]
        self.assertNotIn("key", native["properties"])
        self.assertNotIn("key", native["required"])
        chapter["properties"]["beat_map"]["items"]["required"].clear()
        self.assertEqual(base, before)
        self.assertEqual(x02.x02_runtime_policies()["structure_wire"], wire.POLICY_VERSION)
        self.assertEqual(wire.POLICY_FIELD, "structure_wire_policy_version")

    def test_three_recorded_packs_preserve_beats_native_payloads_and_inputs(self):
        for pack, case in self.cases.items():
            with self.subTest(pack=pack):
                recorded_before = copy.deepcopy(case)
                raw = project_recorded_legacy_wire(case)
                before = copy.deepcopy(raw)
                output, audit = wire.normalize_output(raw)
                self.assertEqual(raw, before)
                self.assertEqual(case, recorded_before)
                self.assertEqual(audit["facts_created"], 0)
                self.assertEqual(audit["model_calls_added"], 0)
                for source, derived in zip(raw["storyline_proposals"],
                                           output["storyline_proposals"]):
                    self.assertEqual(derived["beat_map"], source["beat_map"])
                    self.assertEqual(derived["observation_ids"],
                                     [beat["observation_id"] for beat in source["beat_map"]])
                    self.assertEqual(derived["fact_ids"],
                                     [fact for beat in source["beat_map"] for fact in beat["fact_ids"]])
                    self.assertEqual(derived["thesis"], source["thesis"])
                for source, derived in zip(raw["aha_proposals"], output["aha_proposals"]):
                    self.assertEqual(derived, {**source, "key": source["observation_id"]})
                # Editing the result must not reach back into the raw response.
                output["storyline_proposals"][0]["beat_map"][0]["fact_ids"].clear()
                self.assertEqual(raw, before)

    def test_recorded_town_invalid_redundant_fact_is_not_a_second_authority(self):
        case = self.cases[1]
        key = "historic_town_walks"
        _, old_ledger, _, _ = build(case, case["structure_output"])
        self.assertIn("STORYLINE_FACT_REFERENCE_INVALID",
                      ledger_entry(old_ledger, key)["reason_codes"])
        output, _ = wire.normalize_output(project_recorded_legacy_wire(case))
        chapters, ledger, _, _ = build(case, output)
        entry = ledger_entry(ledger, key)
        self.assertEqual(entry["validation_status"], "PASSED")
        chapter = next(item for item in chapters if item["candidate_id"] == entry["candidate_id"])
        original = next(p for p in case["structure_output"]["storyline_proposals"] if p["key"] == key)
        self.assertEqual(len(chapter["observation_ids"]), 7)
        self.assertEqual(set(chapter["observation_ids"]), set(original["observation_ids"]))
        self.assertEqual(chapter["storyline_identity"]["beat_map"], original["beat_map"])
        self.assertEqual(set(chapter["fact_ids"]),
                         {fact for beat in original["beat_map"] for fact in beat["fact_ids"]})
        # The old direct-builder path retains its original rejection.
        self.assertEqual(build(case, case["structure_output"])[1], old_ledger)

    def test_recorded_football_has_seven_beats_not_a_recovered_eighth_member(self):
        case = self.cases[3]
        key = "ch01_football_championship"
        original = next(p for p in case["structure_output"]["storyline_proposals"] if p["key"] == key)
        self.assertEqual(len(original["observation_ids"]), 8)
        self.assertEqual(len(original["beat_map"]), 7)
        _, old_ledger, _, _ = build(case, case["structure_output"])
        self.assertIn("STORYLINE_BEAT_COVERAGE_INCOMPLETE",
                      ledger_entry(old_ledger, key)["reason_codes"])
        output, _ = wire.normalize_output(project_recorded_legacy_wire(case))
        chapters, ledger, _, _ = build(case, output)
        entry = ledger_entry(ledger, key)
        self.assertEqual(entry["validation_status"], "PASSED")
        chapter = next(item for item in chapters if item["candidate_id"] == entry["candidate_id"])
        beat_ids = {beat["observation_id"] for beat in original["beat_map"]}
        self.assertEqual(set(chapter["observation_ids"]), beat_ids)
        self.assertEqual(len(set(original["observation_ids"]) - beat_ids), 1)
        self.assertEqual(chapter["storyline_identity"]["beat_map"], original["beat_map"])

    def test_recorded_pack_one_two_relations_survive_mechanical_nesting(self):
        for pack in (1, 2):
            case = self.cases[pack]
            output, audit = wire.normalize_output(project_recorded_legacy_wire(case))
            row_key = lambda row: (row["chapter_key"], row["aha_observation_id"])
            self.assertEqual(sorted(output["chapter_aha_relations"], key=row_key),
                             sorted(case["structure_output"]["chapter_aha_relations"], key=row_key))
            self.assertEqual(audit["flattened_relation_count"], 4 if pack == 1 else 5)
        # Real pack-2 rows include eligible deterministic candidates absent from
        # native proposals. The new transport must not lose that coverage.
        case = self.cases[2]
        output, _ = wire.normalize_output(project_recorded_legacy_wire(case))
        chapters, ledger, ahas, _ = build(case, output)
        plan = allocation.compile_relations(output, chapters, ledger, ahas)
        native_ids = {item["observation_id"] for item in output["aha_proposals"]}
        explicit = [row for row in plan["relations"] if row["relation"] == "SAME_STORY"
                    and row["aha_observation_id"] not in native_ids]
        self.assertEqual(len(explicit), 2)

    def test_legacy_native_aliases_need_explicit_test_projection_not_runtime_repair(self):
        case = self.cases[3]
        raw = project_recorded_legacy_wire(case)
        unresolved_output, _ = wire.normalize_output(raw)
        chapters, ledger, ahas, _ = build(case, unresolved_output)
        plan = allocation.compile_relations(unresolved_output, chapters, ledger, ahas)
        bad_bindings = [d for d in plan["diagnostics"]
                        if d["code"] == "AHA_OBSERVATION_NOT_UNIQUELY_BOUND"]
        self.assertEqual(len(bad_bindings), 8)
        self.assertTrue(all(row["relation"] == "UNRESOLVED" for row in plan["relations"]))
        output, _ = wire.normalize_output(project_recorded_legacy_wire(case, replay_native_keys=True))
        chapters, ledger, ahas, _ = build(case, output)
        plan = allocation.compile_relations(output, chapters, ledger, ahas)
        native = next(a for a in case["structure_output"]["aha_proposals"]
                      if a["key"] == "aha06_golden_temple_roof")
        old_row = next(r for r in case["structure_output"]["chapter_aha_relations"]
                       if r["aha_observation_id"] == native["key"])
        entry = ledger_entry(ledger, old_row["chapter_key"])
        aha = next(a for a in ahas if a["observation_id"] == native["observation_id"])
        pair = allocation.for_selection(plan, entry["candidate_id"], aha["candidate_id"])
        self.assertEqual(pair["relation"], old_row["relation"])
        self.assertEqual(pair["chapter_fact_ids"], old_row["chapter_fact_ids"])
        self.assertEqual(pair["aha_fact_ids"], old_row["aha_fact_ids"])
        self.assertEqual(pair["reason"], old_row["reason"])

    def test_invalid_beat_types_duplicates_and_fact_ownership_still_reject(self):
        case = self.cases[2]
        original = project_recorded_legacy_wire(case)
        key = original["storyline_proposals"][0]["key"]
        beats = original["storyline_proposals"][0]["beat_map"]
        invalid_lists = [None, [None] + copy.deepcopy(beats[1:]),
                         copy.deepcopy(beats) + [copy.deepcopy(beats[0])]]
        wrong_fact = copy.deepcopy(beats)
        wrong_fact[0]["fact_ids"] = copy.deepcopy(beats[1]["fact_ids"])
        invalid_lists.append(wrong_fact)
        missing_fact_list = copy.deepcopy(beats)
        missing_fact_list[0]["fact_ids"] = None
        invalid_lists.append(missing_fact_list)
        for index, invalid in enumerate(invalid_lists):
            with self.subTest(interface_probe=index):
                raw = copy.deepcopy(original)
                raw["storyline_proposals"][0]["beat_map"] = invalid
                output, _ = wire.normalize_output(raw)
                self.assertEqual(output["storyline_proposals"][0]["beat_map"], invalid)
                _, ledger, _, _ = build(case, output)
                self.assertEqual(ledger_entry(ledger, key)["validation_status"], "REJECTED")

    def test_missing_nested_relations_do_not_reuse_retired_top_level_rows(self):
        case = self.cases[2]
        raw = project_recorded_legacy_wire(case)
        raw["chapter_aha_relations"] = copy.deepcopy(case["structure_output"]["chapter_aha_relations"])
        for chapter in raw["storyline_proposals"]:
            chapter.pop("aha_relations")
        output, audit = wire.normalize_output(raw)
        self.assertEqual(output["chapter_aha_relations"], [])
        codes = [d["code"] for d in audit["diagnostics"]]
        self.assertIn("RETIRED_TOP_LEVEL_RELATIONS_IGNORED", codes)
        self.assertEqual(codes.count("NESTED_RELATIONS_MISSING_OR_INVALID"), 5)
        chapters, ledger, ahas, _ = build(case, output)
        plan = allocation.compile_relations(output, chapters, ledger, ahas)
        self.assertTrue(plan["relations"])
        self.assertTrue(all(row["relation"] == "UNRESOLVED" for row in plan["relations"]))


if __name__ == "__main__":
    unittest.main()

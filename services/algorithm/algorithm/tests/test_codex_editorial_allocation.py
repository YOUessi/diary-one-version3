"""Reference/transport checks, not semantic labels or a writing-quality gold set.

Recorded pack 2 / R2 supplies real IDs and facts. SAME/DISTINCT below are explicit
interface injections, not claims that those relations are visually correct.
The existing ContentBriefTests cover pipeline calls and output schemas.
"""

import copy
import json
import unittest
import uuid
from pathlib import Path

from diary_one_ci import codex_content_brief as brief
from diary_one_ci import codex_editorial_allocation as allocation
from diary_one_ci import x02


ROOT = Path(__file__).resolve().parents[1]
RECORDED = ROOT / "tests/fixtures/codex_v1_66_recorded_allocation_scope.json"
INTERFACE_REASON = "Interface relation injection only; not a semantic-quality label."
TABLE_OBSERVATION_ID = "8829dc31-f526-5c35-bfef-2392d7d13eeb"


class EditorialSchemaTests(unittest.TestCase):
    def test_extension_is_deep_copied_and_receipt_is_versioned(self):
        before = copy.deepcopy(x02.STRUCTURE_SCHEMA)
        extended = allocation.structure_schema(x02.STRUCTURE_SCHEMA)
        self.assertEqual(x02.STRUCTURE_SCHEMA, before)
        self.assertNotIn("chapter_aha_relations", before["properties"])
        self.assertIn("chapter_aha_relations", extended["required"])
        extended["properties"]["storyline_proposals"]["items"]["required"].clear()
        self.assertEqual(x02.STRUCTURE_SCHEMA, before)
        self.assertEqual(x02.x02_runtime_policies()["editorial_allocation"],
                         allocation.POLICY_VERSION)


class RecordedEditorialAllocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Versioned exact excerpt travels with source; no optional var/ lookup
        # or semantic substitute. Its original files and hashes are recorded.
        cls.record = json.loads(RECORDED.read_text(encoding="utf-8"))

    def setUp(self):
        self.data = copy.deepcopy(self.record)
        args = (uuid.UUID(self.data["session_id"]), self.data["observations"],
                self.data["roles"], self.data["moments"], self.data["structure_output"],
                self.data["asset_order"])
        self.chapters, self.chapter_ledger = x02._build_storyline_candidates(*args)
        self.ahas, self.aha_ledger = x02._build_aha_candidates(*args, value_first=True)
        self.chapter = next(c for c in self.chapters if TABLE_OBSERVATION_ID in c["observation_ids"])
        self.aha = next(a for a in self.ahas if a["observation_id"] == TABLE_OBSERVATION_ID)
        self.chapter_key = next(e["candidate_key"] for e in self.chapter_ledger
                                if e.get("candidate_id") == self.chapter["candidate_id"])

    def row(self, relation="DISTINCT_STORY", chapter=None, aha=None):
        chapter, aha = chapter or self.chapter, aha or self.aha
        key = next(e["candidate_key"] for e in self.chapter_ledger
                   if e.get("candidate_id") == chapter["candidate_id"])
        return {"chapter_key": key, "aha_observation_id": aha["observation_id"],
                "relation": relation, "chapter_fact_ids": [chapter["fact_ids"][0]],
                "aha_fact_ids": [aha["fact_ids"][0]], "reason": INTERFACE_REASON}

    def compile(self, rows, ledger=None):
        output = {**self.data["structure_output"], "chapter_aha_relations": rows}
        return allocation.compile_relations(output, self.chapters,
                                            self.chapter_ledger if ledger is None else ledger,
                                            self.ahas)

    def pair(self, plan):
        return allocation.for_selection(plan, self.chapter["candidate_id"], self.aha["candidate_id"])

    def select(self, plan, chapters=None, ahas=None):
        candidates = self.ahas if ahas is None else ahas
        ledger = copy.deepcopy(self.aha_ledger)
        selected, audit = x02._select_aha_set(
            candidates, ledger, [self.chapter] if chapters is None else chapters,
            self.data["observations"], self.data["asset_order"],
            value_first=True, allocation_plan=plan,
        )
        return selected, audit, ledger

    def test_real_id_binding_includes_event_candidate_and_does_not_mutate_input(self):
        before = copy.deepcopy((self.data, self.chapters, self.chapter_ledger, self.ahas))
        self.assertEqual(self.aha["proposal_source"], "DETERMINISTIC_EVENT_PEAK")
        plan = self.compile([self.row()])
        pair = self.pair(plan)
        self.assertEqual(len(plan["relations"]), len(self.chapters) * len(self.ahas))
        self.assertEqual(pair["relation"], "DISTINCT_STORY")
        self.assertEqual(pair["aha_observation_id"], TABLE_OBSERVATION_ID)
        self.assertEqual(pair["aha_fact_ids"], [self.aha["fact_ids"][0]])
        self.assertEqual((self.data, self.chapters, self.chapter_ledger, self.ahas), before)
        pair["aha_fact_ids"].clear()
        self.assertTrue(self.pair(plan)["aha_fact_ids"])

    def test_missing_duplicate_invalid_and_unaccepted_references_stay_unresolved(self):
        valid = self.row()
        wrong_chapter_fact = next(f["fact_id"] for o in self.data["observations"]
                                  for f in o["facts"] if f["fact_id"] not in self.chapter["fact_ids"])
        wrong_aha_fact = next(f["fact_id"] for o in self.data["observations"]
                              for f in o["facts"] if f["fact_id"] not in self.aha["fact_ids"])
        probes = [([], "RELATION_MISSING"), ([valid, copy.deepcopy(valid)],
                   "DUPLICATE_OR_CONFLICTING_RELATION_ROWS"),
                  ([{**valid, "chapter_fact_ids": [wrong_chapter_fact]}], "CHAPTER_FACT_REFERENCE_INVALID"),
                  ([{**valid, "aha_fact_ids": [wrong_aha_fact]}], "AHA_FACT_REFERENCE_INVALID")]
        for rows, code in probes:
            with self.subTest(code=code):
                pair = self.pair(self.compile(rows))
                self.assertEqual(pair["relation"], "UNRESOLVED")
                self.assertIn(code, pair["reason_codes"])
                self.assertEqual(pair["chapter_fact_ids"], [])
        # Ledger-state probes only. Do not bind an unaccepted or ambiguous key
        # to a surviving Chapter merely because the supplied facts match it.
        rejected = copy.deepcopy(self.chapter_ledger)
        entry = next(e for e in rejected if e.get("candidate_id") == self.chapter["candidate_id"])
        entry["validation_status"] = "REJECTED"
        self.assertEqual(self.pair(self.compile([valid], rejected))["relation"], "UNRESOLVED")
        collision = copy.deepcopy(self.chapter_ledger) + [entry]
        plan = self.compile([valid], collision)
        self.assertEqual(self.pair(plan)["relation"], "UNRESOLVED")
        self.assertTrue(any(d["code"] == "AMBIGUOUS_CHAPTER_KEY" for d in plan["diagnostics"]))

    def test_same_story_only_suppresses_aha_against_selected_chapter(self):
        original_chapter = copy.deepcopy(self.chapter)
        plan = self.compile([self.row("SAME_STORY")])
        selected, audit, _ = self.select(plan, ahas=[self.aha])
        self.assertEqual(selected, [])
        self.assertEqual(audit["chapter_conflicts"][0]["selection_effect"], "SUPPRESS_AHA_ONLY")
        self.assertEqual(self.chapter, original_chapter)
        selected, audit, _ = self.select(plan, chapters=[], ahas=[self.aha])
        self.assertEqual([a["candidate_id"] for a in selected], [self.aha["candidate_id"]])
        self.assertEqual(audit["chapter_conflicts"], [])

    def test_role_metadata_does_not_override_allocation_and_legacy_stays_separate(self):
        # Replacing one recorded role checks code-path invariance only; no role
        # or SAME/DISTINCT decision is asserted to be the correct interpretation.
        for relation in ("SAME_STORY", "DISTINCT_STORY"):
            plan = self.compile([self.row(relation)])
            memberships = []
            for role in ("INTERACTION", "PEAK", "RESULT"):
                chapter = copy.deepcopy(self.chapter)
                beat = next(b for b in chapter["storyline_identity"]["beat_map"]
                            if b["observation_id"] == TABLE_OBSERVATION_ID)
                beat["beat_role"] = role
                selected, _, _ = self.select(plan, [chapter], [self.aha])
                memberships.append([a["candidate_id"] for a in selected])
                if role == "PEAK":
                    legacy, legacy_audit, _ = self.select(None, [chapter], [self.aha])
                    self.assertEqual(legacy, [])
                    self.assertEqual(legacy_audit["rejections"][self.aha["candidate_id"]],
                                     "SAME_MODEL_ASSIGNED_CHAPTER_CORE_FACTS")
            self.assertEqual(memberships, [memberships[0]] * len(memberships))

    def test_distinct_does_not_override_capacity_and_missing_is_not_independence(self):
        missing = self.compile([])
        distinct = self.compile([self.row(aha=a) for a in self.ahas])
        baseline, base_audit, ledger = self.select(missing)
        selected, audit, _ = self.select(distinct)
        self.assertGreater(len(self.ahas), x02.MAX_AHAS)
        self.assertEqual([a["candidate_id"] for a in selected], [a["candidate_id"] for a in baseline])
        self.assertEqual(audit["candidate_rank_inputs"], base_audit["candidate_rank_inputs"])
        self.assertIn("AHA_PREVIEW_CAPACITY_REACHED", audit["rejections"].values())
        self.assertTrue(all(row["relation"] == "UNRESOLVED" for row in base_audit["chapter_relations"]))
        for entry in ledger:
            if entry["selection_status"] == "SELECTED":
                self.assertIn("VALUE_RANKED_AHA_SELECTED_RELATION_STATUS_RECORDED", entry["reason_codes"])
                self.assertNotIn("VALUE_RANKED_INDEPENDENT_AHA_SELECTED", entry["reason_codes"])

    def test_projection_requires_both_final_fact_scopes_and_never_creates_facts(self):
        plan = self.compile([self.row()])
        memories = [{"candidate_id": c["candidate_id"], "memory_type": kind,
                     "facts": [copy.deepcopy(f) for o in self.data["observations"] for f in o["facts"]
                               if f["fact_id"] in c["fact_ids"]]}
                    for c, kind in ((self.chapter, "CHAPTER"), (self.aha, "AHA"))]
        memories[0]["storyline_identity"] = copy.deepcopy(self.chapter["storyline_identity"])
        memories[1]["event_fact_ids"] = list(self.aha["event_fact_ids"])
        memories[1]["narrative_duty"] = self.aha["narrative_duty"]
        original = copy.deepcopy(memories)
        projected = allocation.project(plan, memories)
        self.assertEqual(len(projected["relations"]), 1)
        self.assertEqual(projected["guidance_scope"], "EDITORIAL_HINTS_NOT_FACT_EVIDENCE")
        context = {"locale": "zh-Hans", "memories": memories,
                   allocation.POLICY_FIELD: allocation.POLICY_VERSION, "editorial_allocation": projected}
        outgoing = brief.writer_input(context)
        self.assertEqual(outgoing["chapter_aha_relations"], projected["relations"])
        self.assertEqual([m["facts"] for m in outgoing["memories"]], [brief.compact_facts(m) for m in memories])
        for side, field in ((0, "chapter_fact_ids"), (1, "aha_fact_ids")):
            with self.subTest(side=side):
                trimmed = copy.deepcopy(memories)
                unavailable = self.pair(plan)[field][0]
                trimmed[side]["facts"] = [f for f in trimmed[side]["facts"] if f["fact_id"] != unavailable]
                result = allocation.project(plan, trimmed)
                self.assertEqual(result["relations"], [])
                self.assertTrue(any(d["code"] == "FINAL_RELATION_REFERENCES_OR_REASON_UNAVAILABLE"
                                    for d in result["diagnostics"]))
        self.assertEqual(allocation.project(plan, memories[:1])["relations"], [])
        self.assertEqual(allocation.project(self.compile([self.row("SAME_STORY")]), memories)["relations"], [])
        self.assertEqual(memories, original)


if __name__ == "__main__":
    unittest.main()

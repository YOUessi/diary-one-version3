"""Request/validation tests from real failures, not invented semantic scenarios."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path

from diary_one_ci import x02


TOOL = Path(__file__).resolve().parents[1] / "tools/codex_replay_aha_writer.py"
spec = importlib.util.spec_from_file_location("writer_replay", TOOL)
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)
repair = replay.repair


class AhaWriterRepairTests(unittest.TestCase):
    def setUp(self):
        self.recorded, self.context = replay.recorded_context()

    def test_all_four_recorded_live_outputs_fail_without_relaxing_contract(self):
        recorded = json.loads((Path(__file__).parent / "fixtures/codex_aha_writer_live_comparison_failed.json").read_text())
        self.assertEqual(len(recorded["calls"]), 4)
        for call in recorded["calls"]:
            accepted, audit, invalid = x02._validate_writer_output(call["output"], self.context, attempt=2)
            self.assertEqual(accepted, {})
            self.assertEqual(len(invalid), 3)
            self.assertTrue(all("AHA_MOMENT_LINE_INVALID" in item["reason_codes"] for item in audit))

    def test_failed_experiment_is_not_imported_or_selected_by_live_pipeline(self):
        source = Path(x02.__file__).read_text()
        self.assertNotIn("codex_aha_writer_prompt_experiment", source)
        self.assertNotIn("_uses_focused_aha_repair", source)
        self.assertNotIn("writer_request_policy_version", x02._writer_retry_context(
            self.context, [item["candidate_id"] for item in self.context["memories"]],
            self.context["previous_failures"],
        ))

    def test_actual_failed_drafts_still_fail_the_unchanged_twenty_character_limit(self):
        for attempt, expected_counts in ((1, [26, 30, 28]), (2, [41, 30, 35])):
            drafts = [item for item in self.recorded["writer_audit"] if item["attempt"] == attempt]
            facts = {item["candidate_id"]: item["event_fact_ids"] for item in self.context["memories"]}
            output = {"chapters": [], "ahas": [{
                "candidate_id": item["candidate_id"], "title": item["draft_title"],
                "text": item["draft_text"], "claim_ids": facts[item["candidate_id"]],
            } for item in drafts]}
            accepted, audit, invalid = x02._validate_writer_output(output, self.context, attempt=attempt)
            self.assertEqual(accepted, {})
            self.assertEqual(len(invalid), 3)
            self.assertEqual([item["text_visible_characters"] for item in audit], expected_counts)
            self.assertTrue(all("AHA_MOMENT_LINE_INVALID" in item["reason_codes"] for item in audit))
        self.assertEqual(self.context["writer_request_policy_version"], repair.X02_WRITER_REQUEST_POLICY_VERSION)

    def test_retry_projects_metadata_not_facts_and_never_mutates_ledger(self):
        before = copy.deepcopy(self.context)
        prompt = repair._writer_prompt(self.context, retry=True)
        projected = json.loads(prompt.split("Input:\n", 1)[1])
        self.assertEqual(self.context, before)
        for original, outgoing in zip(self.context["memories"], projected["memories"]):
            self.assertEqual(original["candidate_id"], outgoing["candidate_id"])
            self.assertEqual(original["narrative_duty"], outgoing["narrative_duty"])
            self.assertEqual(original["event_fact_ids"], outgoing["event_fact_ids"])
            self.assertEqual(outgoing["facts"], [{"fact_id": fact["fact_id"], "text": fact["text"]} for fact in original["facts"]])
            self.assertNotIn("selected_media", outgoing)
            self.assertNotIn("episode_code", outgoing)
        self.assertEqual(projected["previous_failures"], before["previous_failures"])
        self.assertIn("不需要覆盖整条 fact 的所有细节", prompt)

    def test_first_attempt_and_legacy_retry_are_unchanged(self):
        self.assertEqual(repair._writer_prompt(self.context, retry=False), x02._writer_prompt(self.context, retry=False))
        self.assertIs(repair._writer_request_schema(self.context, retry=False), x02.WRITER_SCHEMA)
        context = copy.deepcopy(self.context)
        context.pop("writer_grounding_policy")
        self.assertEqual(repair._writer_prompt(context, retry=True), x02._writer_prompt(context, retry=True))
        self.assertIs(repair._writer_request_schema(context, retry=True), x02.WRITER_SCHEMA)

    def test_request_schema_does_not_mutate_shared_contract_or_chapter_limits(self):
        before = copy.deepcopy(x02.WRITER_SCHEMA)
        schema = repair._writer_request_schema(self.context, retry=True)
        self.assertEqual(x02.WRITER_SCHEMA, before)
        self.assertEqual(schema["properties"]["chapters"], before["properties"]["chapters"])
        self.assertIn("20", schema["properties"]["ahas"]["items"]["properties"]["text"]["description"])
        self.assertEqual(x02.AHA_MOMENT_LINE_VISIBLE_MAX, 20)

    def test_chapter_only_retry_does_not_use_aha_repair(self):
        # The real Chapter is only a dispatch check, not a claimed past failure.
        context = copy.deepcopy(self.context)
        context["memories"] = [self.recorded["chapter_memory"]]
        context["previous_failures"] = []
        self.assertFalse(repair._uses_focused_aha_repair(context, retry=True))
        self.assertEqual(repair._writer_prompt(context, retry=True), x02._writer_prompt(context, retry=True))

    def test_mixed_retry_preserves_chapter_data_and_single_batch(self):
        context = copy.deepcopy(self.context)
        context["memories"].insert(0, self.recorded["chapter_memory"])
        original = copy.deepcopy(context)
        prompt = repair._writer_prompt(context, retry=True)
        outgoing, _ = json.JSONDecoder().raw_decode(prompt.split("Input:\n", 1)[1])
        self.assertEqual(len(outgoing["memories"]), len(context["memories"]))
        self.assertEqual(outgoing["memories"][0], context["memories"][0])
        self.assertEqual(context, original)
        self.assertIn("Aha 定向重写", prompt)


if __name__ == "__main__":
    unittest.main()

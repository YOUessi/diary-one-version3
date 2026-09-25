"""Recorded Writer failures and transport checks, not semantic quality gold."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from diary_one_ci import codex_writer_exit as exit_policy
from diary_one_ci import x02
from test_codex_x02_chapter_media import MediaGateway
from test_x02 import make_x02_bundle_v03


class WriterExitTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((Path(__file__).parent / "fixtures/codex_writer_exit_real.json").read_text())

    def case(self, name, enable=True):
        case = next(c for c in self.record["cases"] if c["case_id"] == name)
        context = copy.deepcopy(self.record["contexts"][case["context_key"]])
        if enable:
            context[exit_policy.POLICY_FIELD] = exit_policy.POLICY_VERSION
        return copy.deepcopy(case["output"]), context

    def test_real_wrong_bucket_copies_do_not_replace_or_discard_correct_aha_text(self):
        output, context = self.case("v148_attempt_2")
        original = copy.deepcopy(output)
        normalized, notes = exit_policy.normalize_buckets(output, context)
        self.assertEqual(normalized["ahas"], original["ahas"])
        self.assertEqual(normalized["chapters"], [])
        self.assertEqual(output, original)
        _, audit, _ = x02._validate_writer_output(output, context)
        self.assertEqual(len(notes), 3)
        for entry in audit:
            self.assertNotIn("WRITER_ITEM_DUPLICATED", entry["reason_codes"])
            self.assertEqual(entry["normalization_codes"], ["WRITER_WRONG_BUCKET_COPY_IGNORED"])
            self.assertEqual(entry["ignored_wrong_bucket_copy_count"], 1)
            self.assertEqual(entry[exit_policy.POLICY_FIELD], exit_policy.POLICY_VERSION)

    def test_correct_bucket_ambiguity_is_not_resolved_by_picking_a_shorter_version(self):
        output, context = self.case("v148_attempt_2")
        # Move an actual conflicting reply into the correct bucket: structure only.
        output["ahas"].append(copy.deepcopy(output["chapters"][0]))
        candidate_id = output["ahas"][0]["candidate_id"]
        _, audit, invalid = x02._validate_writer_output(output, context)
        self.assertIn(candidate_id, invalid)
        self.assertIn("WRITER_ITEM_DUPLICATED", next(a for a in audit if a["candidate_id"] == candidate_id)["reason_codes"])

    def test_real_missing_fact_references_are_not_invented(self):
        output, context = self.case("v151_attempt_1")
        original = copy.deepcopy(output)
        accepted, audit, invalid = x02._validate_writer_output(output, context)
        self.assertEqual(accepted, {})
        self.assertEqual(len(invalid), 6)
        self.assertTrue(all(a["validation_status"] == "REJECTED" for a in audit))
        self.assertEqual(output, original)

    def test_unmarked_archived_context_keeps_legacy_validation(self):
        output, context = self.case("v148_attempt_2", enable=False)
        _, audit, invalid = x02._validate_writer_output(output, context)
        self.assertEqual(len(invalid), 3)
        self.assertTrue(all("WRITER_ITEM_DUPLICATED" in a["reason_codes"] for a in audit))

    def test_current_pipeline_does_not_rewrite_failed_copy(self):
        class CaptureGateway(MediaGateway):
            def call(self, stage, prompt, schema, evidence=(), context=None):
                if stage.startswith("S11_"):
                    self.writer_schema = copy.deepcopy(schema)
                return super().call(stage, prompt, schema, evidence, context)

        with tempfile.TemporaryDirectory() as temporary:
            gateway = CaptureGateway(fail_all_writer=True)
            result = x02.run_x02(make_x02_bundle_v03(Path(temporary)), gateway)
        calls = [c for c in gateway.calls if c["stage"].startswith("S11_")]
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["context"][exit_policy.POLICY_FIELD], exit_policy.POLICY_VERSION)
        self.assertIn("以 20 字为写作目标，21–24 字也可接受", calls[0]["prompt"])
        self.assertNotIn("at most 20", json.dumps(gateway.writer_schema))
        self.assertIn("21-24 are acceptable", json.dumps(gateway.writer_schema))
        status = next(s for s in result["decision_trace"]["stage_statuses"] if s["stage"] == "S11_GROUNDED_NARRATIVE")
        self.assertIn("WRITER_SINGLE_PASS_NO_MODEL_REWRITE", status["reason_codes"])
        self.assertNotIn("BOUNDED_WRITER_RETRY", status["reason_codes"])

    def test_real_20_and_24_character_lines_are_accepted_without_length_review(self):
        output, context = self.case("v151_attempt_2")
        accepted, audit, invalid = x02._validate_writer_output(output, context)
        self.assertEqual(invalid, [])
        ahas = [a for a in audit if a["memory_type"] == "AHA"]
        self.assertEqual([a["text_visible_characters"] for a in ahas], [20, 20, 24])
        self.assertEqual([a["length_status"] for a in ahas], ["WITHIN_TARGET", "WITHIN_TARGET", "WITHIN_TOLERANCE"])
        for raw in output["ahas"]:
            self.assertEqual(accepted[raw["candidate_id"]]["text"], raw["text"])
        self.assertTrue(all(not a["length_review_required"] and not a["quality_flags"] for a in ahas))
        self.assertTrue(all("required_text_visible_max" not in a for a in ahas))

    def test_real_long_first_reply_is_retained_and_flagged_not_rewritten(self):
        output, context = self.case("v148_attempt_1")
        original = copy.deepcopy(output)
        accepted, audit, invalid = x02._validate_writer_output(output, context)
        self.assertEqual(invalid, [])
        ahas = [a for a in audit if a["memory_type"] == "AHA"]
        self.assertEqual([a["text_visible_characters"] for a in ahas], [38, 41, 41])
        for raw in output["ahas"]:
            self.assertEqual(accepted[raw["candidate_id"]]["text"], raw["text"])
            entry = next(a for a in ahas if a["candidate_id"] == raw["candidate_id"])
            self.assertEqual(entry["quality_flags"], ["AHA_LENGTH_OVER_TOLERANCE_REVIEW"])
            self.assertEqual(entry["length_review_label"], "偏长，待评价")
            self.assertEqual(entry["validation_scope"], "FORMAT_AND_REFERENCES_ONLY_NOT_SEMANTIC_VERIFICATION")
        self.assertEqual(output, original)

    def test_real_cross_bucket_reply_uses_same_soft_policy(self):
        output, context = self.case("v148_attempt_2")
        accepted, audit, invalid = x02._validate_writer_output(output, context)
        self.assertEqual(invalid, [])
        self.assertEqual(len(accepted), 3)
        self.assertEqual([a["text_visible_characters"] for a in audit], [23, 26, 26])
        self.assertEqual([a["length_review_required"] for a in audit], [False, True, True])

    def test_v01_retains_its_length_policy_and_context_is_not_upgraded(self):
        output, context = self.case("v148_attempt_2")
        context[exit_policy.POLICY_FIELD] = exit_policy.LEGACY_POLICY_VERSION
        _, audit, invalid = x02._validate_writer_output(output, context)
        self.assertEqual(len(invalid), 3)
        self.assertTrue(all(a["reason_codes"] == ["AHA_MOMENT_LINE_INVALID"] for a in audit))
        retry = x02._writer_retry_context(context, invalid, audit)
        self.assertEqual(retry[exit_policy.POLICY_FIELD], exit_policy.LEGACY_POLICY_VERSION)
        self.assertTrue(all(a[exit_policy.POLICY_FIELD] == exit_policy.LEGACY_POLICY_VERSION for a in audit))
        context[exit_policy.POLICY_FIELD] = exit_policy.POLICY_VERSION
        context["locale"] = "en-US"
        self.assertFalse(exit_policy.soft_length_enabled(context))

    def test_prompt_and_schema_share_soft_target_without_mutating_legacy_schema(self):
        _, context = self.case("v148_attempt_1")
        original = copy.deepcopy(x02.WRITER_SCHEMA)
        prompt = x02._writer_prompt(context, retry=False)
        self.assertIn("以 20 字为写作目标，21–24 字也可接受", prompt)
        self.assertNotIn("最多 20 字", prompt)
        schema = exit_policy.response_schema(x02.WRITER_SCHEMA, context)
        self.assertNotIn("at most 20", json.dumps(schema))
        self.assertIn("21-24 are acceptable", json.dumps(schema))
        self.assertEqual(x02.WRITER_SCHEMA, original)
        self.assertIsNot(schema["properties"]["chapters"]["items"], schema["properties"]["ahas"]["items"])
        projected = json.loads(prompt.split("Input:\n", 1)[1])
        self.assertEqual(projected[exit_policy.POLICY_FIELD], exit_policy.POLICY_VERSION)

    def test_soft_length_keeps_sentence_reference_and_payload_checks(self):
        output, context = self.case("v151_attempt_2")
        original = output["ahas"][2]
        candidate_id = original["candidate_id"]
        # Structural probes using recorded prose, not constructed semantic claims.
        variants = [
            ({"text": original["text"] * 2}, "AHA_MOMENT_LINE_INVALID"),
            ({"text": original["text"] * x02.WRITER_TEXT_PAYLOAD_MAX}, "WRITER_TEXT_PAYLOAD_TOO_LARGE"),
            ({"claim_ids": output["chapters"][0]["claim_ids"]}, "WRITER_CLAIM_REFERENCE_INVALID"),
        ]
        for changes, reason in variants:
            with self.subTest(reason=reason):
                changed = copy.deepcopy(output)
                changed["ahas"][2].update(changes)
                _, audit, invalid = x02._validate_writer_output(changed, context)
                self.assertIn(candidate_id, invalid)
                self.assertIn(reason, next(a for a in audit if a["candidate_id"] == candidate_id)["reason_codes"])

    def test_real_complete_fact_fallback_is_not_cut_to_twenty_characters(self):
        _, context = self.case("v151_attempt_1")
        context["memories"] = [m for m in context["memories"] if m["memory_type"] == "AHA"]
        original = copy.deepcopy(context)
        output, _ = x02._deterministic_writer_fallback(context)
        accepted, audit, invalid = x02._validate_writer_output(
            output, context, surface_source="DETERMINISTIC_GROUNDED_FALLBACK")
        self.assertEqual(invalid, [])
        self.assertEqual(len(accepted), 3)
        for raw in output["ahas"]:
            memory = next(m for m in context["memories"] if m["candidate_id"] == raw["candidate_id"])
            fact = next(f for f in memory["facts"] if f["fact_id"] == raw["claim_ids"][0])
            self.assertEqual(raw["text"], fact["text"])
        self.assertTrue(all(a["length_review_required"] for a in audit))
        self.assertTrue(all(a["validation_scope"] == "COMPLETE_FACT_COPY_FORMAT_AND_REFERENCES" for a in audit))
        self.assertEqual(context, original)


if __name__ == "__main__":
    unittest.main()

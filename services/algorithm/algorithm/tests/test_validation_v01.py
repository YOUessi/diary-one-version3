import copy
import json
import tempfile
import unittest
from pathlib import Path

from diary_one_ci.validation_cases_v01 import build_reference_suite
from diary_one_ci.validation_v01 import (
    ValidationContractError,
    evaluate_trial,
    load_validation_suite,
    run_validation_suite,
    validate_validation_suite,
    write_validation_scorecard,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures/validation_v01/semantic_day_suite_v01.json"


class ValidationV01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite = load_validation_suite(FIXTURE)
        cls.scorecard = run_validation_suite(cls.suite)

    def test_reference_fixture_matches_deterministic_builder(self):
        self.assertEqual(self.suite, build_reference_suite())

    def test_contract_has_twelve_days_sixteen_trials_and_full_nominal_coverage(self):
        summary = validate_validation_suite(copy.deepcopy(self.suite))
        self.assertEqual(summary["day_count"], 12)
        self.assertEqual(summary["trial_count"], 16)
        self.assertEqual(summary["design_gold_day_count"], 12)
        self.assertEqual(summary["human_gold_day_count"], 0)
        self.assertEqual(self.suite["narrative_locale"], "zh-CN")

    def test_timelines_expand_to_explicit_two_minute_windows(self):
        self.assertEqual(sum(len(day["timeline"]) for day in self.suite["days"]), 609)
        for day in self.suite["days"]:
            minutes = [window["capture_minute"] for window in day["timeline"]]
            self.assertEqual(minutes, sorted(minutes))
            self.assertTrue(
                all((second - first) % 2 == 0 for first, second in zip(minutes, minutes[1:]))
            )

    def test_suite_conformance_and_separated_outcomes(self):
        self.assertEqual(self.scorecard["status"], "VALIDATION_SUITE_PASS")
        self.assertEqual(
            self.scorecard["aggregate"]["evaluation_status_counts"],
            {"PASS": 11, "REVIEW": 1, "QUALITY_FAIL": 1, "BLOCKING_FAIL": 3},
        )
        self.assertEqual(self.scorecard["aggregate"]["conformance_pass_count"], 16)
        self.assertEqual(self.scorecard["aggregate"]["conformance_fail_count"], 0)

    def test_design_gold_never_becomes_an_accuracy_claim(self):
        self.assertEqual(
            self.scorecard["accuracy_claim_status"],
            "NOT_ELIGIBLE_DESIGN_GOLD_ONLY",
        )
        self.assertTrue(self.scorecard["no_overall_score"])
        self.assertNotIn("overall_score", self.scorecard)
        self.assertFalse(any(result["accuracy_claim_eligible"] for result in self.scorecard["trial_results"]))

    def test_failure_injections_have_expected_attribution(self):
        codes_by_trial = {
            result["trial_id"]: {issue["code"] for issue in result["issues"]}
            for result in self.scorecard["trial_results"]
        }
        self.assertIn("FALSE_SPLIT", codes_by_trial["T-D01-FALSE-SPLIT"])
        self.assertIn("SAME_STORY_AHA", codes_by_trial["T-D02-SAME-STORY-AHA"])
        self.assertIn("UNSUPPORTED_ASSERTION", codes_by_trial["T-D06-UNSUPPORTED-TASTE"])
        self.assertIn("FALSE_MERGE", codes_by_trial["T-D09-FALSE-MERGE"])

    def test_optional_embedded_aha_remains_review_not_forced_output(self):
        result = next(
            item for item in self.scorecard["trial_results"] if item["trial_id"] == "T-D11-NOMINAL"
        )
        self.assertEqual(result["evaluation_status"], "REVIEW")
        self.assertEqual(
            {issue["code"] for issue in result["issues"]},
            {"OPTIONAL_MEMORY_REVIEW"},
        )

    def test_correspondence_does_not_depend_on_memory_ids(self):
        day = copy.deepcopy(next(day for day in self.suite["days"] if day["day_id"] == "D01"))
        trial = copy.deepcopy(next(trial for trial in self.suite["trials"] if trial["trial_id"] == "T-D01-NOMINAL"))
        for index, memory in enumerate(trial["prediction"]["memories"]):
            old_id = memory["memory_id"]
            memory["memory_id"] = f"RENAMED-{index}"
            for media_index, media in enumerate(memory["media"]):
                media["media_id"] = f"RENAMED-{index}-M{media_index}"
            self.assertNotEqual(old_id, memory["memory_id"])
        result = evaluate_trial(day, trial)
        self.assertEqual(result["evaluation_status"], "PASS")

    def test_unsupported_and_misaligned_media_are_separate(self):
        day = copy.deepcopy(next(day for day in self.suite["days"] if day["day_id"] == "D01"))
        trial = copy.deepcopy(next(trial for trial in self.suite["trials"] if trial["trial_id"] == "T-D01-NOMINAL"))
        trial["prediction"]["memories"][0]["media"][0]["semantic_atom"] = "invented_scene"
        blocking = evaluate_trial(day, trial)
        self.assertIn("UNSUPPORTED_MEDIA_ATOM", {issue["code"] for issue in blocking["issues"]})
        self.assertEqual(blocking["evaluation_status"], "BLOCKING_FAIL")

        trial = copy.deepcopy(next(trial for trial in self.suite["trials"] if trial["trial_id"] == "T-D01-NOMINAL"))
        trial["prediction"]["memories"][0]["media"][0]["semantic_atom"] = "tea_shop_visit"
        quality = evaluate_trial(day, trial)
        self.assertIn("MEDIA_MEMORY_ALIGNMENT_INVALID", {issue["code"] for issue in quality["issues"]})
        self.assertEqual(quality["evaluation_status"], "QUALITY_FAIL")

    def test_cross_memory_media_reuse_is_visible(self):
        day = copy.deepcopy(next(day for day in self.suite["days"] if day["day_id"] == "D09"))
        trial = copy.deepcopy(next(trial for trial in self.suite["trials"] if trial["trial_id"] == "T-D09-NOMINAL"))
        reused_id = trial["prediction"]["memories"][0]["media"][0]["media_id"]
        trial["prediction"]["memories"][1]["media"][0]["media_id"] = reused_id
        result = evaluate_trial(day, trial)
        self.assertIn("CROSS_MEMORY_MEDIA_REUSE", {issue["code"] for issue in result["issues"]})
        self.assertEqual(result["evaluation_status"], "QUALITY_FAIL")

    def test_unsafe_design_gold_accuracy_claim_is_rejected(self):
        suite = copy.deepcopy(self.suite)
        suite["days"][0]["gold"]["accuracy_eligible"] = True
        with self.assertRaisesRegex(ValidationContractError, "DESIGN_GOLD_CLAIM_INVALID"):
            validate_validation_suite(suite)

    def test_non_two_minute_timeline_is_rejected(self):
        suite = copy.deepcopy(self.suite)
        suite["days"][0]["timeline"][1]["capture_minute"] += 1
        with self.assertRaisesRegex(ValidationContractError, "TIMELINE_CADENCE_INVALID"):
            validate_validation_suite(suite)

    def test_english_cannot_reuse_the_chinese_length_contract(self):
        suite = copy.deepcopy(self.suite)
        suite["narrative_locale"] = "en-US"
        with self.assertRaisesRegex(ValidationContractError, "NARRATIVE_LOCALE_UNSUPPORTED"):
            validate_validation_suite(suite)

    def test_day_state_output_shape_is_a_blocking_invariant(self):
        day = copy.deepcopy(next(day for day in self.suite["days"] if day["day_id"] == "D04"))
        trial = copy.deepcopy(next(trial for trial in self.suite["trials"] if trial["trial_id"] == "T-D01-NOMINAL"))
        trial["day_id"] = "D04"
        trial["prediction"]["day_state"] = "EMPTY_DAY"
        result = evaluate_trial(day, trial)
        self.assertEqual(result["evaluation_status"], "BLOCKING_FAIL")
        self.assertIn("DAY_STATE_OUTPUT_SHAPE_INVALID", {issue["code"] for issue in result["issues"]})

    def test_suite_id_cannot_escape_the_artifact_directory(self):
        suite = copy.deepcopy(self.suite)
        suite["suite_id"] = "../outside"
        with self.assertRaisesRegex(ValidationContractError, "SUITE_ID_INVALID"):
            validate_validation_suite(suite)

    def test_two_item_chapter_needs_an_explicit_compact_gate(self):
        suite = copy.deepcopy(self.suite)
        memory = suite["days"][0]["gold"]["memories"][0]
        memory["media_count_range"] = [2, 5]
        with self.assertRaisesRegex(ValidationContractError, "GOLD_MEDIA_RANGE_INVALID"):
            validate_validation_suite(suite)

        memory["media_policy"] = "COMPACT_2_TO_5"
        memory["compact_pair_gate_ref"] = "D01-COMPACT-GATE"
        summary = validate_validation_suite(suite)
        self.assertEqual(summary["status"], "VALIDATION_SUITE_CONTRACT_PASS")

    def test_chinese_title_soft_extension_and_second_sentence_need_reasons(self):
        day = copy.deepcopy(next(day for day in self.suite["days"] if day["day_id"] == "D01"))
        trial = copy.deepcopy(next(trial for trial in self.suite["trials"] if trial["trial_id"] == "T-D01-NOMINAL"))
        narrative = trial["prediction"]["memories"][0]["narrative"]
        narrative["title"] = "古镇石板路上的清晨漫步"
        narrative["story"] = "石板路向前。木雕在转角出现。"
        missing = evaluate_trial(day, trial)
        missing_codes = {issue["code"] for issue in missing["issues"]}
        self.assertIn("TITLE_SOFT_EXTENSION_REASON_MISSING", missing_codes)
        self.assertIn("SECOND_SENTENCE_INCREMENT_MISSING", missing_codes)

        narrative["title_soft_extension_reason"] = "保留古镇与清晨两个必要信息"
        narrative["second_sentence_increment_atom"] = "wood_carving"
        grounded = evaluate_trial(day, trial)
        self.assertEqual(grounded["evaluation_status"], "PASS")

    def test_every_day_requires_exactly_one_nominal_reference(self):
        suite = copy.deepcopy(self.suite)
        trial = next(
            trial for trial in suite["trials"] if trial["trial_id"] == "T-D12-NOMINAL"
        )
        trial["trial_kind"] = "FAILURE_INJECTION"
        trial["expected_evaluation"] = {
            "status": "BLOCKING_FAIL",
            "required_error_codes": ["TEST_INJECTION"],
        }
        with self.assertRaisesRegex(ValidationContractError, "NOMINAL_TRIAL_COVERAGE_INVALID"):
            validate_validation_suite(suite)

    def test_all_canonical_concepts_exist_in_frozen_registry(self):
        registry = json.loads(
            (ROOT / "contracts/canonical_concept_registry_v1.json").read_text(encoding="utf-8")
        )
        registry_ids = {concept["concept_id"] for concept in registry["concepts"]}
        suite_ids = {
            concept
            for day in self.suite["days"]
            for memory in day["gold"]["memories"]
            for key in ("required_concept_ids", "allowed_concept_ids", "forbidden_concept_ids")
            for concept in memory[key]
        } | {
            concept
            for trial in self.suite["trials"]
            for memory in trial["prediction"]["memories"]
            for concept in memory["canonical_concept_ids"]
        }
        self.assertEqual(suite_ids - registry_ids, set())

    def test_contract_schemas_are_valid_json(self):
        for name in (
            "day_eval_case_v01.schema.json",
            "validation_suite_v01.schema.json",
            "validation_scorecard_v01.schema.json",
        ):
            schema = json.loads((ROOT / "contracts" / name).read_text(encoding="utf-8"))
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_scorecard_artifact_is_deterministic_and_snapshots_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = write_validation_scorecard(self.suite, root)
            first_scorecard = (first / "validation_scorecard.json").read_bytes()
            second = write_validation_scorecard(self.suite, root)
            self.assertEqual(first, second)
            self.assertEqual(first_scorecard, (second / "validation_scorecard.json").read_bytes())
            self.assertEqual(
                json.loads((first / "validation_suite.snapshot.json").read_text(encoding="utf-8")),
                self.suite,
            )


if __name__ == "__main__":
    unittest.main()

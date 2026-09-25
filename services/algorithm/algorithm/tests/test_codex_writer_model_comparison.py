"""Recorded request/format checks; passing does not certify natural wording."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path

from diary_one_ci import x02


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("model_check", ROOT / "tools/codex_compare_writer_models.py")
comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)


class WriterModelComparisonTests(unittest.TestCase):
    def setUp(self):
        self.results = json.loads((ROOT / "tests/fixtures/codex_writer_model_comparison_v1_39.json").read_text())
        self.source = json.loads((ROOT / "tests/fixtures/codex_aha_writer_real_failures.json").read_text())
        observations = {item["id"]: item for item in self.source["observations"]}
        self.context = {
            "locale": "zh-Hans", "writer_grounding_policy": x02.X02_WRITER_GROUNDING_POLICY,
            "memories": [{
                "candidate_id": item["candidate_id"], "memory_type": "AHA",
                "facts": observations[item["observation_id"]]["facts"],
                "event_fact_ids": [fact["fact_id"] for fact in observations[item["observation_id"]]["facts"]],
            } for item in self.source["selected_ahas"]],
        }

    def test_four_actual_responses_pass_only_format_and_reference_validation(self):
        self.assertEqual(len(self.results["calls"]), 4)
        for call in self.results["calls"]:
            accepted, audit, invalid = x02._validate_writer_output(call["output"], self.context, attempt=2)
            self.assertEqual(len(accepted), 3)
            self.assertEqual(invalid, [])
            self.assertTrue(all(a["validation_scope"] == "FORMAT_AND_REFERENCES_ONLY_NOT_SEMANTIC_VERIFICATION" for a in audit))

    def test_recorded_requests_have_one_common_non_model_fingerprint(self):
        self.assertEqual(len({call["non_model_request_sha256"] for call in self.results["calls"]}), 1)
        for call in self.results["calls"]:
            self.assertEqual(call["only_changed_request_field"], "model")
            self.assertEqual(call["model"], call["response_model"])
            self.assertEqual(call["http_status"], 200)
            self.assertEqual(call["finish_reasons"], ["stop"])

    def test_request_builder_only_changes_model_and_does_not_mutate_source(self):
        request = {"model": "qwen3-vl-flash-2026-01-22", "messages": [{"role": "user", "content": [
            {"type": "text", "text": json.dumps(self.context, ensure_ascii=False)}]}],
            "enable_thinking": False, "stream": False, "response_format": {"type": "json_object"}}
        before = copy.deepcopy(request)
        changed = comparison.model_only_request(request, comparison.MODELS["flash"][0])
        self.assertEqual(request, before)
        self.assertEqual({key for key in request if request[key] != changed[key]}, {"model"})

    def test_no_model_comparison_has_been_deployed_in_active_pipeline(self):
        source = Path(x02.__file__).read_text()
        self.assertNotIn("codex_compare_writer_models", source)
        for model, _, _ in comparison.MODELS.values():
            self.assertNotIn(model, source)


if __name__ == "__main__":
    unittest.main()

"""Display/reference tests, not invented scene semantics or visual-quality gold."""

import copy
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from diary_one_ci import codex_chapter_media as media
from diary_one_ci import x02
from test_x02 import ScriptedGateway, make_x02_bundle_v03


class MediaGateway(ScriptedGateway):
    def __init__(self, display_count=3, fail=False, **kwargs):
        super().__init__(**kwargs)
        self.display_count = display_count
        self.fail = fail

    def call(self, stage, prompt, schema, evidence=(), context=None):
        run = super().call(stage, prompt, schema, evidence, context)
        if stage.startswith("S10_CHAPTER_VISUAL_SELECTION_"):
            if self.fail:
                run = replace(run, call_status="HTTP_FAILED")
                raise x02.X02StageCallError("test transport failure", stage_run=run, code="MODEL_HTTP_503")
            run.output["display_count"] = self.display_count
        return run


class ChapterDisplayTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).parent / "fixtures/codex_chapter_media_real_members.json"
        self.members = json.loads(path.read_text())["members"]

    def test_four_recorded_members_can_display_three_without_deleting_membership(self):
        original = copy.deepcopy(self.members)
        by_name = {item["file"]: item["id"] for item in self.members}
        # Actual inspected files; prescribed ranking tests transport, not model skill.
        rank = [by_name[name] for name in ("13.jpg", "11.jpg", "10.jpg", "12.jpg")]
        choice = media.choose_display(self.members, {
            "ranked_observation_ids": rank, "display_count": 3, "reason": "",
        })
        self.assertEqual(choice["selected_observation_ids"], rank[:3])
        self.assertEqual(choice["omitted_observation_ids"], [by_name["12.jpg"]])
        self.assertEqual(self.members, original)
        self.assertFalse(choice["candidate_membership_changed"])

    def test_requested_count_below_floor_keeps_first_three_ranked_members(self):
        rank = [item["id"] for item in self.members]
        choice = media.choose_display(self.members, {"ranked_observation_ids": rank, "display_count": 1})
        self.assertEqual(choice["selected_observation_ids"], rank[:3])
        self.assertTrue(choice["count_adjusted_to_display_contract"])

    def test_three_members_and_invalid_reference_output_do_not_erase_the_chapter(self):
        exact = media.choose_display(self.members[:3])
        self.assertEqual(len(exact["selected_observation_ids"]), 3)
        invalid = media.choose_display(self.members, {"ranked_observation_ids": [], "display_count": 3})
        self.assertEqual(len(invalid["selected_observation_ids"]), 3)
        self.assertEqual(invalid["selection_source"], "QUALITY_ONLY_FALLBACK_NOT_DEDUP_VERIFIED")

    def run_fixture(self, gateway):
        with tempfile.TemporaryDirectory() as temporary:
            return x02.run_x02(make_x02_bundle_v03(Path(temporary)), gateway)

    def test_pipeline_records_visual_call_usage_and_publishes_three_not_five(self):
        gateway = MediaGateway()
        result = self.run_fixture(gateway)
        self.assertEqual(result["chapter_media_policy_version"], media.POLICY_VERSION)
        self.assertEqual(len(result["chapters"][0]["selected_media"]), 3)
        entry = result["decision_trace"]["s10_chapter_media"][0]
        self.assertEqual(entry["candidate_content_unit_count"], 5)
        self.assertEqual(entry["display_selection"]["selection_source"], "MODEL_VISUAL_SELECTION")
        calls = [c for c in gateway.calls if c["stage"].startswith("S10_CHAPTER_VISUAL_SELECTION_")]
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(calls[0]["evidence"]), 5)
        metrics = [m for m in result["trace"]["stage_metrics"] if m["stage"].startswith("S10_CHAPTER_VISUAL_SELECTION_")]
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["model_frame_count"], 5)
        self.assertEqual(metrics[0]["input_tokens"], 100)
        self.assertEqual(result["trace"]["model_calls"], sum(m["model_calls"] for m in result["trace"]["stage_metrics"]))

    def test_two_members_are_not_publishable_but_observations_remain_available(self):
        result = self.run_fixture(MediaGateway(storyline_groups=[[0, 1]]))
        self.assertEqual(result["chapters"], [])
        self.assertEqual(len(result["observations"]), 5)
        self.assertTrue(any("CHAPTER_DISPLAY_NEEDS_THREE_MATERIALS" in c["reason_codes"]
                            for c in result["decision_trace"]["chapter_candidates"]))

    def test_three_members_skip_extra_call_and_four_or_five_remain_allowed(self):
        exact = MediaGateway(storyline_groups=[[0, 1, 2]])
        result = self.run_fixture(exact)
        self.assertEqual(len(result["chapters"][0]["selected_media"]), 3)
        self.assertFalse(any(c["stage"].startswith("S10_") for c in exact.calls))
        for count in (4, 5):
            result = self.run_fixture(MediaGateway(display_count=count))
            self.assertEqual(len(result["chapters"][0]["selected_media"]), count)

    def test_visual_transport_failure_keeps_three_and_audits_failure_without_retry(self):
        gateway = MediaGateway(fail=True)
        result = self.run_fixture(gateway)
        self.assertEqual(len(result["chapters"][0]["selected_media"]), 3)
        selection = result["decision_trace"]["s10_chapter_media"][0]["display_selection"]
        self.assertEqual(selection["selection_source"], "QUALITY_ONLY_FALLBACK_NOT_DEDUP_VERIFIED")
        self.assertEqual(selection["fallback_reason"], "MODEL_HTTP_503")
        self.assertEqual(sum(c["stage"].startswith("S10_") for c in gateway.calls), 1)
        self.assertEqual(result["trace"]["model_call_failed_count"], 1)


if __name__ == "__main__":
    unittest.main()

import copy
import json
import unittest
import uuid
from dataclasses import replace
from pathlib import Path

from diary_one_ci import x02


FIXTURE = Path(__file__).parent / "fixtures" / "codex_v1_48_s04_overlong_real.json"


class RealS04FactRetentionTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.raw = copy.deepcopy(self.record["observation"])
        self.source_asset_id = self.raw["asset_id"]
        self.presented = set(self.raw["facts"][0]["evidence_frame_ids"])
        self.asset = {
            "asset_id": self.source_asset_id,
            "media_kind": "VIDEO",
        }
        self.stage_run = x02.StageRun(
            stage=self.record["source_stage"],
            output={"observations": [copy.deepcopy(self.raw)]},
            provider="archived-real-output",
            model="qwen3-vl-flash-2026-01-22",
            request_id="archived-no-call",
            input_tokens=0,
            output_tokens=0,
            latency_seconds=0,
            model_frame_count=len(self.presented),
            model_calls=0,
            pricing_currency="CNY",
            input_rate_per_million=0,
            output_rate_per_million=0,
            native_currency_per_usd=1,
            pricing_basis="archived-no-call",
            selected_evidence=tuple(
                {
                    "source_asset_id": self.source_asset_id,
                    "frame_id": frame_id,
                }
                for frame_id in self.presented
            ),
        )

    def test_v041_retains_exact_real_grounded_fact_that_exceeds_concise_target(self):
        observations, audit = x02._validate_perception_batch(
            uuid.uuid4(),
            [self.asset],
            self.stage_run,
            {self.source_asset_id: self.source_asset_id.removeprefix("asset_")},
            unicode_motifs=True,
            retain_extended_fact_text=True,
        )

        self.assertGreater(
            len(self.raw["facts"][0]["text"]),
            x02.PERCEPTION_FACT_CONCISE_TARGET_CHARS,
        )
        self.assertEqual(observations[0]["facts"][0]["text"], self.raw["facts"][0]["text"])
        self.assertEqual(observations[0]["status"], "OBSERVED")
        self.assertEqual(observations[0]["degraded_fields"], [])
        self.assertIn(
            "OVER_CONCISE_FACT_TEXT_RETAINED_WITHOUT_SEMANTIC_REWRITE",
            audit[0]["reason_codes"],
        )

    def test_historical_v03_fact_length_behavior_is_unchanged(self):
        observations, audit = x02._validate_perception_batch(
            uuid.uuid4(),
            [self.asset],
            self.stage_run,
            {self.source_asset_id: self.source_asset_id.removeprefix("asset_")},
            unicode_motifs=False,
            retain_extended_fact_text=False,
        )

        self.assertEqual(observations[0]["facts"], [])
        self.assertEqual(observations[0]["status"], "INSUFFICIENT_EVIDENCE")
        self.assertTrue(any(
            item["validation_rule_id"] == "X02V03_INVALID_FACT_DROPPED"
            for item in audit[0]["degraded_fields"]
        ))

    def test_v041_keeps_an_absolute_payload_limit(self):
        raw = copy.deepcopy(self.raw)
        raw["facts"][0]["text"] = "x" * (
            x02.PERCEPTION_FACT_PAYLOAD_MAX_CHARS + 1
        )
        run = replace(self.stage_run, output={"observations": [raw]})
        observations, audit = x02._validate_perception_batch(
            uuid.uuid4(),
            [self.asset],
            run,
            {self.source_asset_id: self.source_asset_id.removeprefix("asset_")},
            retain_extended_fact_text=True,
        )

        self.assertEqual(observations[0]["facts"], [])
        self.assertEqual(observations[0]["status"], "INSUFFICIENT_EVIDENCE")
        self.assertTrue(any(
            item["validation_rule_id"] == "X02V03_INVALID_FACT_DROPPED"
            for item in audit[0]["degraded_fields"]
        ))


if __name__ == "__main__":
    unittest.main()

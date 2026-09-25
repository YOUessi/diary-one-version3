"""Subject-policy wiring and real normalized-record replay, not model-quality tests."""
import copy
import json
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from diary_one_ci import x02
from test_codex_full_frame_bundle import make_x02_bundle_v04
from test_x02 import ScriptedGateway, make_x02_bundle_v02

RECORD = json.loads((Path(__file__).parent / "fixtures/codex_subject_codes_real_v1_61.json").read_text())


def projected_snapshot(observation):
    # The source is already-normalized output, not the unrecorded raw model reply.
    raw = {key: copy.deepcopy(observation[key]) for key in (
        "status", "setting_code", "activity_code", "episode_code", "subject_codes",
        "motifs", "event_kind", "event_salience", "quality_score", "limitations",
    )}
    raw["asset_id"] = observation["source_asset_id"]
    raw["facts"] = [{key: copy.deepcopy(fact[key]) for key in (
        "text", "evidence_frame_ids", "support_grade",
    )} for fact in observation["facts"]]
    return raw


def validate_snapshot(observation, raw, generic):
    return x02._validated_observation(
        uuid.UUID(RECORD["source_run_id"]),
        {"asset_id": observation["source_asset_id"], "media_kind": observation["media_kind"]},
        raw, observation["asset_id"], set(observation["evidence_frame_ids"]),
        unicode_motifs=True, retain_extended_fact_text=True, generic_animal_subjects=generic,
    )


class SchemaRecordingGateway(ScriptedGateway):
    def __init__(self):
        super().__init__()
        self.perception_schemas = []

    def call(self, stage, prompt, schema, evidence=(), context=None):
        if stage.startswith("S04_"):
            self.perception_schemas.append(copy.deepcopy(schema))
        return super().call(stage, prompt, schema, evidence=evidence, context=context)


class SubjectGranularityTests(unittest.TestCase):
    def test_schema_changes_only_subject_granularity_and_does_not_mutate_legacy(self):
        old = copy.deepcopy(x02.PERCEPTION_SCHEMA)
        new = copy.deepcopy(x02.PERCEPTION_SCHEMA_GENERIC_ANIMAL)
        def codes(schema):
            return schema["properties"]["observations"]["items"]["properties"]["subject_codes"]["items"]
        self.assertIn("CAT", codes(old)["enum"])
        self.assertIn("DOG", codes(old)["enum"])
        self.assertNotIn("ANIMAL", codes(old)["enum"])
        self.assertEqual(set(codes(new)["enum"]), (set(codes(old)["enum"]) - {"CAT", "DOG"}) | {"ANIMAL"})
        codes(new)["enum"] = codes(old)["enum"]
        self.assertEqual(new, old)

    def test_real_codes_are_dropped_without_changing_facts_or_inventing_animal(self):
        for snapshot in RECORD["snapshots"]:
            with self.subTest(file=snapshot["source_display_name"]):
                observation = snapshot["observation"]
                raw = projected_snapshot(observation)
                before = copy.deepcopy(raw)
                current, audit = validate_snapshot(observation, raw, True)
                self.assertEqual(raw, before)
                self.assertFalse(set(current["subject_codes"]) & {"CAT", "DOG", "ANIMAL"})
                self.assertEqual(current["subject_codes"], [code for code in raw["subject_codes"] if code not in {"CAT", "DOG"}])
                for actual, original in zip(current["facts"], raw["facts"]):
                    for key in ("text", "evidence_frame_ids", "support_grade"):
                        self.assertEqual(actual[key], original[key])
                self.assertEqual(len(current["facts"]), len(raw["facts"]))
                self.assertNotEqual(current["status"], "INSUFFICIENT_EVIDENCE")
                subject_drops = [entry for entry in audit if ".subject_codes[" in entry["json_field_path"]]
                self.assertEqual(len(subject_drops), len(set(raw["subject_codes"]) & {"CAT", "DOG"}))
                self.assertTrue(all(entry["action"] == "DROP_ONLY_INVALID_LIST_ENTRY" for entry in subject_drops))

    def test_recorded_canonical_vote_is_not_propagated_under_new_policy(self):
        groups = [RECORD["snapshots"][:2], RECORD["snapshots"][2:]]
        for snapshots, old_tag in zip(groups, ("CENTRAL_SUBJECT.CAT", "CENTRAL_SUBJECT.DOG")):
            observations = [item["observation"] for item in snapshots]
            before = copy.deepcopy(observations)
            self.assertIn(old_tag, x02._canonical_tags({}, observations))
            tags = x02._canonical_tags({}, observations, generic_animal_subjects=True)
            self.assertFalse(set(tags) & {"CENTRAL_SUBJECT.CAT", "CENTRAL_SUBJECT.DOG", "CENTRAL_SUBJECT.ANIMAL"})
            self.assertEqual(observations, before)

    def test_animal_enum_wiring_keeps_exact_recorded_text(self):
        observation = RECORD["snapshots"][0]["observation"]
        raw = projected_snapshot(observation)
        # Transport-field substitution only; this is NOT a new model inference.
        raw["subject_codes"] = ["ANIMAL"]
        current, audit = validate_snapshot(observation, raw, True)
        self.assertEqual(current["subject_codes"], ["ANIMAL"])
        self.assertFalse(audit)
        self.assertEqual(current["facts"][0]["text"], observation["facts"][0]["text"])
        old, _ = validate_snapshot(observation, raw, False)
        self.assertEqual(old["subject_codes"], [])
        _, failure = x02._failed_observation(
            uuid.UUID(RECORD["source_run_id"]), {"asset_id": observation["source_asset_id"], "media_kind": "PHOTO"},
            observation["asset_id"], "OBSERVATION_CONTRACT_INVALID", "transport test only",
            raw_candidate=raw, generic_animal_subjects=True,
        )
        self.assertEqual(failure["rejected_structured_candidate"]["raw_enum_fields"]["subject_codes"], ["ANIMAL"])

    def test_current_and_historical_pipeline_wiring_are_separate(self):
        with tempfile.TemporaryDirectory() as temporary:
            gateway = SchemaRecordingGateway()
            with patch.object(x02, "_public_chapters", wraps=x02._public_chapters) as chapters, patch.object(x02, "_public_ahas", wraps=x02._public_ahas) as ahas:
                result = x02.run_x02(make_x02_bundle_v04(Path(temporary)), gateway)
                self.assertTrue(chapters.call_args.kwargs["generic_animal_subjects"])
                self.assertTrue(ahas.call_args.kwargs["generic_animal_subjects"])
            self.assertTrue(gateway.perception_schemas)
            self.assertTrue(all(schema == x02.PERCEPTION_SCHEMA_GENERIC_ANIMAL for schema in gateway.perception_schemas))
            self.assertTrue(all("Subject granularity: use ANIMAL" in call["prompt"] for call in gateway.calls if call["stage"].startswith("S04_")))
            self.assertEqual(result["decision_trace"]["runtime_policies"]["subject_granularity"], x02.SUBJECT_GRANULARITY_VERSION)
        with tempfile.TemporaryDirectory() as temporary:
            gateway = SchemaRecordingGateway()
            result = x02.run_x02_v03(make_x02_bundle_v02(Path(temporary)), gateway)
            self.assertTrue(all(schema == x02.PERCEPTION_SCHEMA for schema in gateway.perception_schemas))
            self.assertTrue(all("Subject granularity: use ANIMAL" not in call["prompt"] for call in gateway.calls if call["stage"].startswith("S04_")))
            self.assertNotIn("runtime_policies", result["decision_trace"])

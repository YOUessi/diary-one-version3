import copy
import json
import re
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import diary_one_ci.x02 as x02_module

from diary_one_ci.bundle import (
    APP_LIBRARY_BUNDLE_VERSION,
    APP_LIBRARY_BUNDLE_VERSION_V02,
    APP_LIBRARY_BUNDLE_VERSION_V03,
    PHONE_TEST_EVIDENCE_PROFILE_V01,
)
from diary_one_ci.core import sha256_file
from diary_one_ci.x02 import (
    ACTIVITY_CODES,
    EPISODE_CODES,
    EVENT_KINDS,
    PERCEPTION_SCHEMA,
    QwenStageGateway,
    SETTING_CODES,
    StageModelGateway,
    StageRun,
    X02ContractError,
    X02ExecutionError,
    X02StageCallError,
    X02_FIELD_DEGRADATION_SHA256,
    X02_FIELD_DEGRADATION_VERSION,
    X02_OBSERVATION_COMPATIBILITY,
    X02_OBSERVATION_COMPATIBILITY_SHA256,
    X02_OBSERVATION_COMPATIBILITY_VERSION,
    X02_PIPELINE_VERSION,
    X02_SCHEMA_VERSION,
    X02_STORYLINE_CONTRACT_SHA256,
    X02_STORYLINE_CONTRACT_VERSION,
    X02_V03_PIPELINE_VERSION,
    X02_V03_SCHEMA_VERSION,
    _episode_compatibility,
    _perception_prompt,
    _validate_writer_output,
    _writer_prompt,
    _writer_retry_context,
    run_x02,
    run_x02_v03,
)
from diary_one_ci.x01 import QwenChatCompletionsAdapter, X01Error
from diary_one_ci.x01_server import (
    X02_FAILED_RUN_AUDIT_SCHEMA_VERSION,
    X02_RUN_AUDIT_SCHEMA_VERSION,
    X02_V03_FAILED_RUN_AUDIT_SCHEMA_VERSION,
    _write_x02_failed_run_audit,
    _write_x02_run_audit,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
X02_STORYLINE_V02_CONTRACT_PATH = (
    REPOSITORY_ROOT / "src" / "diary_one_ci" / "contracts" / "x02_storyline_v02.json"
)
X02_V041_PREVIEW_SCHEMA_PATH = (
    REPOSITORY_ROOT / "contracts" / "codex_x02_staged_preview_v04_1_media_v01.schema.json"
)


def assert_json_schema_instance(testcase, schema, instance):
    """Small dependency-free validator for the JSON Schema features used by X02."""

    def resolve(reference):
        testcase.assertTrue(reference.startswith("#/"), reference)
        value = schema
        for component in reference[2:].split("/"):
            value = value[component.replace("~1", "/").replace("~0", "~")]
        return value

    def matches_type(value, expected):
        return {
            "null": value is None,
            "boolean": isinstance(value, bool),
            "object": isinstance(value, dict),
            "array": isinstance(value, list),
            "string": isinstance(value, str),
            "integer": isinstance(value, int) and not isinstance(value, bool),
            "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        }[expected]

    def condition_matches(rule, value):
        if "const" in rule and value != rule["const"]:
            return False
        if "enum" in rule and value not in rule["enum"]:
            return False
        if isinstance(value, dict):
            if any(key not in value for key in rule.get("required", [])):
                return False
            for key, child_rule in rule.get("properties", {}).items():
                if key in value and not condition_matches(child_rule, value[key]):
                    return False
        return all(condition_matches(branch, value) for branch in rule.get("allOf", []))

    def validate(rule, value, path="$" ):
        if "$ref" in rule:
            validate(resolve(rule["$ref"]), value, path)
        for branch in rule.get("allOf", []):
            validate(branch, value, path)
        if "anyOf" in rule:
            matches = 0
            for branch in rule["anyOf"]:
                try:
                    validate(branch, value, path)
                except AssertionError:
                    continue
                matches += 1
            testcase.assertGreaterEqual(matches, 1, "%s does not match anyOf" % path)
        if "oneOf" in rule:
            matches = 0
            for branch in rule["oneOf"]:
                try:
                    validate(branch, value, path)
                except AssertionError:
                    continue
                matches += 1
            testcase.assertEqual(matches, 1, "%s does not match exactly one oneOf branch" % path)
        if "not" in rule:
            try:
                validate(rule["not"], value, path)
            except AssertionError:
                pass
            else:
                testcase.fail("%s matches forbidden schema" % path)
        if "if" in rule:
            conditional_branch = "then" if condition_matches(rule["if"], value) else "else"
            if conditional_branch in rule:
                validate(rule[conditional_branch], value, path)
        if "const" in rule:
            testcase.assertEqual(value, rule["const"], path)
        if "enum" in rule:
            testcase.assertIn(value, rule["enum"], path)
        expected_type = rule.get("type")
        if expected_type is not None:
            allowed_types = expected_type if isinstance(expected_type, list) else [expected_type]
            testcase.assertTrue(
                any(matches_type(value, item) for item in allowed_types),
                "%s has type %s, expected %s" % (path, type(value).__name__, allowed_types),
            )
        if isinstance(value, dict):
            required = rule.get("required", [])
            missing = [key for key in required if key not in value]
            testcase.assertEqual(missing, [], "%s missing required properties" % path)
            properties = rule.get("properties", {})
            if rule.get("additionalProperties") is False:
                extras = sorted(set(value) - set(properties))
                testcase.assertEqual(extras, [], "%s has unexpected properties" % path)
            for key, child_rule in properties.items():
                if key in value:
                    validate(child_rule, value[key], "%s.%s" % (path, key))
        if isinstance(value, list):
            if "minItems" in rule:
                testcase.assertGreaterEqual(len(value), rule["minItems"], path)
            if "maxItems" in rule:
                testcase.assertLessEqual(len(value), rule["maxItems"], path)
            if rule.get("uniqueItems"):
                canonical = [json.dumps(item, sort_keys=True) for item in value]
                testcase.assertEqual(len(canonical), len(set(canonical)), path)
            item_rule = rule.get("items")
            if isinstance(item_rule, dict):
                for index, child in enumerate(value):
                    validate(item_rule, child, "%s[%d]" % (path, index))
            if "contains" in rule:
                matching_items = 0
                for index, child in enumerate(value):
                    try:
                        validate(rule["contains"], child, "%s[%d]" % (path, index))
                    except AssertionError:
                        continue
                    matching_items += 1
                testcase.assertGreaterEqual(
                    matching_items,
                    rule.get("minContains", 1),
                    "%s contains too few matching items" % path,
                )
                if "maxContains" in rule:
                    testcase.assertLessEqual(
                        matching_items,
                        rule["maxContains"],
                        "%s contains too many matching items" % path,
                    )
        if isinstance(value, str):
            if "minLength" in rule:
                testcase.assertGreaterEqual(len(value), rule["minLength"], path)
            if "pattern" in rule:
                testcase.assertIsNotNone(re.search(rule["pattern"], value), path)
            if rule.get("format") == "uuid":
                try:
                    uuid.UUID(value)
                except ValueError:
                    testcase.fail("%s is not a UUID: %s" % (path, value))
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in rule:
                testcase.assertGreaterEqual(value, rule["minimum"], path)
            if "maximum" in rule:
                testcase.assertLessEqual(value, rule["maximum"], path)

    validate(schema, instance)


def assert_v041_cross_field_truth(testcase, instance):
    """Assert implementation invariants JSON Schema cannot express as value equality."""

    batching = instance["decision_trace"]["perception_batching"]
    testcase.assertEqual(instance["coverage_status"], batching["coverage_status"])
    testcase.assertEqual(
        instance["unresolved_asset_ids"],
        batching["unresolved_asset_ids"],
    )
    testcase.assertEqual(batching["max_assets"], 3)
    testcase.assertEqual(batching["max_frames"], 18)
    testcase.assertEqual(batching["max_evidence_bytes"], 4 * 1024 * 1024)
    testcase.assertEqual(batching["single_asset_retry_limit"], 1)

    outcomes = instance["selected_memory_outcomes"]
    outcome_ids = [item["memory_id"] for item in outcomes]
    testcase.assertEqual(len(outcome_ids), len(set(outcome_ids)))
    published_by_type = {
        "CHAPTER": {item["id"] for item in instance["chapters"]},
        "AHA": {item["id"] for item in instance["ahas"]},
    }
    publishable_outcome_by_type = {
        memory_type: {
            item["memory_id"]
            for item in outcomes
            if item["memory_type"] == memory_type
            and item["media_state"] == "S10_MEDIA_READY"
            and item["surface_state"] in {
                "MODEL_SURFACE_VERIFIED",
                "DETERMINISTIC_FALLBACK_VERIFIED",
            }
        }
        for memory_type in ("CHAPTER", "AHA")
    }
    testcase.assertEqual(published_by_type, publishable_outcome_by_type)

    if instance["coverage_status"] == "PARTIAL_UNRESOLVED":
        expected_semantic_state = "UNRESOLVED_DAY"
    elif any(item["memory_type"] == "CHAPTER" for item in outcomes):
        expected_semantic_state = "CHAPTER_DAY"
    elif any(item["memory_type"] == "AHA" for item in outcomes):
        expected_semantic_state = "HIGHLIGHT_DAY"
    else:
        expected_semantic_state = "EMPTY_DAY"
    testcase.assertEqual(instance["semantic_day_state"], expected_semantic_state)
    if instance["semantic_day_state"] == "HIGHLIGHT_DAY":
        testcase.assertEqual(
            [item["memory_type"] for item in outcomes],
            ["AHA"],
        )

    visible = [item for item in outcomes if item["visibility_state"] == "VISIBLE_PREVIEW"]
    if instance["coverage_status"] == "PARTIAL_UNRESOLVED":
        expected_delivery_state = "PIPELINE_BLOCKED"
    elif not outcomes:
        expected_delivery_state = "NO_GROUNDED_MEMORY"
    elif len(visible) < len(outcomes):
        expected_delivery_state = "READY_WITH_ITEM_BLOCKS" if visible else "PIPELINE_BLOCKED"
    elif any(
        item["surface_state"] == "DETERMINISTIC_FALLBACK_VERIFIED"
        for item in outcomes
    ):
        expected_delivery_state = "READY_WITH_GROUNDED_COPY_FALLBACK"
    else:
        expected_delivery_state = "READY_PRIMARY_COPY"
    testcase.assertEqual(instance["delivery_state"], expected_delivery_state)
    testcase.assertEqual(
        instance["output_mode"],
        "PIPELINE_BLOCKED"
        if expected_delivery_state == "PIPELINE_BLOCKED"
        else expected_semantic_state,
    )


def make_x02_bundle(root: Path, count: int, media_kind: str = "VIDEO") -> Path:
    session_id = "195d9278-0247-4ac0-bd3c-3acecda5af97"
    namespace = uuid.UUID(session_id)
    assets = []
    for index in range(count):
        asset_uuid = uuid.uuid5(namespace, "x02-asset:%d" % index)
        asset_id = "asset_" + str(asset_uuid)
        frames = []
        for offset_index, offset in enumerate((1500, 4500, 7500)):
            relative = Path("evidence") / asset_id / ("frame_%d.jpg" % offset)
            frame_path = root / relative
            frame_path.parent.mkdir(parents=True, exist_ok=True)
            frame_path.write_bytes(("x02-jpeg-%d-%d" % (index, offset)).encode())
            frames.append({
                "frame_id": "frame_%s_%d" % (asset_uuid, offset),
                "canonical_offset_ms": offset,
                "source_timestamp_ms": None if media_kind == "PHOTO" else (offset_index + 1) * 500,
                "relative_path": str(relative),
                "sha256": sha256_file(frame_path),
                "width": 768,
                "height": 1024,
                "spatial_transform": "CENTER_CROP_ASPECT_FILL",
            })
        assets.append({
            "asset_id": asset_id,
            "media_kind": media_kind,
            "media_source": "PHOTO_LIBRARY_TEST",
            "original_file_extension": "jpg" if media_kind == "PHOTO" else "mov",
            "original_sha256": "%064x" % (index + 1),
            "original_bytes": 1_000 + index,
            "original_width": 1_920,
            "original_height": 1_080,
            "original_duration_ms": None if media_kind == "PHOTO" else 2_300,
            "capture_time": None,
            "original_included": False,
            "timeline_offset_ms": index * 120_000,
            "logical_asset_duration_ms": 9_000,
            "materialized_video": False,
            "frames": frames,
        })
    manifest = {
        "bundle_version": APP_LIBRARY_BUNDLE_VERSION,
        "research_only": True,
        "session": {
            "session_id": session_id,
            "exported_at": "2026-08-31T12:00:00Z",
            "timezone": "Asia/Shanghai",
        },
        "device": {
            "device_id": "pseudo",
            "hardware_revision": "test",
            "firmware_version": "test",
            "sdk_version": "test",
        },
        "normalization": {
            "width": 768,
            "height": 1024,
            "orientation": "PORTRAIT",
            "aspect_ratio": "3:4",
            "spatial_transform": "CENTER_CROP_ASPECT_FILL",
            "temporal_transform": "NORMALIZED_FRACTIONS_TO_CANONICAL_9S",
            "canonical_frame_offsets_ms": [1500, 4500, 7500],
        },
        "assets": assets,
    }
    path = root / "bundle.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def make_x02_bundle_v02(root: Path) -> Path:
    session_id = "42cd74ac-979f-4b38-9643-8f4b5a6872db"
    namespace = uuid.UUID(session_id)
    specs = [
        ("PHOTO", None, 1, [4_500]),
        ("VIDEO", 9_000, 1, [1_500, 4_500, 7_500]),
        ("VIDEO", 16_000, 2, [1_500, 7_500] * 2),
        ("VIDEO", 73_000, 4, [1_500, 7_500] * 4),
        ("VIDEO", 120_000, 6, [1_500, 7_500] * 6),
    ]
    assets = []
    for index, (kind, duration_ms, window_count, offsets) in enumerate(specs):
        asset_uuid = uuid.uuid5(namespace, "x02-v02-asset:%d" % index)
        asset_id = "asset_" + str(asset_uuid)
        frames = []
        for frame_index, offset in enumerate(offsets):
            window_index = 0 if kind == "PHOTO" or window_count == 1 else frame_index // 2
            if kind == "PHOTO":
                timestamp = None
                sample_role = "PHOTO_REPRESENTATIVE"
            else:
                fraction = (frame_index + 1) / (len(offsets) + 1)
                timestamp = max(0, min(duration_ms - 1, round(duration_ms * fraction)))
                sample_role = (
                    "WINDOW_MIDDLE" if offset == 4_500
                    else "WINDOW_EARLY" if offset == 1_500 else "WINDOW_LATE"
                )
            relative = Path("evidence") / asset_id / ("frame_%02d.jpg" % frame_index)
            frame_path = root / relative
            frame_path.parent.mkdir(parents=True, exist_ok=True)
            frame_path.write_bytes(("x02-v02-jpeg-%d-%d" % (index, frame_index)).encode())
            frames.append({
                "frame_id": "frame_%s_%02d" % (asset_uuid, frame_index),
                "window_index": window_index,
                "window_count": window_count,
                "sample_role": sample_role,
                "canonical_offset_ms": offset,
                "source_timestamp_ms": timestamp,
                "relative_path": str(relative),
                "sha256": sha256_file(frame_path),
                "width": 768,
                "height": 1024,
                "spatial_transform": "CENTER_CROP_ASPECT_FILL",
            })
        assets.append({
            "asset_id": asset_id,
            "media_kind": kind,
            "media_source": "PHONE_LIBRARY_DAY_TEST",
            "original_file_extension": "jpg" if kind == "PHOTO" else "mp4",
            "original_sha256": "%064x" % (index + 101),
            "original_bytes": 10_000 + index,
            "original_width": 1_920,
            "original_height": 1_080,
            "original_duration_ms": duration_ms,
            "original_included": False,
            "timeline_offset_ms": index * 120_000,
            "logical_asset_duration_ms": 9_000,
            "materialized_video": False,
            "evidence_sampling_profile": (
                "PHOTO_SINGLE_FRAME" if kind == "PHOTO"
                else "VIDEO_SINGLE_WINDOW_THREE" if window_count == 1
                else "VIDEO_MULTI_WINDOW_TWO_PER_WINDOW"
            ),
            "evidence_window_count": window_count,
            "frames": frames,
        })
    manifest = {
        "bundle_version": APP_LIBRARY_BUNDLE_VERSION_V02,
        "research_only": True,
        "session": {
            "session_id": session_id,
            "exported_at": "2026-09-02T09:00:00Z",
            "timezone": "TEST_DAY_NO_TIMEZONE",
        },
        "device": {
            "device_id": "web-test",
            "hardware_revision": "PHONE_LIBRARY_TEST",
            "firmware_version": "NOT_APPLICABLE",
            "sdk_version": "WEB_EVIDENCE_V02",
        },
        "normalization": {
            "width": 768,
            "height": 1024,
            "orientation": "PORTRAIT",
            "aspect_ratio": "3:4",
            "spatial_transform": "CENTER_CROP_ASPECT_FILL",
            "temporal_transform": PHONE_TEST_EVIDENCE_PROFILE_V01,
            "canonical_frame_offsets_ms": [1_500, 4_500, 7_500],
            "evidence_profile_version": PHONE_TEST_EVIDENCE_PROFILE_V01,
        },
        "assets": assets,
    }
    path = root / "bundle.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def make_x02_bundle_v03(root: Path) -> Path:
    path = make_x02_bundle_v02(root)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["bundle_version"] = APP_LIBRARY_BUNDLE_VERSION_V03
    manifest["device"]["sdk_version"] = "WEB_EVIDENCE_V03"
    for index, asset in enumerate(manifest["assets"]):
        asset.pop("timeline_offset_ms")
        asset["sequence_index"] = index
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


class ScriptedGateway(StageModelGateway):
    provider = "test"
    model = "scripted-stages"

    def __init__(
        self,
        semantic_plan=None,
        storyline_groups=None,
        fail_first_writer=False,
        fail_all_writer=False,
        fail_aha_writer_attempts=0,
        observation_overrides=None,
    ):
        self.semantic_plan = semantic_plan or {}
        self.storyline_groups = storyline_groups
        self.fail_first_writer = fail_first_writer
        self.fail_all_writer = fail_all_writer
        self.fail_aha_writer_attempts = fail_aha_writer_attempts
        self.observation_overrides = observation_overrides or {}
        self.calls = []
        self.writer_calls = 0

    @property
    def ready(self):
        return True

    def call(self, stage, prompt, schema, evidence=(), context=None):
        context = context or {}
        self.calls.append({
            "stage": stage,
            "evidence": list(evidence),
            "prompt": prompt,
            "context": context,
        })
        if stage.startswith("S04_PERCEPTION"):
            output = self._perception(context)
        elif stage == "S05_S07_STRUCTURE_PROPOSAL":
            output = self._structure(context)
        elif stage.startswith("S10_CHAPTER_VISUAL_SELECTION_"):
            output = {
                "ranked_observation_ids": [item["observation_id"] for item in context["members"]],
                "display_count": min(5, len(context["members"])),
                "reason": "Interface fixture; not a visual-quality judgement.",
            }
        elif stage.startswith("S11_WRITER"):
            self.writer_calls += 1
            output = self._writer(context)
        else:
            output = {}
        return StageRun(
            stage=stage,
            output=output,
            provider=self.provider,
            model=self.model,
            request_id="request-%d" % len(self.calls),
            input_tokens=100,
            output_tokens=50,
            latency_seconds=0.01,
            model_frame_count=len(evidence),
            model_calls=1,
            pricing_currency="USD",
            input_rate_per_million=1.0,
            output_rate_per_million=2.0,
            native_currency_per_usd=1.0,
            pricing_basis="test",
            selected_evidence=tuple({
                "selection_order": order,
                "source_asset_id": asset["asset_id"],
                "asset_id": str(asset["asset_id"]).removeprefix("asset_"),
                "frame_id": frame["frame_id"],
                "media_kind": asset["media_kind"],
                "canonical_offset_ms": frame["canonical_offset_ms"],
                "reason_code": "TEST_PRESENTED",
            } for order, (asset, frame, _) in enumerate(evidence)),
        )

    def _perception(self, context):
        frames_by_asset = {}
        for asset, frame, _ in context["evidence"]:
            frames_by_asset.setdefault(asset["asset_id"], []).append(frame["frame_id"])
        observations = []
        for asset in context["assets"]:
            index = (
                int(asset["sequence_index"])
                if "sequence_index" in asset
                else int(asset["timeline_offset_ms"]) // 120_000
            )
            episode = self.semantic_plan.get(index, "HISTORIC_TOWN_WALK")
            mapping = {
                "HISTORIC_TOWN_WALK": ("HISTORIC_STREET", "WALKING", ["HISTORIC_ARCHITECTURE"], ["historic_lane"]),
                "NATURE_WALK": ("NATURE_TRAIL", "WALKING", ["LANDSCAPE"], ["forest_path"]),
                "MARKET_VISIT": ("COMMERCIAL_MARKET", "BROWSING", ["STREET_SCENE"], ["market_stall"]),
                "CAFE_STOP": ("CAFE_TEA_SHOP", "EATING_DRINKING", ["FOOD_DESSERT"], ["dessert"]),
                "HOME_LIFE": ("HOME", "OTHER", ["OTHER"], ["home_life"]),
                "URBAN_WALK": ("URBAN_STREET", "WALKING", ["STREET_SCENE"], ["urban_street"]),
                "TRANSIT": ("TRANSIT", "TRANSIT", ["OTHER"], ["transit"]),
                "CRAFT_SESSION": ("HOME", "CRAFT", ["CRAFT_OBJECT"], ["craft_object"]),
                "BIRTHDAY_GATHERING": ("HOME", "GATHERING", ["PEOPLE", "FOOD_DESSERT"], ["birthday"]),
            }
            setting, activity, subjects, motifs = mapping[episode]
            event_kind = "FOOD_MOMENT" if episode == "CAFE_STOP" else "NONE"
            if episode == "BIRTHDAY_GATHERING":
                event_kind = "CEREMONY"
            event_salience = "HIGH" if event_kind != "NONE" else "NONE"
            override = self.observation_overrides.get(index, {})
            setting = override.get("setting_code", setting)
            activity = override.get("activity_code", activity)
            episode = override.get("episode_code", episode)
            subjects = override.get("subject_codes", subjects)
            motifs = override.get("motifs", motifs)
            event_kind = override.get("event_kind", event_kind)
            event_salience = override.get(
                "event_salience",
                "HIGH" if event_kind != "NONE" else "NONE",
            )
            observations.append({
                "asset_id": asset["asset_id"],
                "status": "OBSERVED",
                "facts": [{
                    "text": override.get(
                        "fact_text",
                        "第%d项可见%s。" % (index + 1, episode.lower()),
                    ),
                    "evidence_frame_ids": frames_by_asset[asset["asset_id"]],
                    "support_grade": override.get("support_grade", "STRONG"),
                }],
                "setting_code": setting,
                "activity_code": activity,
                "episode_code": episode,
                "subject_codes": subjects,
                "motifs": motifs,
                "event_kind": event_kind,
                "event_salience": event_salience,
                "quality_score": override.get(
                    "quality_score",
                    0.7 + ((index % 3) * 0.05),
                ),
                "limitations": [],
            })
        return {"observations": observations}

    def _structure(self, context):
        if "storyline_contract_version" not in context:
            return {"chapter_proposals": [], "aha_proposals": []}
        # Prescribed member IDs only. This stub does not judge scene semantics.
        observations = {item["sequence_index"]: item for item in context["observations"]}
        keep_indices = [
            index for index, item in observations.items() if item["role"] == "KEEP"
        ]
        groups = self.storyline_groups
        if groups is None:
            groups = [keep_indices[:12]] if len(keep_indices) >= 3 else []
        proposals = []
        for group_index, indices in enumerate(groups):
            members = [observations[index] for index in indices]
            proposals.append({
                "key": "scripted_group_%02d" % group_index,
                "storyline_basis": "ACTIVITY_THREAD",
                "thesis": "Integration fixture; not semantic-quality evidence.",
                "observation_ids": [item["observation_id"] for item in members],
                "fact_ids": [fact["fact_id"] for item in members for fact in item["facts"]],
                "beat_map": [{
                    "observation_id": item["observation_id"],
                    "beat_role": "PROGRESSION",
                    "fact_ids": [fact["fact_id"] for fact in item["facts"]],
                    "contribution": "Prescribed member reference.",
                } for item in members],
                "reason": "Prescribed grouping for pipeline integration only.",
            })
        return {"storyline_proposals": proposals, "aha_proposals": []}

    def _writer(self, context):
        chapters = []
        ahas = []
        for memory in context["memories"]:
            claim_ids = [fact["fact_id"] for fact in memory["facts"]]
            if memory["memory_type"] == "CHAPTER":
                source_preserving = (
                    context.get("writer_grounding_policy")
                    == "V04_1_SOURCE_PRESERVING_FACT_SURFACE"
                )
                text = (
                    memory["facts"][0]["text"]
                    if source_preserving else
                    "沿着街巷慢慢走，眼前的景致一路展开。"
                )
                if self.fail_all_writer or (
                    self.fail_first_writer and self.writer_calls == 1 and not chapters
                ):
                    text = "先写第一句。接着写第二句。最后又写了第三句。"
                chapters.append({
                    "candidate_id": memory["candidate_id"],
                    "title": (
                        memory["deterministic_allowed_title"]
                        if source_preserving else "沿路所见"
                    ),
                    "text": text,
                    "claim_ids": claim_ids[:1] if source_preserving else claim_ids[:3],
                })
            else:
                source_preserving = (
                    context.get("writer_grounding_policy")
                    == "V04_1_SOURCE_PRESERVING_FACT_SURFACE"
                )
                text = (
                    memory["facts"][0]["text"]
                    if source_preserving else "甜点端到了眼前。"
                )
                if self.writer_calls <= self.fail_aha_writer_attempts:
                    text = "甜点终于端到了眼前，这句话故意写得明显超过二十个可见字符。"
                ahas.append({
                    "candidate_id": memory["candidate_id"],
                    "title": (
                        memory["deterministic_allowed_title"]
                        if source_preserving else "甜点片刻"
                    ),
                    "text": text,
                    "claim_ids": claim_ids[:1],
                })
        return {"chapters": chapters, "ahas": ahas}


class MissingAhaReferenceGateway(ScriptedGateway):
    """Interface failure injection; does not use long prose as a semantic failure."""

    def _writer(self, context):
        output = super()._writer(context)
        for item in output["ahas"]:
            item.pop("claim_ids")
        return output


class PerceptionFailureGateway(ScriptedGateway):
    """Raises billable S04 call errors while leaving all later stages scripted."""

    def __init__(self, *, fail_multi_asset=True, permanently_failed_indices=()):
        super().__init__()
        self.fail_multi_asset = fail_multi_asset
        self.permanently_failed_indices = set(permanently_failed_indices)
        self.perception_attempts = []
        self.failed_stage_runs = []

    def call(self, stage, prompt, schema, evidence=(), context=None):
        context = context or {}
        if stage.startswith("S04_PERCEPTION"):
            assets = list(context.get("assets", []))
            indices = tuple(
                int(asset["timeline_offset_ms"]) // 120_000 for asset in assets
            )
            should_fail = (
                self.fail_multi_asset and len(assets) > 1
            ) or (
                len(assets) == 1 and indices[0] in self.permanently_failed_indices
            )
            self.perception_attempts.append({
                "stage": stage,
                "indices": indices,
                "status": "FAILED" if should_fail else "VALIDATED",
            })
            if should_fail:
                failed = StageRun(
                    stage=stage,
                    output={},
                    provider=self.provider,
                    model=self.model,
                    request_id="failed-%s" % stage.lower(),
                    input_tokens=701,
                    output_tokens=29,
                    latency_seconds=0.02,
                    model_frame_count=len(evidence),
                    model_calls=1,
                    pricing_currency="USD",
                    input_rate_per_million=2.0,
                    output_rate_per_million=3.0,
                    native_currency_per_usd=1.0,
                    pricing_basis="test-failed-call",
                    selected_evidence=(),
                    call_status="HTTP_FAILED",
                )
                self.failed_stage_runs.append(failed)
                raise X02StageCallError(
                    "%s rejected the perception request envelope" % stage,
                    stage_run=failed,
                    code="PERCEPTION_ASSET_LOCAL_CONTRACT_INVALID",
                )
        return super().call(stage, prompt, schema, evidence=evidence, context=context)


class PerceptionCodeFailureGateway(ScriptedGateway):
    """Fails every S04 provider attempt with one explicit gateway code."""

    def __init__(self, code):
        super().__init__()
        self.code = code
        self.perception_attempts = []

    def call(self, stage, prompt, schema, evidence=(), context=None):
        context = context or {}
        if stage.startswith("S04_PERCEPTION"):
            assets = list(context.get("assets", []))
            self.perception_attempts.append(tuple(
                int(asset["timeline_offset_ms"]) // 120_000 for asset in assets
            ))
            failed = StageRun(
                stage=stage,
                output={"failure": "TEST"},
                provider=self.provider,
                model=self.model,
                request_id="failed-%03d" % len(self.perception_attempts),
                input_tokens=0,
                output_tokens=0,
                latency_seconds=0.001,
                model_frame_count=len(evidence),
                model_calls=1,
                pricing_currency="USD",
                input_rate_per_million=0.0,
                output_rate_per_million=0.0,
                native_currency_per_usd=1.0,
                pricing_basis="test",
                selected_evidence=(),
                call_status=(
                    "FAILED_BEFORE_RESPONSE"
                    if self.code.startswith("MODEL_TRANSPORT_") else "HTTP_FAILED"
                ),
            )
            raise X02StageCallError(
                "test perception failure",
                stage_run=failed,
                code=self.code,
            )
        return super().call(stage, prompt, schema, evidence=evidence, context=context)


class X02Tests(unittest.TestCase):
    def test_v02_compatibility_source_covers_every_specific_episode_with_positive_and_negative_cases(self):
        rules = X02_OBSERVATION_COMPATIBILITY["episode_rules"]
        self.assertEqual(
            {rule["episode_code"] for rule in rules},
            set(EPISODE_CODES) - {"OTHER", "UNKNOWN"},
        )
        for rule in rules:
            episode_code = rule["episode_code"]
            for clause in rule["clauses"]:
                setting = clause.get("setting_codes", [sorted(SETTING_CODES)[0]])[0]
                activity = clause.get("activity_codes", [sorted(ACTIVITY_CODES)[0]])[0]
                event_kind = clause.get("event_kinds", ["NONE"])[0]
                compatible, rule_id = _episode_compatibility(
                    setting,
                    activity,
                    episode_code,
                    event_kind,
                )
                self.assertTrue(compatible, (rule_id, setting, activity, episode_code, event_kind))
                self.assertEqual(rule_id, rule["rule_id"])
            negative = next(
                (
                    (setting, activity, event_kind)
                    for setting in sorted(SETTING_CODES)
                    for activity in sorted(ACTIVITY_CODES)
                    for event_kind in sorted(EVENT_KINDS)
                    if not _episode_compatibility(
                        setting,
                        activity,
                        episode_code,
                        event_kind,
                    )[0]
                ),
                None,
            )
            self.assertIsNotNone(negative, episode_code)
        self.assertTrue(_episode_compatibility("HOME", "CRAFT", "OTHER", "NONE")[0])
        self.assertTrue(_episode_compatibility("HOME", "CRAFT", "UNKNOWN", "NONE")[0])

    def test_craft_is_many_to_many_and_event_shaped_episode_requires_visible_event(self):
        for setting in ("HOME", "WORKPLACE", "INDOOR_PUBLIC"):
            self.assertTrue(
                _episode_compatibility(setting, "CRAFT", "CRAFT_SESSION", "NONE")[0]
            )
        self.assertFalse(
            _episode_compatibility(
                "HOME",
                "GATHERING",
                "BIRTHDAY_GATHERING",
                "NONE",
            )[0]
        )
        self.assertTrue(
            _episode_compatibility(
                "HOME",
                "GATHERING",
                "BIRTHDAY_GATHERING",
                "CEREMONY",
            )[0]
        )

    def test_perception_prompt_is_generated_from_the_versioned_compatibility_source(self):
        prompt = _perception_prompt([], [])
        self.assertIn(X02_OBSERVATION_COMPATIBILITY_VERSION, prompt)
        self.assertIn(X02_OBSERVATION_COMPATIBILITY_SHA256, prompt)
        for rule in X02_OBSERVATION_COMPATIBILITY["episode_rules"]:
            self.assertIn(rule["rule_id"], prompt)

    def test_contradictory_tuple_degrades_without_leaking_free_form_content(self):
        private_text = "PRIVATE FREE FORM FACT TEXT MUST NOT ENTER THE REJECTION SNAPSHOT"
        gateway = ScriptedGateway(
            observation_overrides={
                0: {
                    "setting_code": "HOME",
                    "activity_code": "WALKING",
                    "episode_code": "CRAFT_SESSION",
                    "fact_text": private_text,
                    "motifs": ["PRIVATE_MOTIF"],
                }
            }
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = make_x02_bundle(root / "bundle", 6)
            result = run_x02(manifest_path, gateway)
            ledger = result["decision_trace"]["observation_candidates"]
            degraded = next(
                item for item in ledger
                if item["validation_status"] == "PASSED_WITH_FIELD_DEGRADATION"
            )
            self.assertEqual(len(degraded["canonical_candidate_sha256"]), 64)
            self.assertEqual(
                degraded["degraded_fields"],
                [{
                    "json_field_path": "$.observations[*].episode_code",
                    "validation_rule_id": "X02V02_EPISODE_CRAFT_SESSION",
                    "action": "USE_UNKNOWN_WITHOUT_INFERRING_REPLACEMENT_EPISODE",
                    "original_value_sentinel": "<CONTRADICTORY_CLOSED_VOCABULARY_TUPLE>",
                }],
            )
            serialized_degradation = json.dumps(degraded, sort_keys=True)
            self.assertNotIn(private_text, serialized_degradation)
            self.assertNotIn("PRIVATE_MOTIF", serialized_degradation)
            self.assertNotIn('"facts"', serialized_degradation)
            self.assertNotIn('"motifs"', serialized_degradation)
            observation = result["observations"][0]
            self.assertEqual(observation["status"], "PARTIAL")
            self.assertEqual(observation["episode_code"], "UNKNOWN")
            self.assertEqual(observation["facts"][0]["text"], private_text)
            self.assertEqual(result["decision_trace"]["counts"]["accepted_observation_count"], 6)
            self.assertEqual(result["decision_trace"]["counts"]["field_degraded_observation_count"], 1)
            self.assertEqual(len(result["chapters"]), 1)
            self.assertEqual(result["schema_version"], X02_SCHEMA_VERSION)
            self.assertEqual(
                result["observation_semantic_contract_version"],
                X02_OBSERVATION_COMPATIBILITY_VERSION,
            )
            self.assertEqual(
                result["observation_semantic_contract_sha256"],
                X02_OBSERVATION_COMPATIBILITY_SHA256,
            )
            self.assertEqual(
                result["field_degradation_contract_version"],
                X02_FIELD_DEGRADATION_VERSION,
            )
            self.assertEqual(
                result["field_degradation_contract_sha256"],
                X02_FIELD_DEGRADATION_SHA256,
            )
            self.assertEqual(
                result["storyline_contract_version"],
                X02_STORYLINE_CONTRACT_VERSION,
            )
            self.assertEqual(
                result["storyline_contract_sha256"],
                X02_STORYLINE_CONTRACT_SHA256,
            )

            audit_path = _write_x02_run_audit(
                root / "audits",
                json.loads(manifest_path.read_text()),
                result,
                1.0,
                2.0,
                4_096,
            )
            audit = json.loads(audit_path.read_text())
            self.assertEqual(audit["schema_version"], X02_RUN_AUDIT_SCHEMA_VERSION)
            self.assertNotIn(private_text, json.dumps(audit["result"]["decision_trace"]))

    def test_twenty_videos_receive_three_frames_each_without_order_starvation(self):
        with tempfile.TemporaryDirectory() as temporary:
            gateway = ScriptedGateway()
            result = run_x02(make_x02_bundle(Path(temporary), 20), gateway)
            selected = result["decision_trace"]["evidence_selection"]["selected"]
            counts = {}
            for item in selected:
                counts[item["source_asset_id"]] = counts.get(item["source_asset_id"], 0) + 1
            self.assertEqual(len(counts), 20)
            self.assertEqual(set(counts.values()), {3})
            self.assertEqual(result["trace"]["evidence_frame_count"], 60)
            self.assertEqual(
                [item["selection_order"] for item in selected],
                list(range(60)),
            )
            model_presentations = [
                (asset["asset_id"], frame["frame_id"])
                for call in gateway.calls if call["stage"].startswith("S04_")
                for asset, frame, _ in call["evidence"]
            ]
            self.assertEqual(
                [(item["source_asset_id"], item["frame_id"]) for item in selected],
                model_presentations,
            )
            self.assertEqual(
                [len(call["evidence"]) for call in gateway.calls if call["stage"].startswith("S04_")],
                [9, 9, 9, 9, 9, 9, 6],
            )
            batching = result["decision_trace"]["perception_batching"]
            self.assertEqual(batching["max_assets"], 3)
            self.assertEqual(batching["max_frames"], 18)
            self.assertEqual(batching["planned_batch_count"], 7)
            self.assertEqual(batching["coverage_status"], "COMPLETE")

    def test_six_photos_use_dense_middle_frame_selection_order(self):
        with tempfile.TemporaryDirectory() as temporary:
            gateway = ScriptedGateway()
            result = run_x02(
                make_x02_bundle(Path(temporary), 6, media_kind="PHOTO"),
                gateway,
            )
            selected = result["decision_trace"]["evidence_selection"]["selected"]
            self.assertEqual(len(selected), 6)
            self.assertEqual(
                [item["selection_order"] for item in selected],
                list(range(6)),
            )
            self.assertEqual(
                [item["canonical_offset_ms"] for item in selected],
                [4500] * 6,
            )
            self.assertEqual(
                [item["frame_id"] for item in selected],
                [
                    frame["frame_id"]
                    for call in gateway.calls if call["stage"].startswith("S04_")
                    for _, frame, _ in call["evidence"]
                ],
            )

    def test_v02_phone_test_bundle_uses_one_three_four_eight_and_twelve_frames(self):
        with tempfile.TemporaryDirectory() as temporary:
            gateway = ScriptedGateway()
            result = run_x02(make_x02_bundle_v02(Path(temporary)), gateway)
            selected = result["decision_trace"]["evidence_selection"]["selected"]
            counts = {}
            windows = {}
            for item in selected:
                counts[item["source_asset_id"]] = counts.get(item["source_asset_id"], 0) + 1
                windows[item["source_asset_id"]] = item["window_count"]
            self.assertEqual(list(counts.values()), [1, 3, 4, 8, 12])
            self.assertEqual(list(windows.values()), [1, 1, 2, 4, 6])
            self.assertEqual(result["trace"]["evidence_frame_count"], 28)
            self.assertEqual(result["trace"]["input_bundle_version"], APP_LIBRARY_BUNDLE_VERSION_V02)
            self.assertEqual(
                result["trace"]["evidence_profile_version"],
                PHONE_TEST_EVIDENCE_PROFILE_V01,
            )
            self.assertEqual(result["evaluation_run_mode"], "FRESH_FULL_RUN")
            self.assertFalse(result["cross_run_semantic_cache_used"])
            self.assertFalse(result["trace"]["cross_run_semantic_cache_used"])

    def test_v03_phone_test_bundle_uses_duration_windows_and_sequence_order(self):
        with tempfile.TemporaryDirectory() as temporary:
            gateway = ScriptedGateway()
            result = run_x02(make_x02_bundle_v03(Path(temporary)), gateway)
            selected = result["decision_trace"]["evidence_selection"]["selected"]
            counts = {}
            for item in selected:
                counts[item["source_asset_id"]] = counts.get(item["source_asset_id"], 0) + 1
            self.assertEqual(list(counts.values()), [1, 3, 4, 8, 12])
            self.assertEqual(result["trace"]["evidence_frame_count"], 28)
            self.assertEqual(
                result["trace"]["input_bundle_version"],
                APP_LIBRARY_BUNDLE_VERSION_V03,
            )
            self.assertEqual(
                result["trace"]["evidence_profile_version"],
                PHONE_TEST_EVIDENCE_PROFILE_V01,
            )
            self.assertEqual(
                result["decision_trace"]["evidence_selection"]["strategy"],
                "PHOTO_ONE_FRAME_VIDEO_DURATION_AWARE_WINDOWS_IN_BOUNDED_DYNAMIC_BATCHES",
            )
            schema = json.loads(
                X02_V041_PREVIEW_SCHEMA_PATH.read_text(encoding="utf-8")
            )
            assert_json_schema_instance(self, schema, result)

    def test_historical_x02_v03_rejects_bundle_v03_without_changing_v02(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(
                X02ContractError,
                "historical X02 V03 accepts App Library Bundle V01/V02 only",
            ):
                run_x02_v03(
                    make_x02_bundle_v03(Path(temporary)),
                    ScriptedGateway(),
                )
        with tempfile.TemporaryDirectory() as temporary:
            historical = run_x02_v03(
                make_x02_bundle_v02(Path(temporary)),
                ScriptedGateway(),
            )
            self.assertEqual(historical["schema_version"], X02_V03_SCHEMA_VERSION)
            self.assertEqual(
                historical["trace"]["input_bundle_version"],
                APP_LIBRARY_BUNDLE_VERSION_V02,
            )

    def test_invalid_subject_code_is_dropped_without_deleting_grounded_observation(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = run_x02(
                make_x02_bundle(Path(temporary), 3),
                ScriptedGateway(observation_overrides={
                    0: {"subject_codes": ["HISTORIC_ARCHITECTURE", "CROWD"]},
                }),
            )
            observation = result["observations"][0]
            self.assertEqual(observation["status"], "PARTIAL")
            self.assertEqual(observation["subject_codes"], ["HISTORIC_ARCHITECTURE"])
            self.assertTrue(observation["facts"])
            audit = result["decision_trace"]["observation_candidates"][0]
            self.assertEqual(audit["validation_status"], "PASSED_WITH_FIELD_DEGRADATION")
            self.assertEqual(
                audit["degraded_fields"][0]["json_field_path"],
                "$.observations[*].subject_codes[1]",
            )
            self.assertEqual(result["decision_trace"]["counts"]["failed_observation_count"], 0)

    def test_zero_aha_requires_explicit_completed_dual_path_search_outcome(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = run_x02(make_x02_bundle(Path(temporary), 3), ScriptedGateway())
            self.assertEqual(result["ahas"], [])
            selection = result["decision_trace"]["aha_set_selection"]
            self.assertEqual(selection["search_contract"], "EVENT_AND_DISCOVERY_AHA_PATHS_V02")
            self.assertEqual(selection["search_outcome"], "NO_GROUNDED_AHA_AFTER_SEARCH")
            self.assertEqual(selection["event_candidate_count"], 0)
            self.assertEqual(selection["discovery_candidate_count"], 0)
            self.assertTrue(selection["membership_order_separate_from_output_order"])
            self.assertEqual(selection["pair_ledger"], [])

    def test_six_asset_candidate_is_reduced_only_in_s10(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = run_x02(
                make_x02_bundle(Path(temporary), 6),
                ScriptedGateway(),
            )
            passed = [
                item for item in result["decision_trace"]["chapter_candidates"]
                if item["validation_status"] == "PASSED"
            ]
            self.assertEqual(len(passed), 1)
            self.assertIn("CANDIDATE_SIZE_6_NOT_FINAL_MEDIA_COUNT", passed[0]["reason_codes"])
            self.assertEqual(len(result["chapters"]), 1)
            self.assertEqual(len(result["chapters"][0]["selected_media"]), 5)



    def test_historical_v03_route_keeps_historical_contract_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = run_x02_v03(
                make_x02_bundle(Path(temporary), 6),
                ScriptedGateway(),
            )
            self.assertEqual(result["schema_version"], X02_V03_SCHEMA_VERSION)
            self.assertEqual(result["trace"]["pipeline_version"], X02_V03_PIPELINE_VERSION)
            self.assertNotIn("storyline_contract_version", result)
            self.assertNotIn("storyline_identity", result["chapters"][0])

    def test_historical_v03_aha_membership_remains_time_ordered_v01(self):
        plan = {
            0: "HISTORIC_TOWN_WALK",
            1: "HISTORIC_TOWN_WALK",
            2: "HISTORIC_TOWN_WALK",
            3: "MARKET_VISIT",
            4: "CAFE_STOP",
            5: "HOME_LIFE",
            6: "CRAFT_SESSION",
        }
        overrides = {
            3: {
                "event_kind": "DISCOVERY",
                "event_salience": "MEDIUM",
                "support_grade": "MODERATE",
            },
            5: {
                "event_kind": "PLAYFUL_ANIMAL",
                "event_salience": "HIGH",
                "subject_codes": ["DOG"],
            },
            6: {"event_kind": "RESULT", "event_salience": "HIGH"},
        }
        with tempfile.TemporaryDirectory() as temporary:
            result = run_x02_v03(
                make_x02_bundle(Path(temporary), 7),
                ScriptedGateway(plan, observation_overrides=overrides),
            )
        selection = result["decision_trace"]["aha_set_selection"]
        self.assertEqual(selection["search_contract"], "EVENT_AND_DISCOVERY_AHA_PATHS_V01")
        candidate_by_source = {
            item["source_asset_id"]: item["candidate_id"]
            for item in result["decision_trace"]["aha_candidates"]
            if item["validation_status"] == "PASSED"
        }
        expected = [
            candidate_by_source[result["observations"][index]["source_asset_id"]]
            for index in (3, 4, 5)
        ]
        self.assertEqual(selection["selected_candidate_ids"], expected)
        self.assertNotIn("semantic_day_state", result)

    def test_single_pass_writer_preserves_complete_local_fact_fallback(self):
        with tempfile.TemporaryDirectory() as temporary:
            gateway = ScriptedGateway(fail_first_writer=True)
            result = run_x02(make_x02_bundle(Path(temporary), 6), gateway)
            self.assertEqual(gateway.writer_calls, 1)
            self.assertEqual(len(result["chapters"]), 1)
            writer_items = result["decision_trace"]["writer_items"]
            self.assertTrue(any(
                item["validation_status"] == "REJECTED"
                and "CHAPTER_STORY_SENTENCE_COUNT_INVALID" in item["reason_codes"]
                and item["attempt"] == 1
                for item in writer_items
            ))
            self.assertTrue(any(
                item["validation_status"] == "PASSED"
                and item.get("surface_source") == "DETERMINISTIC_GROUNDED_FALLBACK"
                for item in writer_items
            ))

    def test_chapter_story_over_48_characters_is_audited_but_not_blocked(self):
        fact_id = "fact-chapter"
        context = {
            "locale": "zh-Hans",
            "memories": [{
                "candidate_id": "chapter-candidate",
                "memory_type": "CHAPTER",
                "facts": [{"fact_id": fact_id}],
            }],
        }
        text = "沿着湿润的石板路慢慢向前，牌坊、临街店铺、木窗和层层屋檐依次出现在这段古镇步行的沿途视野中，远处还能看见更多老建筑。"
        narratives, audit, invalid = _validate_writer_output({
            "chapters": [{
                "candidate_id": "chapter-candidate",
                "title": "古镇漫步",
                "text": text,
                "claim_ids": [fact_id],
            }],
            "ahas": [],
        }, context)
        self.assertEqual(invalid, [])
        self.assertIn("chapter-candidate", narratives)
        self.assertGreater(audit[0]["text_visible_characters"], 48)
        self.assertIn(
            "CHAPTER_STORY_OVER_PREVIEW_WRITING_TARGET",
            audit[0]["quality_flags"],
        )

    def test_aha_length_failure_records_exact_count_and_retry_scope(self):
        chapter_fact = "fact-chapter"
        aha_fact = "fact-aha"
        context = {
            "locale": "zh-Hans",
            "memories": [
                {
                    "candidate_id": "chapter-candidate",
                    "memory_type": "CHAPTER",
                    "facts": [{"fact_id": chapter_fact}],
                },
                {
                    "candidate_id": "aha-candidate",
                    "memory_type": "AHA",
                    "facts": [{"fact_id": aha_fact}],
                },
            ],
        }
        long_aha = "一只小猫忽然跳上桌面并碰倒了旁边的白色纸杯。"
        narratives, audit, invalid = _validate_writer_output({
            "chapters": [{
                "candidate_id": "chapter-candidate",
                "title": "古镇漫步",
                "text": "沿着老街继续向前。",
                "claim_ids": [chapter_fact],
            }],
            "ahas": [{
                "candidate_id": "aha-candidate",
                "title": "小猫插曲",
                "text": long_aha,
                "claim_ids": [aha_fact],
            }],
        }, context, attempt=1)
        self.assertEqual(set(narratives), {"chapter-candidate"})
        self.assertEqual(invalid, ["aha-candidate"])
        aha_audit = next(item for item in audit if item["candidate_id"] == "aha-candidate")
        self.assertEqual(aha_audit["attempt"], 1)
        self.assertEqual(aha_audit["draft_text"], long_aha)
        self.assertEqual(aha_audit["text_visible_characters"], len(long_aha))
        self.assertEqual(aha_audit["required_text_visible_max"], 20)
        self.assertIn("AHA_MOMENT_LINE_INVALID", aha_audit["reason_codes"])

        retry_context = _writer_retry_context(context, invalid, audit)
        self.assertEqual(
            [item["candidate_id"] for item in retry_context["memories"]],
            ["aha-candidate"],
        )
        self.assertEqual(retry_context["previous_failures"][0]["text_visible_characters"], len(long_aha))
        retry_prompt = _writer_prompt(retry_context, retry=True)
        self.assertIn("exact draft", retry_prompt)
        self.assertIn('"required_text_visible_max": 20', retry_prompt)

        repaired, retry_audit, retry_invalid = _validate_writer_output({
            "chapters": [],
            "ahas": [{
                "candidate_id": "aha-candidate",
                "title": "小猫插曲",
                "text": "小猫跳上桌，碰倒了纸杯。",
                "claim_ids": [aha_fact],
            }],
        }, retry_context, attempt=2)
        self.assertEqual(retry_invalid, [])
        self.assertIn("aha-candidate", repaired)
        self.assertEqual(retry_audit[0]["attempt"], 2)

    def test_writer_failure_uses_same_memory_grounded_fallback_not_empty_day(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = run_x02(
                make_x02_bundle(Path(temporary), 3),
                ScriptedGateway(fail_all_writer=True),
            )
            self.assertEqual(len(result["chapters"]), 1)
            self.assertEqual(result["ahas"], [])
            self.assertEqual(result["semantic_day_state"], "CHAPTER_DAY")
            self.assertEqual(
                result["delivery_state"],
                "READY_WITH_GROUNDED_COPY_FALLBACK",
            )
            self.assertEqual(result["output_mode"], "CHAPTER_DAY")
            self.assertEqual(result["decision_trace"]["blocked_memories"], [])
            self.assertEqual(
                result["chapters"][0]["surface_source"],
                "DETERMINISTIC_GROUNDED_FALLBACK",
            )
            self.assertEqual(
                result["selected_memory_outcomes"][0]["surface_state"],
                "DETERMINISTIC_FALLBACK_VERIFIED",
            )

    def test_x02_is_explicitly_not_production_and_has_stage_costs(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = run_x02(make_x02_bundle(Path(temporary), 3), ScriptedGateway())
            self.assertEqual(result["trace"]["pipeline_version"], X02_PIPELINE_VERSION)
            self.assertFalse(result["production_ready"])
            self.assertEqual(result["trace"]["s13_status"], "NOT_EXECUTED_IN_WEB_PREVIEW")
            self.assertGreater(result["trace"]["model_calls"], 0)
            self.assertGreater(result["trace"]["input_tokens"], 0)
            self.assertTrue(all("duration_ms" in item for item in result["trace"]["stage_metrics"]))

    def test_billable_invalid_perception_batches_isolate_then_keep_failure_cost_evidence(self):
        def transport(url, headers, body, timeout):
            payload = {
                "id": "qwen-failed-structured-request",
                "choices": [{"message": {"content": "not-json"}}],
                "usage": {"prompt_tokens": 123, "completion_tokens": 17},
            }
            return 200, {"x-request-id": "qwen-failed-structured-request"}, json.dumps(payload).encode()

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = make_x02_bundle(root / "bundle", 3)
            adapter = QwenChatCompletionsAdapter(
                api_key="test-key",
                transport=transport,
            )
            with self.assertRaises(X02ExecutionError) as caught:
                run_x02(manifest_path, QwenStageGateway(adapter))
            error = caught.exception
            self.assertEqual(error.code, "MODEL_STRUCTURED_OUTPUT_INVALID")
            self.assertEqual(error.stage, "S05_S07_STRUCTURE_PROPOSAL")
            # Generic invalid/timeout/provider responses are not evidence of an
            # asset-local fault, so V04.1 no longer recursively fans one bad
            # batch into eight billable attempts.
            self.assertEqual(len(error.stage_runs), 2)
            perception_runs = [
                item for item in error.stage_runs
                if item.stage.startswith("S04_PERCEPTION_BATCH_")
            ]
            self.assertEqual(len(perception_runs), 1)
            self.assertEqual(error.stage_runs[-1].stage, "S05_S07_STRUCTURE_PROPOSAL")
            self.assertTrue(all(item.input_tokens == 123 for item in error.stage_runs))
            self.assertTrue(all(item.output_tokens == 17 for item in error.stage_runs))
            self.assertTrue(all(item.estimated_cost_usd > 0 for item in error.stage_runs))

            manifest = json.loads(manifest_path.read_text())
            failure_id, path = _write_x02_failed_run_audit(
                root / "audits", manifest, error, 12.5, 4_096
            )
            audit = json.loads(path.read_text())
            self.assertEqual(audit["failure_id"], failure_id)
            self.assertEqual(audit["failure"]["stage"], "S05_S07_STRUCTURE_PROPOSAL")
            self.assertEqual(audit["schema_version"], X02_FAILED_RUN_AUDIT_SCHEMA_VERSION)
            billable = [
                item for item in audit["stage_metrics"]
                if item["model_calls"] == 1
            ]
            self.assertEqual(len(billable), 2)
            self.assertTrue(all(item["input_tokens"] == 123 for item in billable))
            self.assertTrue(all(item["output_tokens"] == 17 for item in billable))
            self.assertTrue(all(item["estimated_cost_usd"] > 0 for item in billable))
            self.assertEqual(audit["completed_stage_calls"], [])
            self.assertEqual(len(audit["stage_call_attempts"]), 2)
            self.assertTrue(all(
                item["call_status"] == "RESPONSE_INVALID"
                for item in audit["stage_call_attempts"]
            ))
            self.assertFalse(audit["image_payloads_included"])


class X02V041ContractAndBehaviorTests(unittest.TestCase):
    def _run_v041(self, root, count, gateway):
        return x02_module.run_x02_v041(
            make_x02_bundle(Path(root), count),
            gateway,
        )

    def _source_asset_id(self, result, index):
        return result["observations"][index]["source_asset_id"]

    def test_historical_storyline_v02_contract_retains_its_recorded_stop_losses(self):
        contract = json.loads(X02_STORYLINE_V02_CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["schema_version"], "DIARY_ONE_X02_STORYLINE_V02")
        self.assertEqual(
            contract["contract_status"],
            "PROVISIONAL_RESEARCH_STOP_LOSS_NOT_PERMANENT_PRODUCT_THRESHOLD",
        )
        self.assertEqual(contract["max_member_gap_in_source_order"], 8)
        parameters = contract["provisional_research_parameters"]
        self.assertEqual(
            parameters,
            {
                "parameter_status": "CALIBRATE_WITH_FRESH_REAL_RUNS_DO_NOT_TREAT_AS_UNIVERSAL",
                "episode_partition_max_gap_in_source_order": 8,
                "max_total_span_in_source_order": 12,
                "max_interruption_ratio": 0.34,
                "max_temporal_segments": 4,
                "split_challenge_min_member_count": 6,
            },
        )
        challenge = contract["whole_vs_split_challenge"]
        self.assertTrue(challenge["enabled"])
        self.assertFalse(challenge["local_member_gap_is_sufficient_alone"])
        self.assertEqual(challenge["partition_counts"], [2, 3])
        compact = contract["compact_two_member_policy"]
        self.assertFalse(compact["category_restriction"])
        self.assertNotIn("allowed_focus_codes", compact)
        self.assertEqual(compact["required_member_count"], 2)
        self.assertEqual(compact["minimum_supported_fact_count_per_member"], 1)
        self.assertEqual(set(compact["allowed_fact_support_grades"]), {"STRONG", "MODERATE"})
        self.assertEqual(
            set(compact["distinctness_any_of"]),
            {"MEMBER_UNIQUE_GROUNDED_NORMALIZED_MOTIF"},
        )
        self.assertTrue(compact["each_member_must_contribute_unique_facet"])
        self.assertFalse(compact["beat_role_is_sufficient_alone"])
        self.assertFalse(compact["time_distance_is_sufficient_alone"])

    def test_v041_preview_schema_separates_semantics_delivery_and_surface_provenance(self):
        schema = json.loads(X02_V041_PREVIEW_SCHEMA_PATH.read_text(encoding="utf-8"))
        properties = schema["properties"]
        self.assertEqual(
            properties["schema_version"]["const"],
            "DIARY_ONE_X02_STAGED_PREVIEW_V04_1",
        )
        self.assertEqual(
            properties["trace"]["properties"]["pipeline_version"]["const"],
            "X02_STAGED_REAL_MEDIA_PREVIEW_V04_1",
        )
        self.assertEqual(
            properties["storyline_contract_version"]["const"],
            "DIARY_ONE_X02_STORYLINE_V03",
        )
        self.assertEqual(properties["validation_scope"]["const"], "STAGED_PREVIEW_ONLY")
        self.assertEqual(properties["coverage_status"]["enum"], ["COMPLETE", "PARTIAL_UNRESOLVED"])
        self.assertEqual(properties["unresolved_asset_ids"]["type"], "array")
        self.assertEqual(
            properties["semantic_day_state"]["enum"],
            ["CHAPTER_DAY", "HIGHLIGHT_DAY", "EMPTY_DAY", "UNRESOLVED_DAY"],
        )
        self.assertEqual(
            properties["delivery_state"]["enum"],
            [
                "READY_PRIMARY_COPY",
                "READY_WITH_GROUNDED_COPY_FALLBACK",
                "READY_WITH_ITEM_BLOCKS",
                "PIPELINE_BLOCKED",
                "NO_GROUNDED_MEMORY",
            ],
        )
        self.assertTrue(properties["output_mode"]["deprecated"])
        self.assertIn("semantic_day_state plus delivery_state", properties["output_mode"]["description"])
        self.assertEqual(
            properties["timeline_basis"]["const"], "SYNTHETIC_SEQUENCE_ONLY"
        )
        self.assertIsNone(properties["timeline_date"]["const"])
        self.assertEqual(
            set(properties["time_reliability"]["required"]),
            {"capture_time_reliable", "interval_reliable", "timezone_reliable"},
        )
        self.assertFalse(properties["time_reliability"]["additionalProperties"])
        self.assertTrue(all(
            properties["time_reliability"]["properties"][field]["const"] is False
            for field in (
                "capture_time_reliable", "interval_reliable", "timezone_reliable"
            )
        ))

        outcome = schema["$defs"]["selectedMemoryOutcome"]
        self.assertEqual(
            set(outcome["required"]),
            {
                "memory_type", "memory_id", "selection_state", "media_state",
                "surface_state", "visibility_state",
            },
        )
        self.assertEqual(set(outcome["properties"]), set(outcome["required"]))
        self.assertEqual(outcome["properties"]["selection_state"]["const"], "S09_SELECTED")
        self.assertEqual(
            outcome["properties"]["media_state"]["enum"],
            ["S10_MEDIA_READY", "S10_MEDIA_BLOCKED"],
        )
        self.assertEqual(
            outcome["properties"]["surface_state"]["enum"],
            [
                "MODEL_SURFACE_VERIFIED",
                "DETERMINISTIC_FALLBACK_VERIFIED",
                "COPY_BLOCKED",
                "NOT_ATTEMPTED",
            ],
        )
        memory = schema["$defs"]["memory"]
        self.assertIn("surface_source", memory["required"])
        self.assertIn("surface_policy_version", memory["required"])
        self.assertEqual(
            memory["properties"]["surface_policy_version"]["const"],
            "DIARY_ONE_X02_WRITER_SURFACE_V02",
        )
        self.assertEqual(
            memory["properties"]["surface_source"]["enum"],
            ["MODEL_WRITER", "DETERMINISTIC_GROUNDED_FALLBACK"],
        )
        self.assertEqual(
            memory["properties"]["publication_status"]["enum"],
            ["STAGED_PREVIEW_VALIDATED", "STAGED_PREVIEW_DIAGNOSTIC_ONLY"],
        )

        aha_selection = schema["$defs"]["ahaSetSelection"]
        self.assertEqual(
            aha_selection["properties"]["algorithm"]["const"],
            "V04_1_AHA_LEXICOGRAPHIC_RELATION_AWARE_SET_SELECTION",
        )
        self.assertEqual(
            aha_selection["properties"]["search_contract"]["const"],
            "EVENT_AND_DISCOVERY_AHA_PATHS_V02",
        )
        self.assertTrue(
            aha_selection["properties"]["membership_order_separate_from_output_order"]["const"]
        )
        aha_pair = schema["$defs"]["ahaPairLedger"]
        self.assertEqual(
            aha_pair["properties"]["relation"]["enum"],
            [
                "EXACT_DUPLICATE",
                "UNRESOLVED_POTENTIAL_CONFLICT",
                "NO_CONFLICT_EVIDENCE",
            ],
        )
        self.assertEqual(
            aha_pair["properties"]["selection_effect"]["enum"],
            ["FORBID_COSELECT", "AT_MOST_ONE", "ALLOW_COSELECT"],
        )
        self.assertIn("reason_codes", aha_pair["required"])
        self.assertIn("published_sequence_candidate_ids", aha_selection["required"])
        self.assertIn("publication_order_basis", aha_selection["required"])
        self.assertEqual(
            aha_selection["properties"]["publication_order_basis"]["const"],
            "IMPORT_SEQUENCE_INDEX_THEN_CANDIDATE_ID_NOT_CHRONOLOGY",
        )
        split_challenge = schema["$defs"]["splitChallenge"]
        self.assertEqual(
            set(split_challenge["required"]),
            {
                "triggered", "trigger_reason_codes", "whole_candidate_summary",
                "partition_alternatives", "decision", "reason_codes",
            },
        )
        batching = schema["$defs"]["perceptionBatching"]
        self.assertTrue({
            "policy", "max_assets", "max_frames", "max_evidence_bytes",
            "single_asset_retry_limit", "run_max_model_call_attempts",
            "model_call_attempt_count", "circuit_breaker_tripped",
            "planned_batch_count", "attempts",
            "coverage_status", "unresolved_asset_ids",
        }.issubset(set(batching["required"])))
        self.assertEqual(
            batching["properties"]["policy"]["const"],
            "V04_1_BOUNDED_ASSETS_FRAMES_BYTES_WITH_FAILURE_ISOLATION",
        )
        self.assertEqual(batching["properties"]["max_assets"]["const"], 3)
        self.assertEqual(batching["properties"]["max_frames"]["const"], 18)
        self.assertEqual(batching["properties"]["max_evidence_bytes"]["const"], 4 * 1024 * 1024)
        self.assertEqual(batching["properties"]["single_asset_retry_limit"]["const"], 1)
        self.assertEqual(batching["properties"]["run_max_model_call_attempts"]["const"], 96)
        self.assertIn(
            "Whole X02 V04.1 run count",
            batching["properties"]["model_call_attempt_count"]["description"],
        )
        self.assertEqual(
            batching["properties"]["attempts"]["items"]["$ref"],
            "#/$defs/perceptionAttempt",
        )
        attempt = schema["$defs"]["perceptionAttempt"]
        self.assertFalse(attempt["additionalProperties"])
        self.assertEqual(
            set(attempt["required"]),
            {
                "attempt_id", "parent_attempt_id", "asset_ids", "asset_count",
                "frame_count", "evidence_bytes", "provider_call_attempted",
                "attempt_kind", "status", "reason_code", "recovery_action",
                "terminal_unresolved_asset_ids",
            },
        )
        self.assertIn(
            "RESPONSE_INVALID",
            schema["$defs"]["stageMetric"]["properties"]["call_status"]["enum"],
        )

    def test_v041_representative_result_matches_the_versioned_preview_schema(self):
        plan = {
            0: "HISTORIC_TOWN_WALK",
            1: "HISTORIC_TOWN_WALK",
            2: "HISTORIC_TOWN_WALK",
            3: "HOME_LIFE",
            4: "CRAFT_SESSION",
        }
        overrides = {
            3: {
                "event_kind": "DISCOVERY",
                "event_salience": "HIGH",
                "motifs": ["窗边新发现"],
            },
            4: {
                "event_kind": "RESULT",
                "event_salience": "HIGH",
                "motifs": ["手作完成"],
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(
                temporary,
                5,
                ScriptedGateway(plan, observation_overrides=overrides),
            )
        schema = json.loads(X02_V041_PREVIEW_SCHEMA_PATH.read_text(encoding="utf-8"))
        assert_json_schema_instance(self, schema, result)
        assert_v041_cross_field_truth(self, result)
    def test_v041_schema_rejects_state_timeline_and_batching_contradictions(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(temporary, 3, ScriptedGateway())
        schema = json.loads(X02_V041_PREVIEW_SCHEMA_PATH.read_text(encoding="utf-8"))

        invalid_instances = []

        nested_coverage_drift = copy.deepcopy(result)
        nested_coverage_drift["decision_trace"]["perception_batching"][
            "coverage_status"
        ] = "PARTIAL_UNRESOLVED"
        invalid_instances.append(("nested coverage status drift", nested_coverage_drift))

        partial_without_unresolved = copy.deepcopy(result)
        partial_without_unresolved["coverage_status"] = "PARTIAL_UNRESOLVED"
        invalid_instances.append(("partial coverage without unresolved assets", partial_without_unresolved))

        false_empty = copy.deepcopy(result)
        false_empty["semantic_day_state"] = "EMPTY_DAY"
        false_empty["delivery_state"] = "NO_GROUNDED_MEMORY"
        false_empty["output_mode"] = "EMPTY_DAY"
        invalid_instances.append(("empty state with selected memories", false_empty))

        wrong_projection = copy.deepcopy(result)
        wrong_projection["output_mode"] = "HIGHLIGHT_DAY"
        invalid_instances.append(("output projection disagrees with Chapter semantics", wrong_projection))

        primary_with_fallback = copy.deepcopy(result)
        primary_with_fallback["selected_memory_outcomes"][0][
            "surface_state"
        ] = "DETERMINISTIC_FALLBACK_VERIFIED"
        invalid_instances.append(("primary delivery contains fallback", primary_with_fallback))

        visible_copy_block = copy.deepcopy(result)
        visible_copy_block["selected_memory_outcomes"][0]["surface_state"] = "COPY_BLOCKED"
        invalid_instances.append(("copy-blocked item is visible", visible_copy_block))

        synthetic_with_date = copy.deepcopy(result)
        synthetic_with_date["timeline_date"] = "2026-08-31"
        invalid_instances.append(("synthetic timeline exposes a date", synthetic_with_date))

        synthetic_claims_reliable_time = copy.deepcopy(result)
        synthetic_claims_reliable_time["time_reliability"][
            "capture_time_reliable"
        ] = True
        invalid_instances.append(("synthetic timeline claims reliable capture time", synthetic_claims_reliable_time))

        wrong_batch_limit = copy.deepcopy(result)
        wrong_batch_limit["decision_trace"]["perception_batching"]["max_assets"] = 4
        invalid_instances.append(("V04.1 batching limit drift", wrong_batch_limit))

        contradictory_attempt = copy.deepcopy(result)
        contradictory_attempt["decision_trace"]["perception_batching"]["attempts"][0][
            "recovery_action"
        ] = "BISECT"
        invalid_instances.append(("validated attempt claims recovery split", contradictory_attempt))

        unknown_attempt_field = copy.deepcopy(result)
        unknown_attempt_field["decision_trace"]["perception_batching"]["attempts"][0][
            "uncontracted_field"
        ] = True
        invalid_instances.append(("attempt carries uncontracted field", unknown_attempt_field))

        for label, invalid in invalid_instances:
            with self.subTest(label=label), self.assertRaises(AssertionError):
                assert_json_schema_instance(self, schema, invalid)

        capture_time_result = copy.deepcopy(result)
        capture_time_result["timeline_basis"] = "CAPTURE_TIME"
        capture_time_result["timeline_date"] = "2026-08-31"
        capture_time_result["time_reliability"] = {
            "capture_time_reliable": True,
            "interval_reliable": True,
            "timezone_reliable": False,
        }
        with self.assertRaises(AssertionError):
            assert_json_schema_instance(self, schema, capture_time_result)

    def test_v041_targeted_equality_checks_reject_id_and_publication_drift(self):
        gateway = PerceptionFailureGateway(
            fail_multi_asset=True,
            permanently_failed_indices={1},
        )
        with tempfile.TemporaryDirectory() as temporary:
            partial = self._run_v041(temporary, 4, gateway)
        assert_v041_cross_field_truth(self, partial)

        unresolved_id_drift = copy.deepcopy(partial)
        unresolved_id_drift["decision_trace"]["perception_batching"][
            "unresolved_asset_ids"
        ] = ["different-asset-with-same-cardinality"]
        with self.assertRaises(AssertionError):
            assert_v041_cross_field_truth(self, unresolved_id_drift)

        published_id_drift = copy.deepcopy(partial)
        published_id_drift["chapters"][0]["id"] = str(uuid.uuid4())
        with self.assertRaises(AssertionError):
            assert_v041_cross_field_truth(self, published_id_drift)

    def test_v041_primary_copy_result_reports_independent_state_axes(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(temporary, 3, ScriptedGateway())
        self.assertEqual(result["schema_version"], "DIARY_ONE_X02_STAGED_PREVIEW_V04_1")
        self.assertEqual(
            result["trace"]["pipeline_version"],
            "X02_STAGED_REAL_MEDIA_PREVIEW_V04_1",
        )
        self.assertEqual(result["storyline_contract_version"], "DIARY_ONE_X02_STORYLINE_V03")
        self.assertEqual(result["writer_surface_policy_version"], "DIARY_ONE_X02_WRITER_SURFACE_V02")
        self.assertEqual(result["validation_scope"], "STAGED_PREVIEW_ONLY")
        self.assertEqual(result["coverage_status"], "COMPLETE")
        self.assertEqual(result["unresolved_asset_ids"], [])
        self.assertEqual(result["semantic_day_state"], "CHAPTER_DAY")
        self.assertEqual(result["delivery_state"], "READY_PRIMARY_COPY")
        self.assertEqual(result["output_mode"], "CHAPTER_DAY")
        self.assertEqual(result["timeline_basis"], "SYNTHETIC_SEQUENCE_ONLY")
        self.assertIsNone(result["timeline_date"])
        self.assertEqual(
            result["time_reliability"],
            {
                "capture_time_reliable": False,
                "interval_reliable": False,
                "timezone_reliable": False,
            },
        )
        batching = result["decision_trace"]["perception_batching"]
        self.assertEqual(batching["max_assets"], 3)
        self.assertEqual(batching["max_frames"], 18)
        self.assertEqual(batching["max_evidence_bytes"], 4 * 1024 * 1024)
        self.assertEqual(batching["single_asset_retry_limit"], 1)
        self.assertEqual(batching["planned_batch_count"], 1)
        self.assertEqual(batching["coverage_status"], "COMPLETE")
        self.assertEqual(batching["unresolved_asset_ids"], [])
        self.assertTrue(batching["attempts"])
        self.assertEqual(len(result["selected_memory_outcomes"]), 1)
        outcome = result["selected_memory_outcomes"][0]
        self.assertEqual(outcome["memory_type"], "CHAPTER")
        self.assertEqual(outcome["memory_id"], result["chapters"][0]["id"])
        self.assertEqual(outcome["selection_state"], "S09_SELECTED")
        self.assertEqual(outcome["media_state"], "S10_MEDIA_READY")
        self.assertEqual(outcome["surface_state"], "MODEL_SURFACE_VERIFIED")
        self.assertEqual(outcome["visibility_state"], "VISIBLE_PREVIEW")
        self.assertEqual(result["chapters"][0]["surface_source"], "MODEL_WRITER")
        self.assertEqual(
            result["chapters"][0]["surface_policy_version"],
            "DIARY_ONE_X02_WRITER_SURFACE_V02",
        )

    def test_v041_multi_asset_perception_error_bisects_and_keeps_good_assets(self):
        gateway = PerceptionFailureGateway(fail_multi_asset=True)
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(temporary, 3, gateway)
        self.assertEqual(
            [(item["indices"], item["status"]) for item in gateway.perception_attempts],
            [
                ((0, 1, 2), "FAILED"),
                ((0,), "VALIDATED"),
                ((1, 2), "FAILED"),
                ((1,), "VALIDATED"),
                ((2,), "VALIDATED"),
            ],
        )
        self.assertEqual([item["status"] for item in result["observations"]], ["OBSERVED"] * 3)
        self.assertEqual(result["coverage_status"], "COMPLETE")
        self.assertEqual(result["unresolved_asset_ids"], [])
        batching = result["decision_trace"]["perception_batching"]
        self.assertEqual(batching["planned_batch_count"], 1)
        self.assertEqual(len(batching["attempts"]), 5)
        self.assertEqual(
            [item["asset_count"] for item in batching["attempts"]],
            [3, 1, 2, 1, 1],
        )
        self.assertEqual(
            [item["status"] for item in batching["attempts"]],
            ["FAILED", "VALIDATED", "FAILED", "VALIDATED", "VALIDATED"],
        )

        historical_gateway = PerceptionFailureGateway(fail_multi_asset=True)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(X02ExecutionError) as caught:
                run_x02_v03(
                    make_x02_bundle(Path(temporary), 3),
                    historical_gateway,
                )
        self.assertEqual(caught.exception.stage, "S04_PERCEPTION_BATCH_001")
        self.assertEqual(
            caught.exception.code,
            "PERCEPTION_ASSET_LOCAL_CONTRACT_INVALID",
        )
        self.assertEqual(len(caught.exception.stage_runs), 1)
        self.assertEqual(
            historical_gateway.perception_attempts,
            [{"stage": "S04_PERCEPTION_BATCH_001", "indices": (0, 1, 2), "status": "FAILED"}],
        )

    def test_v041_single_asset_retry_exhaustion_is_partial_and_never_empty_success(self):
        gateway = PerceptionFailureGateway(
            fail_multi_asset=True,
            permanently_failed_indices={1},
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(temporary, 4, gateway)
        unresolved_id = self._source_asset_id(result, 1)
        self.assertEqual(
            [item["status"] for item in result["observations"]],
            ["OBSERVED", "FAILED", "OBSERVED", "OBSERVED"],
        )
        self.assertEqual(result["coverage_status"], "PARTIAL_UNRESOLVED")
        self.assertEqual(result["unresolved_asset_ids"], [unresolved_id])
        self.assertEqual(result["semantic_day_state"], "UNRESOLVED_DAY")
        self.assertEqual(result["delivery_state"], "PIPELINE_BLOCKED")
        self.assertEqual(result["output_mode"], "PIPELINE_BLOCKED")
        self.assertNotEqual(result["output_mode"], "EMPTY_DAY")
        self.assertEqual(len(result["chapters"]), 1)
        self.assertEqual(
            result["chapters"][0]["publication_status"],
            "STAGED_PREVIEW_DIAGNOSTIC_ONLY",
        )
        self.assertTrue(all(
            item["visibility_state"] == "DIAGNOSTIC_ONLY"
            for item in result["selected_memory_outcomes"]
        ))
        batching = result["decision_trace"]["perception_batching"]
        self.assertEqual(batching["coverage_status"], "PARTIAL_UNRESOLVED")
        self.assertEqual(batching["unresolved_asset_ids"], [unresolved_id])
        failed_single_attempts = [
            item for item in batching["attempts"]
            if item["asset_ids"] == [unresolved_id] and item["status"] == "FAILED"
        ]
        # Bisection isolates a failing singleton but does not retry that child
        # again, bounding a three-asset failure tree to five calls.
        self.assertEqual(len(failed_single_attempts), 1)
        schema = json.loads(X02_V041_PREVIEW_SCHEMA_PATH.read_text(encoding="utf-8"))
        assert_json_schema_instance(self, schema, result)
        assert_v041_cross_field_truth(self, result)

    def test_v041_partial_without_candidates_and_all_failed_are_unresolved_not_empty(self):
        partial_gateway = PerceptionFailureGateway(
            fail_multi_asset=True,
            permanently_failed_indices={2},
        )
        with tempfile.TemporaryDirectory() as temporary:
            partial = self._run_v041(temporary, 3, partial_gateway)
        self.assertEqual(partial["coverage_status"], "PARTIAL_UNRESOLVED")
        self.assertEqual(partial["semantic_day_state"], "UNRESOLVED_DAY")
        self.assertEqual(partial["delivery_state"], "PIPELINE_BLOCKED")
        self.assertEqual(partial["output_mode"], "PIPELINE_BLOCKED")
        self.assertEqual(partial["chapters"], [])
        self.assertEqual(partial["ahas"], [])

        all_failed_gateway = PerceptionFailureGateway(
            fail_multi_asset=True,
            permanently_failed_indices={0, 1},
        )
        with tempfile.TemporaryDirectory() as temporary:
            all_failed = self._run_v041(temporary, 2, all_failed_gateway)
        self.assertEqual(all_failed["coverage_status"], "PARTIAL_UNRESOLVED")
        self.assertEqual(all_failed["semantic_day_state"], "UNRESOLVED_DAY")
        self.assertEqual(all_failed["delivery_state"], "PIPELINE_BLOCKED")
        self.assertEqual(all_failed["output_mode"], "PIPELINE_BLOCKED")
        self.assertEqual(len(all_failed["unresolved_asset_ids"]), 2)

        schema = json.loads(X02_V041_PREVIEW_SCHEMA_PATH.read_text(encoding="utf-8"))
        assert_json_schema_instance(self, schema, partial)
        assert_json_schema_instance(self, schema, all_failed)
        assert_v041_cross_field_truth(self, partial)
        assert_v041_cross_field_truth(self, all_failed)
        false_empty = dict(partial)
        false_empty["semantic_day_state"] = "EMPTY_DAY"
        with self.assertRaises(AssertionError):
            assert_json_schema_instance(self, schema, false_empty)

    def test_v041_failed_stage_run_usage_and_request_id_remain_in_trace(self):
        gateway = PerceptionFailureGateway(fail_multi_asset=True)
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(temporary, 3, gateway)
        self.assertEqual(len(gateway.failed_stage_runs), 2)
        expected_cost = round((701 * 2.0 + 29 * 3.0) / 1_000_000, 8)
        stage_metrics = result["trace"]["stage_metrics"]
        for failed in gateway.failed_stage_runs:
            matching = [
                item for item in stage_metrics
                if item["stage"] == failed.stage
                and item.get("request_id") == failed.request_id
            ]
            self.assertEqual(len(matching), 1)
            metric = matching[0]
            self.assertEqual(metric["model_calls"], 1)
            self.assertEqual(metric["input_tokens"], 701)
            self.assertEqual(metric["output_tokens"], 29)
            self.assertEqual(metric["estimated_cost_usd"], expected_cost)
            self.assertEqual(result["trace"]["request_ids"].count(failed.request_id), 1)
        self.assertGreaterEqual(result["trace"]["input_tokens"], 2 * 701)
        self.assertGreaterEqual(result["trace"]["output_tokens"], 2 * 29)
        self.assertGreaterEqual(result["trace"]["estimated_cost_usd"], 2 * expected_cost)

    def test_provider_transport_timeout_has_failed_stage_run_and_v03_http_envelope_stays_stable(self):
        def timeout_transport(url, headers, body, timeout):
            raise TimeoutError("socket timed out")

        timeout_gateway = QwenStageGateway(QwenChatCompletionsAdapter(
            api_key="test-key",
            transport=timeout_transport,
        ))
        with self.assertRaises(X02StageCallError) as timeout_caught:
            timeout_gateway.call(
                "S04_PERCEPTION_BATCH_001", "test", {},
                context={"_x02_policy_version": "V04_1"},
            )
        self.assertEqual(timeout_caught.exception.code, "MODEL_TRANSPORT_TIMEOUT")
        failed_run = timeout_caught.exception.stage_run
        self.assertEqual(failed_run.stage, "S04_PERCEPTION_BATCH_001")
        self.assertEqual(failed_run.model_calls, 1)
        self.assertEqual(failed_run.input_tokens, 0)
        self.assertEqual(failed_run.output_tokens, 0)
        self.assertEqual(
            failed_run.output,
            {"failure": "STRUCTURED_RESPONSE_UNAVAILABLE"},
        )

        def x01_transport_failure(url, headers, body, timeout):
            raise X01Error("could not reach provider")

        x01_gateway = QwenStageGateway(QwenChatCompletionsAdapter(
            api_key="test-key",
            transport=x01_transport_failure,
        ))
        with self.assertRaises(X02StageCallError) as x01_caught:
            x01_gateway.call(
                "S11_WRITER_ATTEMPT_1", "test", {},
                context={"_x02_policy_version": "V04_1"},
            )
        self.assertEqual(x01_caught.exception.code, "MODEL_TRANSPORT_FAILED")
        self.assertEqual(
            x01_caught.exception.stage_run.stage,
            "S11_WRITER_ATTEMPT_1",
        )

        def http_failure_transport(url, headers, body, timeout):
            return 503, {"x-request-id": "historical-http-503"}, b"unavailable"

        historical_gateway = QwenStageGateway(QwenChatCompletionsAdapter(
            api_key="test-key",
            transport=http_failure_transport,
        ))
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(X02ExecutionError) as http_caught:
                run_x02_v03(
                    make_x02_bundle(Path(temporary), 3),
                    historical_gateway,
                )
        self.assertEqual(http_caught.exception.stage, "MODEL_GATEWAY")
        self.assertEqual(http_caught.exception.code, "MODEL_REQUEST_FAILED")
        self.assertEqual(http_caught.exception.stage_runs, ())

    def test_v041_unicode_motifs_are_nfkc_casefolded_and_v03_stays_historical(self):
        gateway = ScriptedGateway(observation_overrides={
            0: {"motifs": [" 古镇 石板路 ", "ＭＡＲＫＥＴ", "cafe\u0301"]},
        })
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(temporary, 3, gateway)
        self.assertEqual(
            result["observations"][0]["motifs"],
            ["古镇_石板路", "market", "café"],
        )
        self.assertFalse(any(
            item["json_field_path"].startswith("$.observations[*].motifs")
            for item in result["observations"][0]["degraded_fields"]
        ))

        with tempfile.TemporaryDirectory() as temporary:
            historical = run_x02_v03(
                make_x02_bundle(Path(temporary), 3),
                ScriptedGateway(observation_overrides={
                    0: {"motifs": [" 古镇 石板路 ", "ＭＡＲＫＥＴ", "cafe\u0301"]},
                }),
            )
        self.assertEqual(historical["schema_version"], X02_V03_SCHEMA_VERSION)
        self.assertNotIn("古镇_石板路", historical["observations"][0]["motifs"])

    def test_v041_invalid_quality_provenance_cannot_masquerade_as_valid_floor(self):
        gateway = ScriptedGateway(observation_overrides={
            0: {"quality_score": "not-a-number"},
            1: {"quality_score": 0.35},
            2: {"quality_score": 0.349},
        })
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(temporary, 3, gateway)
        self.assertEqual(result["observations"][0]["quality_score"], 0.35)
        self.assertTrue(any(
            item["validation_rule_id"] == "X02V03_QUALITY_SCORE_INVALID"
            for item in result["observations"][0]["degraded_fields"]
        ))
        roles = {
            item["source_asset_id"]: item
            for item in result["decision_trace"]["observation_roles"]
        }
        invalid = roles[self._source_asset_id(result, 0)]
        exact_floor = roles[self._source_asset_id(result, 1)]
        below_floor = roles[self._source_asset_id(result, 2)]
        self.assertEqual(
            (invalid["role"], invalid["reason_code"]),
            ("CONTEXT_ONLY", "INVALID_PRESENTATION_QUALITY_PROVENANCE"),
        )
        self.assertEqual(
            (exact_floor["role"], exact_floor["reason_code"]),
            ("KEEP", "GROUNDED_CONTENT_OR_EVENT_EVIDENCE"),
        )
        self.assertEqual(
            (below_floor["role"], below_floor["reason_code"]),
            ("CONTEXT_ONLY", "BELOW_PRESENTATION_USABILITY_FLOOR"),
        )

    def test_v041_aha_membership_is_value_ranked_then_published_by_import_sequence(self):
        plan = {
            0: "HISTORIC_TOWN_WALK",
            1: "HISTORIC_TOWN_WALK",
            2: "HISTORIC_TOWN_WALK",
            3: "MARKET_VISIT",
            4: "CAFE_STOP",
            5: "HOME_LIFE",
            6: "CRAFT_SESSION",
        }
        overrides = {
            3: {
                "event_kind": "DISCOVERY",
                "event_salience": "MEDIUM",
                "support_grade": "MODERATE",
                "motifs": ["早市招牌"],
                "fact_text": "早市招牌出现在摊位前。",
            },
            4: {
                "quality_score": 0.61,
                "motifs": ["草莓甜点"],
                "fact_text": "草莓甜点摆上了桌。",
            },
            5: {
                "event_kind": "PLAYFUL_ANIMAL",
                "event_salience": "HIGH",
                "subject_codes": ["DOG"],
                "motifs": ["小狗飞盘"],
                "quality_score": 0.82,
                "fact_text": "小狗追着飞盘跑。",
            },
            6: {
                "event_kind": "RESULT",
                "event_salience": "HIGH",
                "motifs": ["手作完成"],
                "quality_score": 0.88,
                "fact_text": "手作作品已经完成。",
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(
                temporary,
                7,
                ScriptedGateway(plan, observation_overrides=overrides),
            )
        selection = result["decision_trace"]["aha_set_selection"]
        self.assertEqual(
            selection["algorithm"],
            "V04_1_AHA_LEXICOGRAPHIC_RELATION_AWARE_SET_SELECTION",
        )
        self.assertEqual(selection["search_contract"], "EVENT_AND_DISCOVERY_AHA_PATHS_V02")
        self.assertTrue(selection["membership_order_separate_from_output_order"])
        candidate_by_source = {
            item["source_asset_id"]: item["candidate_id"]
            for item in result["decision_trace"]["aha_candidates"]
            if item["validation_status"] == "PASSED"
        }
        early_medium_id = candidate_by_source[self._source_asset_id(result, 3)]
        later_high_ids = {
            candidate_by_source[self._source_asset_id(result, index)]
            for index in (4, 5, 6)
        }
        self.assertNotIn(early_medium_id, selection["selected_candidate_ids"])
        self.assertEqual(set(selection["selected_candidate_ids"]), later_high_ids)
        published_ids = [item["candidate_id"] for item in result["ahas"]]
        self.assertEqual(published_ids, [
            candidate_by_source[self._source_asset_id(result, index)]
            for index in (4, 5, 6)
        ])
        self.assertNotEqual(selection["ranked_candidate_ids"], published_ids)

    def test_v041_same_observation_alias_preserves_model_fact_scope(self):
        class SameObservationProposalGateway(ScriptedGateway):
            def _perception(self, context):
                output = super()._perception(context)
                for observation in output["observations"]:
                    if observation["event_kind"] == "FOOD_MOMENT":
                        observation["facts"][0]["text"] = "甜点摆上了桌。"
                        observation["facts"].append({
                            "text": "桌边还能看到一只杯子。",
                            "evidence_frame_ids": observation["facts"][0]["evidence_frame_ids"],
                            "support_grade": "MODERATE",
                        })
                return output

            def _structure(self, context):
                food = next(
                    item for item in context["observations"]
                    if item["event_kind"] == "FOOD_MOMENT"
                )
                return {
                    "storyline_proposals": [],
                    "aha_proposals": [{
                        "key": "model_food_peak",
                        "observation_id": food["observation_id"],
                        "event_fact_ids": [food["facts"][0]["fact_id"]],
                        "narrative_duty": "当前素材的独立事件",
                    }],
                }

        plan = {
            0: "HISTORIC_TOWN_WALK",
            1: "HISTORIC_TOWN_WALK",
            2: "HISTORIC_TOWN_WALK",
            3: "CAFE_STOP",
        }
        gateway = SameObservationProposalGateway(plan)
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(temporary, 4, gateway)
        self.assertEqual(len(result["ahas"]), 1)
        self.assertEqual(len(result["ahas"][0]["claims"]), 1)
        aliases = [
            item for item in result["decision_trace"]["aha_candidates"]
            if "DUPLICATE_AHA_EVENT" in item["reason_codes"]
        ]
        self.assertEqual(len(aliases), 1)
        writer_memory = next(
            memory
            for call in gateway.calls if call["stage"] == "S11_WRITER_ATTEMPT_1"
            for memory in call["context"]["memories"]
            if memory["memory_type"] == "AHA"
        )
        self.assertEqual(writer_memory["narrative_duty"], "当前素材的独立事件")
        self.assertEqual(len(writer_memory["facts"]), 1)
        candidate_id = result["ahas"][0]["candidate_id"]
        self.assertEqual(
            result["decision_trace"]["aha_set_selection"]["candidate_rank_inputs"][
                candidate_id
            ]["event_specificity"],
            1.0,
        )

    def test_v041_aha_capacity_rejection_is_not_reported_as_category_based_duplicate(self):
        # Existing interface fixture, not proof that its described events are
        # distinct. Category/proximity cannot supply the missing event evidence.
        plan = {
            0: "HISTORIC_TOWN_WALK",
            1: "HISTORIC_TOWN_WALK",
            2: "HISTORIC_TOWN_WALK",
            3: "HOME_LIFE",
            4: "HOME_LIFE",
            5: "CAFE_STOP",
            6: "CRAFT_SESSION",
        }
        overrides = {
            3: {
                "event_kind": "PLAYFUL_ANIMAL",
                "event_salience": "HIGH",
                "subject_codes": ["DOG"],
                "motifs": ["小狗飞盘"],
                "quality_score": 0.91,
                "fact_text": "小狗追着飞盘跑。",
            },
            4: {
                "event_kind": "PLAYFUL_ANIMAL",
                "event_salience": "HIGH",
                "subject_codes": ["DOG"],
                "motifs": ["小狗飞盘"],
                "quality_score": 0.89,
                "fact_text": "小狗追着飞盘跑。",
            },
            5: {
                "motifs": ["抹茶甜点"],
                "quality_score": 0.80,
                "fact_text": "抹茶甜点摆上了桌。",
            },
            6: {
                "event_kind": "RESULT",
                "event_salience": "HIGH",
                "motifs": ["手作完成"],
                "quality_score": 0.78,
                "fact_text": "手作作品已经完成。",
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(
                temporary,
                7,
                ScriptedGateway(plan, observation_overrides=overrides),
            )
        selection = result["decision_trace"]["aha_set_selection"]
        dog_source_ids = {
            self._source_asset_id(result, 3),
            self._source_asset_id(result, 4),
        }
        candidates = [
            item for item in result["decision_trace"]["aha_candidates"]
            if item.get("source_asset_id") in dog_source_ids
            and item["validation_status"] == "PASSED"
        ]
        self.assertEqual(len(candidates), 2)
        selected_dog_ids = {
            item["candidate_id"] for item in candidates
            if item["candidate_id"] in selection["selected_candidate_ids"]
        }
        self.assertEqual(len(selected_dog_ids), 1)
        self.assertEqual(len(selection["selected_candidate_ids"]), 3)
        relation = next(
            item for item in selection["pair_ledger"]
            if {item["candidate_a_id"], item["candidate_b_id"]}
            == {item["candidate_id"] for item in candidates}
        )
        self.assertEqual(relation["relation"], "NO_CONFLICT_EVIDENCE")
        self.assertEqual(relation["selection_effect"], "ALLOW_COSELECT")
        self.assertEqual(relation["same_memory_evidence"], [])
        self.assertEqual(relation["distinct_memory_evidence"], [])
        loser = next(
            item for item in candidates
            if item["candidate_id"] not in selected_dog_ids
        )
        self.assertNotIn("suppressed_by_candidate_id", loser)
        self.assertIn("AHA_PREVIEW_CAPACITY_REACHED", loser["reason_codes"])

    def test_v041_distinct_same_kind_events_are_not_removed_by_visual_similarity_alone(self):
        plan = {
            0: "HISTORIC_TOWN_WALK",
            1: "HISTORIC_TOWN_WALK",
            2: "HISTORIC_TOWN_WALK",
            3: "HOME_LIFE",
            4: "CRAFT_SESSION",
        }
        overrides = {
            3: {
                "event_kind": "DISCOVERY",
                "event_salience": "HIGH",
                "subject_codes": ["OTHER"],
                "motifs": ["石板路", "摊位"],
                "fact_text": "摊位旁出现一段石板路。",
            },
            4: {
                "event_kind": "DISCOVERY",
                "event_salience": "HIGH",
                "motifs": ["石板路", "溪流"],
                "fact_text": "手作旁能看到石板路和溪流。",
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(
                temporary,
                5,
                ScriptedGateway(plan, observation_overrides=overrides),
            )
        selection = result["decision_trace"]["aha_set_selection"]
        candidate_by_source = {
            item["source_asset_id"]: item["candidate_id"]
            for item in result["decision_trace"]["aha_candidates"]
            if item["validation_status"] == "PASSED"
        }
        expected = {
            candidate_by_source[self._source_asset_id(result, 3)],
            candidate_by_source[self._source_asset_id(result, 4)],
        }
        self.assertTrue(expected.issubset(set(selection["selected_candidate_ids"])))
        relation = next(
            item for item in selection["pair_ledger"]
            if {item["candidate_a_id"], item["candidate_b_id"]} == expected
        )
        self.assertEqual(relation["relation"], "NO_CONFLICT_EVIDENCE")
        self.assertEqual(relation["distinct_memory_evidence"], [])
        self.assertEqual(relation["selection_effect"], "ALLOW_COSELECT")

    def test_v041_writer_fallback_keeps_selected_candidate_peak_and_claim_plan(self):
        plan = {
            0: "HISTORIC_TOWN_WALK",
            1: "HISTORIC_TOWN_WALK",
            2: "HISTORIC_TOWN_WALK",
            3: "CAFE_STOP",
        }
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(
                temporary,
                4,
                MissingAhaReferenceGateway(
                    plan,
                    observation_overrides={3: {"fact_text": "甜点摆上了桌。"}},
                ),
            )
        selection = result["decision_trace"]["aha_set_selection"]
        self.assertEqual(len(selection["selected_candidate_ids"]), 1)
        selected_id = selection["selected_candidate_ids"][0]
        self.assertEqual(result["semantic_day_state"], "CHAPTER_DAY")
        self.assertEqual(result["delivery_state"], "READY_WITH_GROUNDED_COPY_FALLBACK")
        self.assertEqual(result["output_mode"], "CHAPTER_DAY")
        self.assertEqual([item["candidate_id"] for item in result["ahas"]], [selected_id])
        aha = result["ahas"][0]
        self.assertEqual(aha["surface_source"], "DETERMINISTIC_GROUNDED_FALLBACK")
        self.assertLessEqual(len(aha["story"].replace(" ", "")), 20)
        observation = next(
            item for item in result["observations"]
            if item["source_asset_id"] == aha["selected_media"][0]["source_asset_id"]
        )
        allowed_claim_ids = {item["fact_id"] for item in observation["facts"]}
        self.assertTrue({item["fact_id"] for item in aha["claims"]}.issubset(allowed_claim_ids))
        fallback_outcomes = [
            item for item in result["selected_memory_outcomes"]
            if item["surface_state"] == "DETERMINISTIC_FALLBACK_VERIFIED"
        ]
        self.assertEqual(len(fallback_outcomes), 1)
        self.assertEqual(fallback_outcomes[0]["visibility_state"], "VISIBLE_PREVIEW")
        self.assertEqual(
            result["decision_trace"]["counts"]["selected_aha_count_before_writer"],
            result["decision_trace"]["counts"]["published_preview_aha_count"],
        )
        schema = json.loads(X02_V041_PREVIEW_SCHEMA_PATH.read_text(encoding="utf-8"))
        assert_json_schema_instance(self, schema, result)
        assert_v041_cross_field_truth(self, result)


    def test_v041_long_complete_fact_fallback_is_retained_and_flagged(self):
        plan = {
            0: "HISTORIC_TOWN_WALK",
            1: "HISTORIC_TOWN_WALK",
            2: "HISTORIC_TOWN_WALK",
            3: "MARKET_VISIT",
        }
        overrides = {
            3: {
                "event_kind": "DISCOVERY",
                "event_salience": "HIGH",
                "fact_text": "摊位前摆着多种当地物件，后方还能看到招牌与经过的人群。",
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(
                temporary,
                4,
                MissingAhaReferenceGateway(
                    plan,
                    observation_overrides=overrides,
                ),
            )
        self.assertEqual(result["semantic_day_state"], "CHAPTER_DAY")
        self.assertEqual(len(result["ahas"]), 1)
        aha = result["ahas"][0]
        self.assertEqual(aha["story"], overrides[3]["fact_text"])
        outcome = next(
            item for item in result["selected_memory_outcomes"]
            if item["memory_type"] == "AHA"
        )
        self.assertEqual(outcome["surface_state"], "DETERMINISTIC_FALLBACK_VERIFIED")
        self.assertEqual(result["delivery_state"], "READY_WITH_GROUNDED_COPY_FALLBACK")
        audit = next(item for item in result["decision_trace"]["writer_items"]
                     if item["candidate_id"] == aha["candidate_id"]
                     and item.get("validation_scope") == "COMPLETE_FACT_COPY_FORMAT_AND_REFERENCES")
        self.assertTrue(audit["length_review_required"])
        self.assertEqual(audit["draft_text"], aha["story"])
        serialized = json.dumps(result["decision_trace"]["writer_items"], ensure_ascii=False)
        self.assertNotIn("摊位前摆着多种当地物件。", serialized)
        schema = json.loads(X02_V041_PREVIEW_SCHEMA_PATH.read_text(encoding="utf-8"))
        assert_json_schema_instance(self, schema, result)
        assert_v041_cross_field_truth(self, result)

    def test_v041_highlight_day_state_matches_selected_aha_and_public_result(self):
        overrides = {
            0: {
                "event_kind": "DISCOVERY",
                "event_salience": "HIGH",
                "motifs": ["窗边新发现"],
                "fact_text": "窗边新发现出现在桌面。",
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(
                temporary,
                1,
                ScriptedGateway({0: "HOME_LIFE"}, observation_overrides=overrides),
            )
        self.assertEqual(result["semantic_day_state"], "HIGHLIGHT_DAY")
        self.assertEqual(result["delivery_state"], "READY_PRIMARY_COPY")
        self.assertEqual(result["output_mode"], "HIGHLIGHT_DAY")
        self.assertEqual(result["chapters"], [])
        self.assertEqual(len(result["ahas"]), 1)
        schema = json.loads(X02_V041_PREVIEW_SCHEMA_PATH.read_text(encoding="utf-8"))
        assert_json_schema_instance(self, schema, result)
        assert_v041_cross_field_truth(self, result)

        invalid_two_aha_highlight = copy.deepcopy(result)
        invalid_two_aha_highlight["selected_memory_outcomes"].append(
            copy.deepcopy(result["selected_memory_outcomes"][0])
        )
        with self.assertRaises(AssertionError):
            assert_json_schema_instance(self, schema, invalid_two_aha_highlight)

    def test_v041_complete_day_with_only_blocked_copy_is_pipeline_blocked_not_empty(self):
        overrides = {
            0: {
                "event_kind": "DISCOVERY",
                "event_salience": "HIGH",
                "subject_codes": ["STREET_SCENE"],
                "motifs": ["摊位"],
                "fact_text": "摊位前摆着多种当地物件，后方还能看到招牌与经过的人群。",
            },
        }
        # State-contract probe: both copy providers return no usable output.
        # Length alone is no longer a valid way to manufacture this failure.
        with tempfile.TemporaryDirectory() as temporary, patch.object(
            x02_module, "_deterministic_writer_fallback", return_value=({"chapters": [], "ahas": []}, [])
        ):
            result = self._run_v041(
                temporary,
                1,
                MissingAhaReferenceGateway(
                    {0: "HOME_LIFE"},
                    observation_overrides=overrides,
                ),
            )
        self.assertEqual(result["coverage_status"], "COMPLETE")
        self.assertEqual(result["semantic_day_state"], "HIGHLIGHT_DAY")
        self.assertEqual(result["delivery_state"], "PIPELINE_BLOCKED")
        self.assertEqual(result["output_mode"], "PIPELINE_BLOCKED")
        self.assertEqual(result["chapters"], [])
        self.assertEqual(result["ahas"], [])
        schema = json.loads(X02_V041_PREVIEW_SCHEMA_PATH.read_text(encoding="utf-8"))
        assert_json_schema_instance(self, schema, result)
        assert_v041_cross_field_truth(self, result)

    def test_v041_empty_day_is_semantic_absence_not_pipeline_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(temporary, 2, ScriptedGateway())
        self.assertEqual(result["chapters"], [])
        self.assertEqual(result["ahas"], [])
        self.assertEqual(result["semantic_day_state"], "EMPTY_DAY")
        self.assertEqual(result["delivery_state"], "NO_GROUNDED_MEMORY")
        self.assertEqual(result["output_mode"], "EMPTY_DAY")
        self.assertEqual(result["selected_memory_outcomes"], [])
        schema = json.loads(X02_V041_PREVIEW_SCHEMA_PATH.read_text(encoding="utf-8"))
        assert_json_schema_instance(self, schema, result)
        assert_v041_cross_field_truth(self, result)







    def test_v041_real_pair_is_not_assumed_duplicate_from_import_order(self):
        fixture = Path(__file__).parent / "fixtures/codex_v1_48_aha_selection_real.json"
        record = json.loads(fixture.read_text(encoding="utf-8"))
        by_label = {
            record["candidate_material_labels"][candidate["candidate_id"]]: candidate
            for candidate in record["candidates"]
        }
        self.assertIsNone(x02_module._aha_pair_conflict(
            by_label["M13"], by_label["M14"], record["asset_order"],
        ))

    def test_v041_http_timeout_and_rate_errors_do_not_fan_out(self):
        for code in (
            "MODEL_HTTP_400", "MODEL_HTTP_401", "MODEL_HTTP_403",
            "MODEL_HTTP_404", "MODEL_HTTP_422", "MODEL_HTTP_429",
            "MODEL_HTTP_500", "MODEL_HTTP_503", "MODEL_TRANSPORT_TIMEOUT",
        ):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as temporary:
                gateway = PerceptionCodeFailureGateway(code)
                result = self._run_v041(temporary, 3, gateway)
                expected_attempts = (
                    [(0, 1, 2), (0, 1, 2)]
                    if code in {
                        "MODEL_HTTP_500", "MODEL_HTTP_503", "MODEL_TRANSPORT_TIMEOUT",
                    }
                    else [(0, 1, 2)]
                )
                self.assertEqual(gateway.perception_attempts, expected_attempts)
                self.assertEqual(result["coverage_status"], "PARTIAL_UNRESOLVED")
                self.assertEqual(len(result["unresolved_asset_ids"]), 3)
                attempts = result["decision_trace"]["perception_batching"]["attempts"]
                if len(expected_attempts) == 2:
                    self.assertEqual(attempts[0]["recovery_action"], "ORIGINAL_BATCH_RETRY")
                self.assertEqual(attempts[-1]["recovery_action"], "TERMINAL_UNRESOLVED")

    def test_v041_http_413_bisects_multi_but_does_not_retry_singleton(self):
        gateway = PerceptionCodeFailureGateway("MODEL_HTTP_413")
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(temporary, 3, gateway)
        self.assertEqual(
            gateway.perception_attempts,
            [(0, 1, 2), (0,), (1, 2), (1,), (2,)],
        )
        self.assertEqual(len(result["unresolved_asset_ids"]), 3)
        attempts = result["decision_trace"]["perception_batching"]["attempts"]
        self.assertEqual(sum(item["recovery_action"] == "BISECT" for item in attempts), 2)
        self.assertEqual(len(attempts), 5)

        singleton_gateway = PerceptionCodeFailureGateway("MODEL_HTTP_413")
        with tempfile.TemporaryDirectory() as temporary:
            singleton = self._run_v041(temporary, 1, singleton_gateway)
        self.assertEqual(singleton_gateway.perception_attempts, [(0,)])
        self.assertEqual(
            singleton["decision_trace"]["perception_batching"]["attempts"][0]["recovery_action"],
            "TERMINAL_UNRESOLVED",
        )

    def test_v041_single_asset_over_4mib_is_rejected_before_provider(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = make_x02_bundle(root, 1)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            frame = manifest["assets"][0]["frames"][0]
            frame_path = root / frame["relative_path"]
            frame_path.write_bytes(b"x" * (4 * 1024 * 1024 + 1))
            frame["sha256"] = sha256_file(frame_path)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            gateway = ScriptedGateway()
            result = x02_module.run_x02_v041(manifest_path, gateway)
        self.assertFalse(any(
            call["stage"].startswith("S04_PERCEPTION") for call in gateway.calls
        ))
        self.assertEqual(result["coverage_status"], "PARTIAL_UNRESOLVED")
        attempt = result["decision_trace"]["perception_batching"]["attempts"][0]
        self.assertEqual(attempt["status"], "REJECTED_PREFLIGHT")
        self.assertEqual(attempt["reason_code"], "EVIDENCE_BUDGET_EXCEEDED")
        self.assertFalse(attempt["provider_call_attempted"])


    def test_v041_truthy_unverified_capture_metadata_stays_sequence_only(self):
        gateway = ScriptedGateway()
        with tempfile.TemporaryDirectory() as temporary:
            manifest_path = make_x02_bundle(Path(temporary), 3)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for index, asset in enumerate(manifest["assets"]):
                asset["capture_time"] = "2026-08-31T%02d:00:00Z" % (9 + index)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = x02_module.run_x02_v041(manifest_path, gateway)
        structure_call = next(
            item for item in gateway.calls
            if item["stage"] == "S05_S07_STRUCTURE_PROPOSAL"
        )
        self.assertEqual(structure_call["context"]["sequence_basis"], "IMPORT_SEQUENCE_ONLY")
        self.assertIn(
            "no verified-time provenance",
            structure_call["context"]["sequence_semantics"],
        )
        self.assertEqual(result["timeline_basis"], "SYNTHETIC_SEQUENCE_ONLY")
        self.assertIsNone(result["timeline_date"])
        self.assertEqual(
            result["time_reliability"],
            {
                "capture_time_reliable": False,
                "interval_reliable": False,
                "timezone_reliable": False,
            },
        )

    def test_v041_runtime_rejects_attempt_and_evidence_partition_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(temporary, 4, ScriptedGateway())
        invalids = []
        duplicate_root_asset = copy.deepcopy(result)
        roots = duplicate_root_asset["decision_trace"]["perception_batching"]["attempts"]
        roots[1]["asset_ids"].append(roots[0]["asset_ids"][0])
        invalids.append(duplicate_root_asset)

        missing_parent = copy.deepcopy(result)
        attempt = missing_parent["decision_trace"]["perception_batching"]["attempts"][0]
        attempt["parent_attempt_id"] = "missing-parent"
        attempt["attempt_kind"] = "SPLIT_CHILD"
        invalids.append(missing_parent)

        frame_drift = copy.deepcopy(result)
        frame_drift["trace"]["evidence_frame_count"] += 1
        invalids.append(frame_drift)

        for invalid in invalids:
            with self.assertRaises(X02ContractError):
                x02_module._validate_v041_result_state(invalid)

        source_asset_ids = [
            item["source_asset_id"] for item in result["observations"]
        ]
        frame_ids = [
            item["frame_id"]
            for item in result["decision_trace"]["evidence_selection"]["selected"]
        ]
        with self.assertRaises(X02ContractError):
            x02_module._validate_v041_result_state(
                result,
                expected_asset_ids=list(reversed(source_asset_ids)),
                expected_evidence_frame_ids=frame_ids,
            )
        with self.assertRaises(X02ContractError):
            x02_module._validate_v041_result_state(
                result,
                expected_asset_ids=source_asset_ids,
                expected_evidence_frame_ids=list(reversed(frame_ids)),
            )

    def test_v041_186_asset_normal_run_stays_below_call_attempt_stop_loss(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(temporary, 186, ScriptedGateway())
        trace = result["trace"]
        self.assertEqual(trace["run_max_model_call_attempts"], 96)
        self.assertLess(trace["model_call_attempted_count"], 96)
        self.assertFalse(trace["model_call_circuit_breaker_tripped"])
        self.assertEqual(
            trace["model_call_attempted_count"],
            result["decision_trace"]["perception_batching"]["model_call_attempt_count"],
        )

    def test_v041_call_attempt_stop_loss_returns_unresolved_diagnostic_not_exception(self):
        class EmptyPerceptionGateway(ScriptedGateway):
            def _perception(self, context):
                return {"observations": []}

        gateway = EmptyPerceptionGateway()
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_v041(temporary, 240, gateway)
        self.assertEqual(result["coverage_status"], "PARTIAL_UNRESOLVED")
        self.assertEqual(result["semantic_day_state"], "UNRESOLVED_DAY")
        self.assertEqual(result["delivery_state"], "PIPELINE_BLOCKED")
        self.assertEqual(result["trace"]["model_call_attempted_count"], 96)
        self.assertTrue(result["trace"]["model_call_circuit_breaker_tripped"])
        self.assertEqual(len(result["unresolved_asset_ids"]), 240)
        batching = result["decision_trace"]["perception_batching"]
        self.assertEqual(batching["model_call_attempt_count"], 96)
        self.assertTrue(batching["circuit_breaker_tripped"])
        self.assertTrue(any(
            item["reason_code"] == "MODEL_CALL_CIRCUIT_BREAKER_OPEN"
            and not item["provider_call_attempted"]
            for item in batching["attempts"]
        ))
        s07 = next(
            item for item in result["decision_trace"]["stage_statuses"]
            if item["stage"] == "S07_CANDIDATE_GENERATION"
        )
        self.assertIn("MODEL_STRUCTURE_SKIPPED_CALL_CIRCUIT_BREAKER", s07["reason_codes"])

    def test_v03_result_and_stage_status_do_not_gain_v041_retry_or_call_fields(self):
        with tempfile.TemporaryDirectory() as temporary:
            historical = run_x02_v03(
                make_x02_bundle(Path(temporary), 3),
                ScriptedGateway(),
            )
        s04 = next(
            item for item in historical["decision_trace"]["stage_statuses"]
            if item["stage"] == "S04_OBSERVATION_LITE"
        )
        self.assertNotIn("PER_ASSET_FAILURE_ISOLATION", s04["reason_codes"])
        self.assertFalse(any("RETRY" in code or "SPLIT" in code for code in s04["reason_codes"]))
        self.assertNotIn("model_call_attempted_count", historical["trace"])
        self.assertNotIn("run_max_model_call_attempts", historical["trace"])
        self.assertTrue(all(
            "call_status" not in metric for metric in historical["trace"]["stage_metrics"]
        ))

    def test_v03_failed_run_audit_retains_historical_completed_call_shape(self):
        run = StageRun(
            stage="S04_PERCEPTION_BATCH_001",
            output={"failure": "TEST"},
            provider="test-provider",
            model="test-model",
            request_id="request-v03-failure",
            input_tokens=1,
            output_tokens=0,
            latency_seconds=0.001,
            model_frame_count=1,
            model_calls=1,
            pricing_currency="USD",
            input_rate_per_million=0.0,
            output_rate_per_million=0.0,
            native_currency_per_usd=1.0,
            pricing_basis="test",
            call_status="HTTP_FAILED",
        )
        error = X02ExecutionError(
            "historical V03 failure",
            stage=run.stage,
            code="MODEL_REQUEST_FAILED",
            stage_runs=[run],
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = make_x02_bundle(root / "bundle", 1)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            _, audit_path = _write_x02_failed_run_audit(
                root / "audits",
                manifest,
                error,
                0.0,
                1,
                audit_schema_version=X02_V03_FAILED_RUN_AUDIT_SCHEMA_VERSION,
            )
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
        self.assertNotIn("stage_call_attempts", audit)
        self.assertEqual(len(audit["completed_stage_calls"]), 1)
        self.assertNotIn("call_status", audit["completed_stage_calls"][0])


if __name__ == "__main__":
    unittest.main()

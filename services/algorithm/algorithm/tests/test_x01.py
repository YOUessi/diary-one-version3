import json
import http.client
import tempfile
import threading
import unittest
import uuid
from pathlib import Path
from unittest import mock

from diary_one_ci.bundle import (
    APP_LIBRARY_BUNDLE_VERSION,
    APP_LIBRARY_BUNDLE_VERSION_V03,
    load_app_library_bundle,
)
from diary_one_ci.core import sha256_file
from diary_one_ci.x01 import (
    EditorialModelAdapter,
    FixtureEditorialAdapter,
    ModelRun,
    OpenAIResponsesAdapter,
    QwenChatCompletionsAdapter,
    X01ContractError,
    X01ModelNotReady,
    X01PostModelContractError,
    _editorial_overlap,
    _editorial_tokens,
    run_x01,
)
from diary_one_ci.x01_server import (
    HUMAN_EVALUATION_SCHEMA_VERSION,
    RUN_SIDECAR_SCHEMA_VERSION,
    _assert_no_embedded_images,
    _assert_json_storage_safe,
    _macos_keychain_qwen_api_key,
    _model_not_ready_payload,
    _resolve_qwen_api_key,
    _validate_run_sidecar,
    _write_failed_run_audit,
    _write_run_audit,
    _write_run_sidecar,
    make_server,
)


def make_x01_bundle(root: Path) -> Path:
    session_id = "195d9278-0247-4ac0-bd3c-3acecda5af97"
    assets = []
    for index, kind in enumerate(("PHOTO", "VIDEO")):
        asset_uuid = uuid.uuid5(uuid.UUID(session_id), "asset:%d" % index)
        asset_id = "asset_" + str(asset_uuid)
        frames = []
        for offset_index, offset in enumerate((1500, 4500, 7500)):
            relative = Path("evidence") / asset_id / ("frame_%d.jpg" % offset)
            frame_path = root / relative
            frame_path.parent.mkdir(parents=True, exist_ok=True)
            frame_path.write_bytes(("jpeg-fixture-%d-%d" % (index, offset)).encode())
            frames.append({
                "frame_id": "frame_%s_%d" % (asset_uuid, offset),
                "canonical_offset_ms": offset,
                "source_timestamp_ms": None if kind == "PHOTO" else (offset_index + 1) * 500,
                "relative_path": str(relative),
                "sha256": sha256_file(frame_path),
                "width": 768,
                "height": 1024,
                "spatial_transform": "CENTER_CROP_ASPECT_FILL",
            })
        assets.append({
            "asset_id": asset_id,
            "media_kind": kind,
            "media_source": "PHOTO_LIBRARY_TEST",
            "original_file_extension": "jpg" if kind == "PHOTO" else "mov",
            "original_sha256": "%064x" % (index + 1),
            "original_bytes": 1_000 + index,
            "original_width": 4_032 if kind == "PHOTO" else 1_920,
            "original_height": 3_024 if kind == "PHOTO" else 1_080,
            "original_duration_ms": None if kind == "PHOTO" else 2_300,
            "capture_time": "2026-08-18T0%d:00:00Z" % (8 + index),
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
            "exported_at": "2026-08-18T12:00:00Z",
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
    path.write_text(json.dumps(manifest))
    return path


class EmptyEditorialAdapter(EditorialModelAdapter):
    provider = "test"
    model = "empty"

    @property
    def ready(self):
        return True

    def generate(self, bundle):
        base_run = FixtureEditorialAdapter().generate(bundle)
        fixture = base_run.output
        fixture["chapter_candidates"][0]["confidence"] = 0.2
        return ModelRun(
            fixture, self.provider, self.model, "empty-request", 0, 0, 0.01,
            len(base_run.selected_evidence), selected_evidence=base_run.selected_evidence,
        )


class VideoAhaAdapter(EditorialModelAdapter):
    provider = "test"
    model = "video-aha"

    @property
    def ready(self):
        return True

    def generate(self, bundle):
        base_run = FixtureEditorialAdapter().generate(bundle)
        fixture = base_run.output
        video_asset = bundle.manifest["assets"][1]
        video_moment = fixture["moments"][1]
        fixture["chapter_candidates"] = []
        fixture["aha_candidates"] = [{
            "key": "video_aha",
            "title": "测试高光",
            "time_label": "第2项",
            "story": "视频瞬间被保留。",
            "tags": [],
            "moment_keys": [video_moment["key"]],
            "hero_asset_id": video_asset["asset_id"],
            "confidence": 0.95,
            "evidence_frame_ids": [frame["frame_id"] for frame in video_asset["frames"]],
            "claims": [{
                "text": "视频素材中存在可见瞬间。",
                "claim_type": "OBSERVED",
                "evidence_frame_ids": [video_asset["frames"][0]["frame_id"]],
            }],
        }]
        return ModelRun(
            fixture, self.provider, self.model, "video-aha-request", 0, 0, 0.01,
            len(base_run.selected_evidence), selected_evidence=base_run.selected_evidence,
        )


class X01Tests(unittest.TestCase):
    @mock.patch.dict("os.environ", {}, clear=True)
    @mock.patch("diary_one_ci.x01_server._macos_keychain_qwen_api_key", return_value="keychain-test-key")
    def test_qwen_key_resolver_uses_macos_keychain_when_environment_is_absent(self, keychain_read):
        api_key, source = _resolve_qwen_api_key()
        self.assertEqual(api_key, "keychain-test-key")
        self.assertEqual(source, "macos_keychain")
        keychain_read.assert_called_once_with()

    def test_model_not_ready_payload_is_rendered_without_runtime_formatting_error(self):
        payload = _model_not_ready_payload(QwenChatCompletionsAdapter(api_key=""))
        self.assertEqual(payload["error"], "model_not_ready")
        self.assertIn("DASHSCOPE_API_KEY", payload["message"])
        self.assertIn("No fixture fallback", payload["message"])

    @mock.patch("diary_one_ci.x01_server.getpass.getuser", return_value="diary-user")
    @mock.patch("diary_one_ci.x01_server.sys.platform", "darwin")
    @mock.patch("diary_one_ci.x01_server.subprocess.run")
    def test_macos_keychain_reader_never_requests_visible_output(self, run, getuser):
        run.return_value = mock.Mock(returncode=0, stdout="secret-test-key\n")
        self.assertEqual(_macos_keychain_qwen_api_key(), "secret-test-key")
        command = run.call_args.args[0]
        self.assertEqual(command[-1], "-w")
        self.assertIn("DiaryOne DashScope API Key", command)
        self.assertEqual(run.call_args.kwargs["stderr"], __import__("subprocess").DEVNULL)

    def test_fixture_contract_maps_back_to_app_assets_without_originals(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = make_x01_bundle(Path(tmp))
            result = run_x01(manifest, FixtureEditorialAdapter())
            source = json.loads(manifest.read_text())
            expected_ids = {asset["asset_id"].removeprefix("asset_") for asset in source["assets"]}
            self.assertEqual(result["schema_version"], "DIARY_ONE_X01_PREVIEW_V01")
            self.assertEqual(result["output_mode"], "CHAPTER_DAY")
            self.assertFalse(result["leaderboard_eligible"])
            self.assertTrue(result["experimental"])
            self.assertEqual({moment["asset_id"] for moment in result["moments"]}, expected_ids)
            self.assertEqual(result["trace"]["originals_uploaded"], 0)
            self.assertEqual(result["trace"]["model_calls"], 0)
            self.assertEqual(result["trace"]["pricing"]["basis"], "fixture-zero-cost")
            self.assertFalse(result["decision_trace"]["contains_hidden_reasoning"])
            self.assertEqual(
                result["decision_trace"]["trace_type"], "AUDITABLE_DECISION_EVIDENCE"
            )
            self.assertEqual(
                [metric["stage"] for metric in result["trace"]["stage_metrics"]],
                [
                    "BUNDLE_LOAD",
                    "EDITORIAL_MODEL_BRIDGE",
                    "DETERMINISTIC_VALIDATION_SELECTION",
                ],
            )
            self.assertTrue(all(
                metric["model_calls"] == 0 and metric["input_tokens"] == 0
                and metric["output_tokens"] == 0 and metric["estimated_cost_usd"] == 0
                for metric in result["trace"]["stage_metrics"]
                if metric["stage"] != "EDITORIAL_MODEL_BRIDGE"
            ))
            self.assertNotIn("original_sha256", json.dumps(result))

    def test_low_confidence_candidate_yields_empty_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_x01(make_x01_bundle(Path(tmp)), EmptyEditorialAdapter())
            self.assertEqual(result["output_mode"], "EMPTY_DAY")
            self.assertEqual(result["chapters"], [])
            self.assertEqual(result["ahas"], [])
            decision = result["decision_trace"]["chapter_candidates"][0]
            self.assertEqual(decision["validation_status"], "REJECTED")
            self.assertEqual(decision["selection_status"], "NOT_ELIGIBLE")
            self.assertEqual(decision["reason_code"], "BELOW_CONFIDENCE_THRESHOLD")
            self.assertEqual(decision["reason_codes"], ["BELOW_CONFIDENCE_THRESHOLD"])

    def test_video_can_supply_the_single_visible_aha_media(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_x01(make_x01_bundle(Path(tmp)), VideoAhaAdapter())
            self.assertEqual(result["output_mode"], "HIGHLIGHT_DAY")
            self.assertEqual(len(result["ahas"]), 1)
            self.assertEqual(len(result["ahas"][0]["moment_ids"]), 1)

    def test_candidate_ledger_records_validation_and_selection_reasons_without_pending_entries(self):
        class LedgerAdapter(EditorialModelAdapter):
            provider = "test"
            model = "ledger"

            @property
            def ready(self):
                return True

            def generate(self, bundle):
                base_run = FixtureEditorialAdapter().generate(bundle)
                output = base_run.output
                selected = output["chapter_candidates"][0]
                selected["key"] = "selected"
                selected["confidence"] = 0.99
                overlap = json.loads(json.dumps(selected))
                overlap["key"] = "overlap"
                overlap["title"] = "重叠候选"
                overlap["confidence"] = 0.90
                invalid_tag = json.loads(json.dumps(selected))
                invalid_tag["key"] = "invalid_tag"
                invalid_tag["title"] = "标签异常"
                invalid_tag["tags"] = ["FREE_FORM.NOT_ALLOWED"]
                first_asset = bundle.manifest["assets"][0]
                first_moment = output["moments"][0]
                output["chapter_candidates"] = [selected, overlap, invalid_tag]
                output["aha_candidates"] = [{
                    "key": "chapter_owned_aha",
                    "title": "同源高光",
                    "time_label": "第1项",
                    "story": "同一素材再次出现。",
                    "tags": [],
                    "moment_keys": [first_moment["key"]],
                    "hero_asset_id": first_asset["asset_id"],
                    "confidence": 0.95,
                    "evidence_frame_ids": [first_moment["evidence_frame_ids"][0]],
                    "claims": [{
                        "text": "素材可见。",
                        "claim_type": "OBSERVED",
                        "evidence_frame_ids": [first_moment["evidence_frame_ids"][0]],
                    }],
                }]
                return ModelRun(
                    output, self.provider, self.model, "ledger-request", 0, 0, 0.01,
                    len(base_run.selected_evidence), selected_evidence=base_run.selected_evidence,
                )

        with tempfile.TemporaryDirectory() as tmp:
            result = run_x01(make_x01_bundle(Path(tmp)), LedgerAdapter())
            chapters = result["decision_trace"]["chapter_candidates"]
            ahas = result["decision_trace"]["aha_candidates"]
            self.assertEqual(chapters[0]["selection_status"], "SELECTED")
            self.assertEqual(
                chapters[0]["reason_code"], "SELECTED_BY_CONFIDENCE_AND_TIMELINE"
            )
            self.assertEqual(chapters[1]["selection_status"], "NOT_SELECTED")
            self.assertEqual(
                chapters[1]["reason_code"], "ASSET_OVERLAP_WITH_SELECTED_CHAPTER"
            )
            self.assertEqual(chapters[2]["validation_status"], "REJECTED")
            self.assertEqual(chapters[2]["reason_code"], "UNKNOWN_CANONICAL_TAG")
            self.assertEqual(ahas[0]["selection_status"], "NOT_SELECTED")
            self.assertEqual(
                ahas[0]["reason_code"], "CORE_ASSET_ALREADY_OWNED_BY_CHAPTER"
            )
            self.assertFalse(any(
                entry["validation_status"] == "PENDING" or entry["selection_status"] == "PENDING"
                for entry in chapters + ahas
            ))

    def test_moment_candidate_ledger_records_materialized_superseded_and_rejected_inputs(self):
        class MomentLedgerAdapter(EditorialModelAdapter):
            provider = "test"
            model = "moment-ledger"

            @property
            def ready(self):
                return True

            def generate(self, bundle):
                base_run = FixtureEditorialAdapter().generate(bundle)
                output = base_run.output
                first = output["moments"][0]
                first["confidence"] = 0.80
                higher = json.loads(json.dumps(first))
                higher["key"] = "higher"
                higher["caption"] = "更高置信候选"
                higher["confidence"] = 0.95
                low = json.loads(json.dumps(first))
                low["key"] = "low"
                low["confidence"] = 0.20
                invalid_frame = json.loads(json.dumps(first))
                invalid_frame["key"] = "invalid_frame"
                invalid_frame["evidence_frame_ids"] = ["frame_missing"]
                not_presented = json.loads(json.dumps(first))
                not_presented["key"] = "not_presented"
                not_presented["evidence_frame_ids"] = [
                    bundle.manifest["assets"][0]["frames"][0]["frame_id"]
                ]
                unknown_asset = json.loads(json.dumps(first))
                unknown_asset["key"] = "unknown_asset"
                unknown_asset["asset_ids"] = ["asset_00000000-0000-0000-0000-000000000000"]
                output["moments"] = [
                    first,
                    higher,
                    low,
                    invalid_frame,
                    not_presented,
                    unknown_asset,
                    output["moments"][1],
                ]
                output["chapter_candidates"] = []
                output["aha_candidates"] = []
                return ModelRun(
                    output, self.provider, self.model, "moment-ledger-request", 0, 0, 0.01,
                    len(base_run.selected_evidence), selected_evidence=base_run.selected_evidence,
                )

        with tempfile.TemporaryDirectory() as tmp:
            result = run_x01(make_x01_bundle(Path(tmp)), MomentLedgerAdapter())
            ledger = {
                entry["source_key"]: entry
                for entry in result["decision_trace"]["moment_candidates"]
            }
            self.assertEqual(ledger["higher"]["materialization_status"], "MATERIALIZED")
            self.assertEqual(ledger["higher"]["reason_code"], "MATERIALIZED")
            self.assertEqual(ledger["fixture_moment_0"]["materialization_status"], "NOT_MATERIALIZED")
            self.assertEqual(
                ledger["fixture_moment_0"]["reason_code"],
                "SUPERSEDED_BY_HIGHER_CONFIDENCE",
            )
            self.assertIn("LOW_CONFIDENCE", ledger["fixture_moment_0"]["reason_codes"])
            self.assertEqual(ledger["low"]["validation_status"], "PASSED")
            self.assertEqual(ledger["low"]["materialization_status"], "NOT_MATERIALIZED")
            self.assertEqual(
                ledger["low"]["reason_code"], "SUPERSEDED_BY_HIGHER_CONFIDENCE"
            )
            self.assertIn("LOW_CONFIDENCE", ledger["low"]["reason_codes"])
            self.assertEqual(ledger["invalid_frame"]["reason_code"], "INVALID_FRAME")
            self.assertEqual(
                ledger["not_presented"]["reason_code"],
                "EVIDENCE_FRAME_NOT_PRESENTED_TO_MODEL",
            )
            self.assertEqual(ledger["unknown_asset"]["reason_code"], "UNKNOWN_ASSET")
            self.assertEqual(
                result["decision_trace"]["counts"]["model_moment_count"], 7
            )
            self.assertEqual(
                result["decision_trace"]["counts"]["validated_moment_candidate_count"], 4
            )

    def test_model_outputs_cannot_cite_bundle_frames_that_were_not_presented(self):
        class UnpresentedCandidateAdapter(EditorialModelAdapter):
            provider = "test"
            model = "unpresented-candidate"

            @property
            def ready(self):
                return True

            def generate(self, bundle):
                base_run = FixtureEditorialAdapter().generate(bundle)
                output = base_run.output
                unpresented = bundle.manifest["assets"][0]["frames"][0]["frame_id"]
                chapter = output["chapter_candidates"][0]
                chapter["evidence_frame_ids"] = [unpresented]
                chapter["claims"][0]["evidence_frame_ids"] = [unpresented]
                return ModelRun(
                    output, self.provider, self.model, "unpresented-request", 0, 0, 0.01,
                    len(base_run.selected_evidence), selected_evidence=base_run.selected_evidence,
                )

        class UnpresentedObservationAdapter(UnpresentedCandidateAdapter):
            model = "unpresented-observation"

            def generate(self, bundle):
                base_run = FixtureEditorialAdapter().generate(bundle)
                output = base_run.output
                output["observations"][0]["evidence_frame_ids"] = [
                    bundle.manifest["assets"][0]["frames"][0]["frame_id"]
                ]
                return ModelRun(
                    output, self.provider, self.model, "unpresented-observation-request",
                    0, 0, 0.01, len(base_run.selected_evidence),
                    selected_evidence=base_run.selected_evidence,
                )

        with tempfile.TemporaryDirectory() as tmp:
            manifest = make_x01_bundle(Path(tmp))
            result = run_x01(manifest, UnpresentedCandidateAdapter())
            self.assertEqual(result["chapters"], [])
            self.assertEqual(
                result["decision_trace"]["chapter_candidates"][0]["reason_code"],
                "EVIDENCE_FRAME_NOT_PRESENTED_TO_MODEL",
            )
            observation_result = run_x01(manifest, UnpresentedObservationAdapter())
            self.assertEqual(len(observation_result["observations"]), 1)
            observation_ledger = observation_result["decision_trace"]["observation_candidates"]
            self.assertEqual(observation_ledger[0]["validation_status"], "REJECTED")
            self.assertEqual(
                observation_ledger[0]["reason_code"],
                "EVIDENCE_FRAME_NOT_PRESENTED_TO_MODEL",
            )
            self.assertEqual(
                observation_ledger[0]["invalid_frame_ids"],
                [json.loads(manifest.read_text())["assets"][0]["frames"][0]["frame_id"]],
            )

    def test_editorial_candidate_cannot_silently_rebind_a_superseded_moment_key(self):
        class SupersededMomentReferenceAdapter(EditorialModelAdapter):
            provider = "test"
            model = "superseded-moment-reference"

            @property
            def ready(self):
                return True

            def generate(self, bundle):
                base_run = FixtureEditorialAdapter().generate(bundle)
                output = base_run.output
                losing = output["moments"][0]
                losing["confidence"] = 0.80
                winner = json.loads(json.dumps(losing))
                winner["key"] = "winner_for_same_asset"
                winner["confidence"] = 0.95
                output["moments"].insert(1, winner)
                # The Chapter intentionally keeps the losing source key. It must
                # not be rebound to winner_for_same_asset merely because asset_id matches.
                output["chapter_candidates"][0]["moment_keys"] = [
                    losing["key"],
                    output["moments"][2]["key"],
                ]
                return ModelRun(
                    output, self.provider, self.model, "superseded-reference-request",
                    0, 0, 0.01, len(base_run.selected_evidence),
                    selected_evidence=base_run.selected_evidence,
                )

        with tempfile.TemporaryDirectory() as tmp:
            result = run_x01(
                make_x01_bundle(Path(tmp)), SupersededMomentReferenceAdapter()
            )
            self.assertEqual(result["chapters"], [])
            self.assertEqual(
                result["decision_trace"]["chapter_candidates"][0]["reason_code"],
                "MOMENT_NOT_MATERIALIZED",
            )

    def test_chinese_story_overlap_flags_same_climax_but_not_distinct_dessert(self):
        birthday = _editorial_tokens({
            "title": "生日聚会",
            "story": "大家围着蛋糕，一起吹灭了蜡烛。",
        })
        candle_aha = _editorial_tokens({
            "title": "吹蜡烛",
            "story": "蜡烛一起被吹灭。",
        })
        dessert_aha = _editorial_tokens({
            "title": "甜品一刻",
            "story": "奶油沾到了鼻尖。",
        })
        self.assertGreaterEqual(_editorial_overlap(birthday, candle_aha), 0.35)
        self.assertLess(_editorial_overlap(birthday, dessert_aha), 0.35)

    def test_openai_adapter_uses_image_input_and_strict_structured_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = make_x01_bundle(Path(tmp))
            imported = load_app_library_bundle(manifest)
            fixture_output = FixtureEditorialAdapter().generate(imported).output
            captured = {}

            def transport(url, headers, body, timeout):
                captured["url"] = url
                captured["headers"] = headers
                captured["body"] = json.loads(body)
                payload = {
                    "id": "resp_test",
                    "output_text": json.dumps(fixture_output),
                    "usage": {"input_tokens": 120, "output_tokens": 80},
                }
                return 200, {"x-request-id": "request_test"}, json.dumps(payload).encode()

            adapter = OpenAIResponsesAdapter(
                api_key="server-only-test-key", model="gpt-5.6-luna", transport=transport
            )
            result = run_x01(manifest, adapter)
            request = captured["body"]
            content = request["input"][0]["content"]
            self.assertEqual(captured["url"], "https://api.openai.com/v1/responses")
            self.assertTrue(request["text"]["format"]["strict"])
            self.assertEqual(request["text"]["format"]["type"], "json_schema")
            self.assertEqual(len([part for part in content if part["type"] == "input_image"]), 4)
            self.assertTrue(all(part["image_url"].startswith("data:image/jpeg;base64,") for part in content if part["type"] == "input_image"))
            self.assertEqual(result["trace"]["provider"], "openai")
            self.assertEqual(result["trace"]["request_id"], "request_test")
            self.assertEqual(result["trace"]["model_frame_count"], 4)
            self.assertEqual(result["trace"]["model_calls"], 1)
            self.assertEqual(result["trace"]["pricing"]["currency"], "USD")
            self.assertGreater(result["trace"]["estimated_cost_usd"], 0)
            bridge = next(
                metric for metric in result["trace"]["stage_metrics"]
                if metric["stage"] == "EDITORIAL_MODEL_BRIDGE"
            )
            self.assertEqual(bridge["model_calls"], 1)
            self.assertEqual(bridge["input_tokens"], 120)
            self.assertEqual(bridge["output_tokens"], 80)
            self.assertEqual(bridge["estimated_cost_usd"], result["trace"]["estimated_cost_usd"])

    def test_qwen_adapter_uses_chat_image_input_json_mode_and_local_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = make_x01_bundle(Path(tmp))
            imported = load_app_library_bundle(manifest)
            fixture_output = FixtureEditorialAdapter().generate(imported).output
            captured = {}

            def transport(url, headers, body, timeout):
                captured["url"] = url
                captured["headers"] = headers
                captured["body"] = json.loads(body)
                payload = {
                    "id": "chatcmpl_qwen_test",
                    "choices": [{"message": {"role": "assistant", "content": json.dumps(fixture_output)}}],
                    "usage": {"prompt_tokens": 120, "completion_tokens": 80},
                }
                return 200, {"x-dashscope-request-id": "qwen-request-test"}, json.dumps(payload).encode()

            adapter = QwenChatCompletionsAdapter(
                api_key="server-only-test-key",
                model="qwen3-vl-flash-2026-01-22",
                base_url="https://workspace.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
                transport=transport,
            )
            result = run_x01(manifest, adapter)
            request = captured["body"]
            content = request["messages"][0]["content"]
            images = [part for part in content if part["type"] == "image_url"]
            self.assertEqual(
                captured["url"],
                "https://workspace.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions",
            )
            self.assertEqual(request["response_format"], {"type": "json_object"})
            self.assertFalse(request["enable_thinking"])
            self.assertEqual(len(images), 4)
            self.assertTrue(all(
                part["image_url"]["url"].startswith("data:image/jpeg;base64,") for part in images
            ))
            self.assertIn("JSON Schema", content[0]["text"])
            self.assertIn("chapter_candidates", content[0]["text"])
            self.assertEqual(result["trace"]["provider"], "alibaba_model_studio")
            self.assertEqual(result["trace"]["request_id"], "qwen-request-test")
            self.assertEqual(result["trace"]["model_calls"], 1)
            self.assertEqual(result["trace"]["pricing"]["currency"], "CNY")
            self.assertEqual(result["trace"]["pricing"]["input_rate_per_million"], 0.15)
            self.assertGreater(result["trace"]["estimated_cost_usd"], 0)

    def test_qwen_adapter_refuses_silent_fixture_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            imported = load_app_library_bundle(make_x01_bundle(Path(tmp)))
            with self.assertRaises(X01ModelNotReady):
                QwenChatCompletionsAdapter(api_key="").generate(imported)

    def test_openai_adapter_refuses_silent_fixture_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            imported = load_app_library_bundle(make_x01_bundle(Path(tmp)))
            with self.assertRaises(X01ModelNotReady):
                OpenAIResponsesAdapter(api_key="").generate(imported)

    def test_image_free_run_audit_and_flexible_v02_sidecars_are_atomic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = make_x01_bundle(root / "bundle")
            manifest = json.loads(manifest_path.read_text())
            result = run_x01(manifest_path, FixtureEditorialAdapter())
            audit_root = root / "audits"
            audit_path = _write_run_audit(
                audit_root,
                manifest,
                result,
                materialization_duration_ms=12.5,
                x01_run_duration_ms=33.25,
                request_body_bytes=4_096,
            )
            audit = json.loads(audit_path.read_text())
            self.assertEqual(audit["session_id"], result["session_id"])
            self.assertFalse(audit["image_payloads_included"])
            self.assertEqual(audit["manifest"], manifest)
            self.assertEqual(audit["result"], result)
            self.assertEqual(audit["run_id"], result["trace"]["run_id"])
            self.assertTrue(
                (audit_path.parent / "runs" / (audit["run_id"] + ".run_audit.json")).is_file()
            )
            self.assertNotIn("data:image/", audit_path.read_text())
            self.assertFalse(any(path.suffix == ".tmp" for path in audit_path.parent.iterdir()))

            evaluation_id = str(uuid.uuid4())
            sidecar = {
                "schema_version": RUN_SIDECAR_SCHEMA_VERSION,
                "session_id": result["session_id"],
                "client_trace": {"stages": [{"name": "FRAME_EXTRACTION", "duration_ms": 18}]},
                "human_review": {
                    "schema_version": HUMAN_EVALUATION_SCHEMA_VERSION,
                    "session_id": result["session_id"],
                    "evaluation_id": evaluation_id,
                    "revision": 0,
                    "run_id": result["trace"]["run_id"],
                    "bundle_manifest_sha256": result["bundle_manifest_sha256"],
                    "pipeline_version": result["trace"]["pipeline_version"],
                    "request_id": result["trace"]["request_id"],
                    "saved_at": "2026-08-31T12:00:00Z",
                    "global": {"rating": "NEEDS_WORK"},
                    "reviews": [{
                        "targetType": "COPY_FIELD",
                        "targetId": result["chapters"][0]["id"],
                        "parentEditorialId": result["chapters"][0]["id"],
                        "aspect": "STORY",
                        "verdict": "REVISE",
                        "issueCodes": ["COPY_STIFF"],
                        "assetIds": [],
                        "frameIds": [],
                        "relatedEntityIds": [],
                        "suggestion": "表达更自然。",
                        "notes": "保留现场感。",
                    }],
                    "future_extension": {"allowed": True},
                },
            }
            session_id, client_trace, human_review = _validate_run_sidecar(sidecar)
            self.assertEqual(session_id, result["session_id"])
            self.assertIsInstance(client_trace, dict)
            self.assertIsInstance(human_review, dict)
            saved_session, saved = _write_run_sidecar(audit_root, sidecar)
            self.assertEqual(saved_session, result["session_id"])
            self.assertEqual(saved, ["client_trace", "human_review"])
            session_root = audit_root / result["session_id"]
            self.assertEqual(
                json.loads((session_root / "human_review.json").read_text())["human_review"],
                sidecar["human_review"],
            )
            revision_path = session_root / "reviews" / evaluation_id / "0.human_review.json"
            self.assertTrue(revision_path.is_file())
            recorded_review = json.loads(revision_path.read_text())
            self.assertEqual(recorded_review["bound_run"]["run_id"], result["trace"]["run_id"])

            # Exact retry is idempotent; a different payload at the same revision is not.
            self.assertEqual(_write_run_sidecar(audit_root, sidecar)[1], ["client_trace", "human_review"])
            conflicting = json.loads(json.dumps(sidecar))
            conflicting["human_review"]["global"]["rating"] = "PASS"
            with self.assertRaisesRegex(ValueError, "conflicts"):
                _write_run_sidecar(audit_root, conflicting)

            revision_one = json.loads(json.dumps(sidecar))
            revision_one["client_trace"] = None
            revision_one["human_review"]["revision"] = 1
            revision_one["human_review"]["global"]["rating"] = "PASS"
            _write_run_sidecar(audit_root, revision_one)
            self.assertTrue(
                (session_root / "reviews" / evaluation_id / "1.human_review.json").is_file()
            )
            with self.assertRaisesRegex(ValueError, "stale"):
                _write_run_sidecar(audit_root, sidecar)

    def test_sidecar_rejects_session_mismatch_and_embedded_run_audit_image(self):
        session_id = str(uuid.uuid4())
        with self.assertRaisesRegex(ValueError, "must match"):
            _validate_run_sidecar({
                "schema_version": RUN_SIDECAR_SCHEMA_VERSION,
                "session_id": session_id,
                "human_review": {
                    "schema_version": HUMAN_EVALUATION_SCHEMA_VERSION,
                    "session_id": str(uuid.uuid4()),
                    "evaluation_id": str(uuid.uuid4()),
                    "revision": 0,
                },
            })
        with self.assertRaisesRegex(ValueError, "must not contain embedded image"):
            _assert_no_embedded_images({"preview": "data:image/jpeg;base64,unsafe"})
        with self.assertRaisesRegex(ValueError, "must not contain embedded image"):
            _validate_run_sidecar({
                "schema_version": RUN_SIDECAR_SCHEMA_VERSION,
                "session_id": session_id,
                "client_trace": {"preview": "data:image/jpeg;base64,unsafe"},
            })
        with self.assertRaisesRegex(ValueError, "numbers must be finite"):
            _assert_json_storage_safe({"duration_ms": float("nan")})

    def test_post_model_contract_failure_preserves_usage_cost_and_raw_output_audit(self):
        class InvalidOutputAdapter(EditorialModelAdapter):
            provider = "test"
            model = "invalid-output"

            @property
            def ready(self):
                return True

            def generate(self, bundle):
                selected = FixtureEditorialAdapter().generate(bundle).selected_evidence
                return ModelRun(
                    output={"observations": [], "moments": [], "chapter_candidates": "invalid", "aha_candidates": []},
                    provider=self.provider,
                    model=self.model,
                    request_id="failed-contract-request",
                    input_tokens=12_000,
                    output_tokens=3_000,
                    latency_seconds=1.25,
                    model_frame_count=len(selected),
                    model_calls=1,
                    pricing_currency="CNY",
                    input_rate_per_million=0.15,
                    output_rate_per_million=1.5,
                    native_currency_per_usd=7.2,
                    pricing_basis="test-rate",
                    selected_evidence=selected,
                )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = make_x01_bundle(root / "bundle")
            with self.assertRaises(X01PostModelContractError) as raised:
                run_x01(manifest_path, InvalidOutputAdapter())
            failure_id, latest = _write_failed_run_audit(
                root / "audits",
                json.loads(manifest_path.read_text()),
                raised.exception,
                materialization_duration_ms=4.5,
                request_body_bytes=8_192,
            )
            audit = json.loads(latest.read_text())
            self.assertEqual(audit["failure_id"], failure_id)
            self.assertEqual(audit["failure"]["code"], "POST_MODEL_CONTRACT_VIOLATION")
            self.assertEqual(audit["model_run"]["input_tokens"], 12_000)
            self.assertEqual(audit["model_run"]["output_tokens"], 3_000)
            self.assertEqual(
                audit["model_run"]["raw_model_output"]["chapter_candidates"],
                "invalid",
            )
            self.assertGreater(audit["model_run"]["pricing"]["estimated_cost_usd"], 0)
            self.assertTrue(
                (latest.parent / "failures" / (failure_id + ".failed_run_audit.json")).is_file()
            )
            self.assertNotIn("data:image/", latest.read_text())

    def test_human_review_requires_every_exact_run_binding_field(self):
        session_id = str(uuid.uuid4())
        review = {
            "schema_version": HUMAN_EVALUATION_SCHEMA_VERSION,
            "session_id": session_id,
            "evaluation_id": str(uuid.uuid4()),
            "revision": 0,
            "run_id": str(uuid.uuid4()),
            "bundle_manifest_sha256": "a" * 64,
            "pipeline_version": "X01_DIARY_RESEARCH_PREVIEW_V01",
            "request_id": "request-required-fields",
        }
        for field in (
            "run_id",
            "bundle_manifest_sha256",
            "pipeline_version",
            "request_id",
        ):
            with self.subTest(field=field):
                incomplete = json.loads(json.dumps(review))
                incomplete.pop(field)
                with self.assertRaisesRegex(ValueError, field):
                    _validate_run_sidecar({
                        "schema_version": RUN_SIDECAR_SCHEMA_VERSION,
                        "session_id": session_id,
                        "human_review": incomplete,
                    })
        for field in ("bundle_manifest_sha256", "pipeline_version", "request_id"):
            with self.subTest(empty_field=field):
                empty = json.loads(json.dumps(review))
                empty[field] = ""
                with self.assertRaisesRegex(ValueError, field):
                    _validate_run_sidecar({
                        "schema_version": RUN_SIDECAR_SCHEMA_VERSION,
                        "session_id": session_id,
                        "human_review": empty,
                    })

    def test_human_review_run_id_binds_archived_run_and_rejects_fingerprint_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = make_x01_bundle(root / "bundle")
            manifest = json.loads(manifest_path.read_text())
            audit_root = root / "audits"
            first = run_x01(manifest_path, FixtureEditorialAdapter())
            first["trace"]["request_id"] = "request-first"
            _write_run_audit(audit_root, manifest, first, 1.0, 2.0, 100)
            second = run_x01(manifest_path, FixtureEditorialAdapter())
            second["trace"]["request_id"] = "request-second"
            _write_run_audit(audit_root, manifest, second, 1.0, 2.0, 100)
            self.assertNotEqual(first["trace"]["run_id"], second["trace"]["run_id"])

            review = {
                "schema_version": HUMAN_EVALUATION_SCHEMA_VERSION,
                "session_id": first["session_id"],
                "evaluation_id": str(uuid.uuid4()),
                "revision": 0,
                "run_id": first["trace"]["run_id"],
                "bundle_manifest_sha256": first["bundle_manifest_sha256"],
                "pipeline_version": first["trace"]["pipeline_version"],
                "request_id": "request-first",
                "global": {},
                "reviews": [],
            }
            sidecar = {
                "schema_version": RUN_SIDECAR_SCHEMA_VERSION,
                "session_id": first["session_id"],
                "human_review": review,
            }
            _write_run_sidecar(audit_root, sidecar)
            latest_review = json.loads(
                (audit_root / first["session_id"] / "human_review.json").read_text()
            )
            self.assertEqual(latest_review["bound_run"]["run_id"], first["trace"]["run_id"])
            self.assertEqual(latest_review["bound_run"]["request_id"], "request-first")

            mismatched = json.loads(json.dumps(sidecar))
            mismatched["human_review"]["evaluation_id"] = str(uuid.uuid4())
            mismatched["human_review"]["request_id"] = "request-second"
            with self.assertRaisesRegex(ValueError, "request_id does not match"):
                _write_run_sidecar(audit_root, mismatched)

            with self.assertRaisesRegex(
                ValueError,
                "sidecar route expects pipeline_version X02_STAGED_REAL_MEDIA_PREVIEW_V04_1",
            ):
                _write_run_sidecar(
                    audit_root,
                    sidecar,
                    "X02_STAGED_REAL_MEDIA_PREVIEW_V04_1",
                )

    def test_zero_dependency_server_accepts_evidence_only_multipart(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = make_x01_bundle(root)
            manifest = json.loads(manifest_path.read_text())
            boundary = "DiaryOneTestBoundary"
            body = bytearray()

            def part(name, data, filename, content_type):
                body.extend(("--%s\r\n" % boundary).encode())
                body.extend((
                    'Content-Disposition: form-data; name="%s"; filename="%s"\r\n'
                    % (name, filename)
                ).encode())
                body.extend(("Content-Type: %s\r\n\r\n" % content_type).encode())
                body.extend(data)
                body.extend(b"\r\n")

            part("manifest", manifest_path.read_bytes(), "bundle.json", "application/json")
            for asset in manifest["assets"]:
                for frame in asset["frames"]:
                    path = root / frame["relative_path"]
                    part(frame["frame_id"], path.read_bytes(), path.name, "image/jpeg")
            body.extend(("--%s--\r\n" % boundary).encode())

            try:
                server = make_server(
                    "127.0.0.1", 0, adapter_name="fixture", bearer_token="test-token",
                    run_audit_dir=root / "server-audits",
                    x02_run_audit_dir=root / "x02-server-audits",
                )
            except PermissionError:
                self.skipTest("local sockets are disabled by this test sandbox")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request("GET", "/health")
                unauthorized = connection.getresponse()
                unauthorized.read()
                self.assertEqual(unauthorized.status, 401)
                connection.close()

                connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request("GET", "/health", headers={"Authorization": "Bearer test-token"})
                health_response = connection.getresponse()
                health = json.loads(health_response.read())
                self.assertEqual(health_response.status, 200)
                self.assertTrue(health["modelReady"])
                self.assertEqual(health["contractBasis"], "CANONICAL_V1_25_S00_S13")
                self.assertFalse(health["fullStagedPipelineImplemented"])
                self.assertTrue(health["stagedRealMediaPreviewImplemented"])
                self.assertEqual(health["schemaVersion"], "DIARY_ONE_X02_STAGED_PREVIEW_V04_1")
                self.assertEqual(health["pipelineVersion"], "X02_STAGED_REAL_MEDIA_PREVIEW_V04_1")
                self.assertEqual(health["previewPath"], "/x02/v0.4.1/preview")
                self.assertEqual(health["runSidecarPath"], "/x02/v0.4.1/run-sidecar")
                self.assertTrue(health["storylineSegmentationImplemented"])
                self.assertEqual(
                    health["storylineContractVersion"],
                    "DIARY_ONE_X02_STORYLINE_V03",
                )
                self.assertEqual(
                    health["writerSurfacePolicyVersion"],
                    "DIARY_ONE_X02_WRITER_SURFACE_V02",
                )
                self.assertEqual(health["perceptionBatchMaxAssets"], 3)
                self.assertEqual(health["perceptionBatchMaxFrames"], 18)
                self.assertEqual(health["perceptionBatchMaxEvidenceBytes"], 4 * 1024 * 1024)
                self.assertEqual(health["perceptionSingleAssetRetryLimit"], 1)
                self.assertEqual(
                    health["historicalX02V03"]["previewPath"],
                    "/x02/v0.3/preview",
                )
                self.assertEqual(health["evaluationRunMode"], "FRESH_FULL_RUN")
                self.assertFalse(health["crossRunSemanticCacheUsed"])
                self.assertEqual(
                    health["appLibraryBundleVersion"],
                    APP_LIBRARY_BUNDLE_VERSION_V03,
                )
                self.assertTrue(health["fieldLevelObservationDegradation"])
                self.assertTrue(health["durationAwarePhoneTestEvidence"])
                self.assertEqual(
                    health["observationSemanticContractVersion"],
                    "DIARY_ONE_X02_OBSERVATION_COMPATIBILITY_V02",
                )
                self.assertRegex(health["observationSemanticContractSHA256"], r"^[0-9a-f]{64}$")
                self.assertEqual(health["historicalX01"]["previewPath"], "/x01/v0.1/preview")
                self.assertEqual(health["maxAssets"], 240)
                self.assertTrue(health["runAuditEnabled"])
                connection.close()

                connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request(
                    "OPTIONS",
                    "/x02/v0.4.1/preview",
                    headers={
                        "Origin": "http://localhost:3000",
                        "Access-Control-Request-Method": "POST",
                        "Access-Control-Request-Headers": "authorization,content-type",
                    },
                )
                current_preflight = connection.getresponse()
                current_preflight.read()
                self.assertEqual(current_preflight.status, 204)
                self.assertEqual(
                    current_preflight.getheader("Access-Control-Allow-Origin"),
                    "http://localhost:3000",
                )
                connection.close()

                connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request(
                    "POST",
                    "/x02/v0.4/preview",
                    body=bytes(body),
                    headers={
                        "Content-Type": "multipart/form-data; boundary=" + boundary,
                        "Authorization": "Bearer test-token",
                    },
                )
                retired_v04_response = connection.getresponse()
                retired_v04_result = json.loads(retired_v04_response.read())
                self.assertEqual(retired_v04_response.status, 404, retired_v04_result)
                connection.close()

                connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request(
                    "OPTIONS",
                    "/x01/v0.1/preview",
                    headers={
                        "Origin": "http://localhost:3000",
                        "Access-Control-Request-Method": "POST",
                        "Access-Control-Request-Headers": "authorization,content-type",
                    },
                )
                preflight = connection.getresponse()
                preflight.read()
                self.assertEqual(preflight.status, 204)
                self.assertEqual(preflight.getheader("Access-Control-Allow-Origin"), "http://localhost:3000")
                self.assertIn("Authorization", preflight.getheader("Access-Control-Allow-Headers"))
                connection.close()

                connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request("GET", "/health", headers={"Origin": "https://example.com"})
                forbidden = connection.getresponse()
                forbidden.read()
                self.assertEqual(forbidden.status, 403)
                self.assertIsNone(forbidden.getheader("Access-Control-Allow-Origin"))
                connection.close()

                connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request(
                    "POST",
                    "/x01/v0.1/preview",
                    body=bytes(body),
                    headers={
                        "Content-Type": "multipart/form-data; boundary=" + boundary,
                        "Authorization": "Bearer test-token",
                    },
                )
                response = connection.getresponse()
                result = json.loads(response.read())
                self.assertEqual(response.status, 200, result)
                self.assertEqual(result["trace"]["originals_uploaded"], 0)
                self.assertEqual(result["trace"]["provider"], "fixture")
                audit_path = root / "server-audits" / result["session_id"] / "run_audit.json"
                self.assertTrue(audit_path.exists())
                audit = json.loads(audit_path.read_text())
                self.assertEqual(
                    audit["server_metrics"][0]["stage"],
                    "REQUEST_MULTIPART_MATERIALIZATION",
                )
                connection.close()

                sidecar = {
                    "schema_version": RUN_SIDECAR_SCHEMA_VERSION,
                    "session_id": result["session_id"],
                    "client_trace": {"total_duration_ms": 1_234},
                }
                sidecar_bytes = json.dumps(sidecar).encode()
                connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request(
                    "POST",
                    "/x01/v0.1/run-sidecar",
                    body=sidecar_bytes,
                    headers={
                        "Content-Type": "application/json",
                        "Content-Length": str(len(sidecar_bytes)),
                        "Authorization": "Bearer test-token",
                    },
                )
                sidecar_response = connection.getresponse()
                sidecar_result = json.loads(sidecar_response.read())
                self.assertEqual(sidecar_response.status, 200, sidecar_result)
                self.assertEqual(sidecar_result["saved"], ["client_trace"])
                self.assertTrue((audit_path.parent / "client_trace.json").exists())
                connection.close()

                connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request(
                    "POST",
                    "/x02/v0.4.1/preview",
                    body=bytes(body),
                    headers={
                        "Content-Type": "multipart/form-data; boundary=" + boundary,
                        "Authorization": "Bearer test-token",
                    },
                )
                x02_current_response = connection.getresponse()
                x02_current_result = json.loads(x02_current_response.read())
                self.assertEqual(x02_current_response.status, 200, x02_current_result)
                self.assertEqual(
                    x02_current_result["schema_version"],
                    "DIARY_ONE_X02_STAGED_PREVIEW_V04_1",
                )
                self.assertEqual(
                    x02_current_result["trace"]["pipeline_version"],
                    "X02_STAGED_REAL_MEDIA_PREVIEW_V04_1",
                )
                x02_current_audit_path = (
                    root
                    / "x02-server-audits"
                    / x02_current_result["session_id"]
                    / "run_audit.json"
                )
                self.assertTrue(x02_current_audit_path.exists())
                x02_current_audit = json.loads(x02_current_audit_path.read_text())
                self.assertEqual(
                    x02_current_audit["schema_version"],
                    "DIARY_ONE_X02_RUN_AUDIT_V04_1",
                )
                connection.close()

                x02_current_sidecar = {
                    "schema_version": RUN_SIDECAR_SCHEMA_VERSION,
                    "session_id": x02_current_result["session_id"],
                    "client_trace": {
                        "run_id": x02_current_result["trace"]["run_id"],
                        "pipeline_version": x02_current_result["trace"]["pipeline_version"],
                        "request_id": x02_current_result["trace"]["request_id"],
                        "bundle_manifest_sha256": x02_current_result["bundle_manifest_sha256"],
                    },
                }
                x02_current_sidecar_bytes = json.dumps(x02_current_sidecar).encode()
                connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request(
                    "POST",
                    "/x02/v0.4.1/run-sidecar",
                    body=x02_current_sidecar_bytes,
                    headers={
                        "Content-Type": "application/json",
                        "Content-Length": str(len(x02_current_sidecar_bytes)),
                        "Authorization": "Bearer test-token",
                    },
                )
                x02_current_sidecar_response = connection.getresponse()
                x02_current_sidecar_result = json.loads(x02_current_sidecar_response.read())
                self.assertEqual(
                    x02_current_sidecar_response.status,
                    200,
                    x02_current_sidecar_result,
                )
                self.assertEqual(x02_current_sidecar_result["saved"], ["client_trace"])
                self.assertTrue(
                    (x02_current_audit_path.parent / "client_trace.json").exists()
                )
                connection.close()

                connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request(
                    "POST",
                    "/x02/v0.3/preview",
                    body=bytes(body),
                    headers={
                        "Content-Type": "multipart/form-data; boundary=" + boundary,
                        "Authorization": "Bearer test-token",
                    },
                )
                x02_response = connection.getresponse()
                x02_result = json.loads(x02_response.read())
                self.assertEqual(x02_response.status, 200, x02_result)
                self.assertEqual(x02_result["schema_version"], "DIARY_ONE_X02_STAGED_PREVIEW_V03")
                self.assertEqual(x02_result["evaluation_run_mode"], "FRESH_FULL_RUN")
                self.assertFalse(x02_result["cross_run_semantic_cache_used"])
                self.assertFalse(x02_result["production_ready"])
                self.assertEqual(x02_result["trace"]["s13_status"], "NOT_EXECUTED_IN_WEB_PREVIEW")
                self.assertTrue(x02_result["decision_trace"]["stage_statuses"])
                x02_audit_path = (
                    root / "x02-server-audits" / x02_result["session_id"] / "run_audit.json"
                )
                self.assertTrue(x02_audit_path.exists())
                x02_audit = json.loads(x02_audit_path.read_text())
                self.assertEqual(x02_audit["schema_version"], "DIARY_ONE_X02_RUN_AUDIT_V03")
                self.assertFalse(x02_audit["image_payloads_included"])
                connection.close()

                x02_sidecar = {
                    "schema_version": RUN_SIDECAR_SCHEMA_VERSION,
                    "session_id": x02_result["session_id"],
                    "client_trace": {
                        "run_id": x02_result["trace"]["run_id"],
                        "pipeline_version": x02_result["trace"]["pipeline_version"],
                        "request_id": x02_result["trace"]["request_id"],
                        "bundle_manifest_sha256": x02_result["bundle_manifest_sha256"],
                    },
                }
                x02_sidecar_bytes = json.dumps(x02_sidecar).encode()
                connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request(
                    "POST",
                    "/x02/v0.3/run-sidecar",
                    body=x02_sidecar_bytes,
                    headers={
                        "Content-Type": "application/json",
                        "Content-Length": str(len(x02_sidecar_bytes)),
                        "Authorization": "Bearer test-token",
                    },
                )
                x02_sidecar_response = connection.getresponse()
                x02_sidecar_result = json.loads(x02_sidecar_response.read())
                self.assertEqual(x02_sidecar_response.status, 200, x02_sidecar_result)
                self.assertEqual(x02_sidecar_result["saved"], ["client_trace"])
                self.assertTrue((x02_audit_path.parent / "client_trace.json").exists())
                connection.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()

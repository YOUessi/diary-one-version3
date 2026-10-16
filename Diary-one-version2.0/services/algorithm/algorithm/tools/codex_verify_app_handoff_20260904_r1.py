"""Offline App contract fixtures. Uses exact packaged runtime; no model/network/server."""
import argparse
import copy
import dataclasses
import hashlib
import io
import json
import socket
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "source/src"))
sys.path.insert(0, str(ROOT))


def emit(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def no_network(*args, **kwargs):
    raise PermissionError("handoff offline runner prohibits network and server sockets")


def run(output):
    from codex_contract_test_support import ScriptedGateway, assert_json_schema_instance, make_x02_bundle_v02
    from diary_one_ci import x02, x01_server, codex_chapter_media, codex_content_brief
    from diary_one_ci.bundle import load_app_library_bundle, APP_LIBRARY_BUNDLE_VERSION_V03
    from PIL import Image

    source_manifest = json.loads((ROOT / "codex_source_manifest.json").read_text())
    for record in source_manifest["files"]:
        assert sha(ROOT / "source" / record["path"]) == record["sha256"]
    schema_path = ROOT / "source/contracts/codex_x02_staged_preview_v04_1_media_v01.schema.json"
    result_schema = json.loads(schema_path.read_text())
    input_schema = json.loads((ROOT / "source/contracts/app_library_bundle_v03.schema.json").read_text())
    testcase = unittest.TestCase()
    schema_check = lambda schema, result: assert_json_schema_instance(testcase, schema, result)
    output.mkdir(parents=True, exist_ok=False)

    class SyntheticGateway(ScriptedGateway):
        provider = "fixture"
        model = "codex-app-handoff-placeholder-only-r1"

        def __init__(self, spec):
            self.spec = spec
            event_index = spec.get("event_index")
            overrides = {i: {"fact_text": "交接占位事实%02d。" % i} for i in range(5)}
            if event_index is not None:
                overrides[event_index].update(event_kind="DISCOVERY", event_salience="HIGH")
                if spec.get("block_copy"):
                    overrides[event_index]["fact_text"] = "仅用于交接结构检查的占位文本不代表任何真实素材或观察事实。"
            super().__init__(
                {event_index: "HOME_LIFE"} if event_index is not None else {},
                storyline_groups=spec.get("groups", []), observation_overrides=overrides,
            )

        def _perception(self, context):
            output = super()._perception(context)
            failed = self.spec.get("unresolved_indices", [])
            failed_ids = {a["asset_id"] for a in context["assets"] if a["sequence_index"] in failed}
            output["observations"] = [o for o in output["observations"] if o["asset_id"] not in failed_ids]
            return output

        def _writer(self, context):
            result = {"chapters": [], "ahas": []}
            for memory in context["memories"]:
                aha = memory["memory_type"] == "AHA"
                text = "交接占位文案。"
                if aha and (self.spec.get("block_copy") or self.spec.get("fallback")):
                    text = "此处是用于检查长度失败路径的交接占位文本而不是真实文案。"
                result["ahas" if aha else "chapters"].append({
                    "candidate_id": memory["candidate_id"], "title": "交接样例", "text": text,
                    "claim_ids": [memory["facts"][0]["fact_id"]],
                })
            return result

        def call(self, stage, prompt, schema, evidence=(), context=None):
            result = super().call(stage, prompt, schema, evidence, context)
            if stage.startswith("S10_CHAPTER_VISUAL_SELECTION_"):
                result.output["display_count"] = 3
            return dataclasses.replace(result, model_calls=0, input_tokens=0, output_tokens=0,
                latency_seconds=0.0, input_rate_per_million=0.0, output_rate_per_million=0.0,
                pricing_basis="SYNTHETIC_ZERO_COST_NO_PROVIDER_CALL")

    def make_bundle(root, name, count):
        path = make_x02_bundle_v02(root)
        manifest = json.loads(path.read_text())
        # Retain all 5 duration profiles in a separate input-only fixture; day
        # state examples below use photos, with explicit placeholder JPEGs.
        photo_template = copy.deepcopy(manifest["assets"][0])
        namespace = uuid.uuid5(uuid.NAMESPACE_URL, "codex-handoff:" + name)
        manifest["session"]["session_id"] = str(namespace)
        manifest["session"]["exported_at"] = "2026-09-04T00:00:00Z"
        manifest["bundle_version"] = APP_LIBRARY_BUNDLE_VERSION_V03
        manifest["device"]["device_id"] = "SYNTHETIC_HANDOFF_NO_USER_DEVICE"
        manifest["device"]["sdk_version"] = "CONTRACT_FIXTURE_ONLY"
        assets = []
        for index in range(count):
            asset = copy.deepcopy(photo_template)
            uid = str(uuid.uuid5(namespace, "asset:%d" % index))
            asset["asset_id"] = "asset_" + uid
            asset.pop("timeline_offset_ms")
            asset["sequence_index"] = index
            asset["original_sha256"] = hashlib.sha256((name + str(index)).encode()).hexdigest()
            frame = asset["frames"][0]
            frame["frame_id"] = "frame_" + uid + "_00"
            frame["relative_path"] = "evidence/" + uid + ".jpg"
            target = root / frame["relative_path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            # Solid-color test bytes, no source image and no generated scene.
            Image.new("RGB", (768, 1024), (80 + index * 15, 100, 120)).save(target, format="JPEG")
            frame["sha256"] = sha(target)
            assets.append(asset)
        manifest["assets"] = assets
        emit(path, manifest)
        return path

    def bindings_check(result, manifest_path):
        """Handoff/App integration assertions, NOT an existing runtime endpoint."""
        bundle = load_app_library_bundle(manifest_path)
        manifest = bundle.manifest
        assert result["session_id"] == manifest["session"]["session_id"], "session_binding"
        assert result["bundle_manifest_sha256"] == sha(manifest_path), "bundle_hash_binding"
        assets = {a["asset_id"]: a for a in manifest["assets"]}
        observations = {o["id"]: o for o in result["observations"]}
        for memory in result["chapters"] + result["ahas"]:
            assert memory["hero_asset_id"] in {m["asset_id"] for m in memory["selected_media"]}, "hero_membership"
            for media in memory["selected_media"]:
                source = media["source_asset_id"]
                assert source in assets, "media_source_binding"
                assert media["asset_id"] == x02._app_asset_uuid(source), "media_asset_binding"
                assert media["observation_id"] in observations, "media_observation_binding"
                assert observations[media["observation_id"]]["source_asset_id"] == source, "media_observation_source"
                assert set(media["evidence_frame_ids"]) <= {f["frame_id"] for f in assets[source]["frames"]}, "media_frame_binding"
        x02._validate_v041_result_state(result,
            expected_asset_ids=list(assets),
            expected_evidence_frame_ids=[f["frame_id"] for a in assets.values() for f in a["frames"]])

    specs = {
        "visible": {"count": 5, "groups": [[0, 1, 2, 3]], "event_index": 4,
                    "expected": ["CHAPTER_DAY", "READY_PRIMARY_COPY", "COMPLETE"]},
        "partial_delivery": {"count": 5, "groups": [[0, 1, 2, 3]], "event_index": 4, "block_copy": True,
                    "expected": ["CHAPTER_DAY", "READY_WITH_ITEM_BLOCKS", "COMPLETE"]},
        "all_copy_blocked": {"count": 1, "event_index": 0, "block_copy": True,
                    "expected": ["HIGHLIGHT_DAY", "PIPELINE_BLOCKED", "COMPLETE"]},
        "partial_perception_blocked": {"count": 5, "groups": [[1, 2, 3]], "event_index": 4, "unresolved_indices": [0],
                    "expected": ["UNRESOLVED_DAY", "PIPELINE_BLOCKED", "PARTIAL_UNRESOLVED"]},
        "all_perception_blocked": {"count": 2, "unresolved_indices": [0, 1],
                    "expected": ["UNRESOLVED_DAY", "PIPELINE_BLOCKED", "PARTIAL_UNRESOLVED"]},
        "empty": {"count": 2, "expected": ["EMPTY_DAY", "NO_GROUNDED_MEMORY", "COMPLETE"]},
        "highlight": {"count": 1, "event_index": 0,
                    "expected": ["HIGHLIGHT_DAY", "READY_PRIMARY_COPY", "COMPLETE"]},
        "fallback": {"count": 1, "event_index": 0, "fallback": True,
                    "expected": ["HIGHLIGHT_DAY", "READY_WITH_GROUNDED_COPY_FALLBACK", "COMPLETE"]},
    }
    examples, results = [], {}
    for name, spec in specs.items():
        with tempfile.TemporaryDirectory() as temporary:
            bundle_path = make_bundle(Path(temporary), name, spec["count"])
            bundle = load_app_library_bundle(bundle_path)
            schema_check(input_schema, bundle.manifest)
            result = x02.run_x02_v041(bundle_path, SyntheticGateway(spec))
            schema_check(result_schema, result)
            bindings_check(result, bundle_path)
            state = [result[k] for k in ("semantic_day_state", "delivery_state", "coverage_status")]
            assert state == spec["expected"], (name, state)
            assert result["trace"]["model_calls"] == 0
            assert result["trace"]["input_tokens"] == result["trace"]["output_tokens"] == 0
            destination = output / ("codex_" + name)
            emit(destination / "bundle.json", bundle.manifest)
            for asset in bundle.manifest["assets"]:
                for frame in asset["frames"]:
                    target = destination / frame["relative_path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((bundle_path.parent / frame["relative_path"]).read_bytes())
            emit(destination / "codex_result.json", result)
            x01_server._write_x02_run_audit(destination / "codex_audits", bundle.manifest, result, 0, 0, 0)
            examples.append({"case": name, "state": state, "schema": "PASS_EXISTING_SUBSET_VALIDATOR",
                "runtime_state": "PASS", "handoff_binding_assertions": "PASS", "real_model_calls": 0,
                "chapters": len(result["chapters"]), "ahas": len(result["ahas"]),
                "visible_memories": sum(o["visibility_state"] == "VISIBLE_PREVIEW" for o in result["selected_memory_outcomes"]),
                "bundle_path": str(destination.relative_to(output) / "bundle.json"),
                "result_path": str(destination.relative_to(output) / "codex_result.json")})
            results[name] = (result, destination / "bundle.json")
    # Input-only duration profile fixture. No video exists or is uploaded;
    # times below are explicit synthetic clip-relative sample positions.
    profile_root = output / "codex_duration_profiles"
    profile_root.mkdir()
    profile_path = make_x02_bundle_v02(profile_root)
    profile = json.loads(profile_path.read_text())
    profile["bundle_version"] = APP_LIBRARY_BUNDLE_VERSION_V03
    for index, asset in enumerate(profile["assets"]):
        asset.pop("timeline_offset_ms")
        asset["sequence_index"] = index
        for frame in asset["frames"]:
            target = profile_root / frame["relative_path"]
            Image.new("RGB", (768, 1024), (80 + index * 15, 100, 120)).save(target, format="JPEG")
            frame["sha256"] = sha(target)
            with Image.open(target) as decoded:
                decoded.load()
                assert decoded.size == (768, 1024) and decoded.format == "JPEG"
    emit(profile_path, profile)
    schema_check(input_schema, profile)
    load_app_library_bundle(profile_path)
    assert [len(a["frames"]) for a in profile["assets"]] == [1, 3, 4, 8, 12]
    input_checks = []
    for name, mutation in (
        ("bundle_version", lambda m: m.update(bundle_version="DIARY_ONE_APP_LIBRARY_BUNDLE_V99")),
        ("sequence_gap", lambda m: m["assets"][0].update(sequence_index=3)),
        ("uncontracted_capture_time", lambda m: m["assets"][0].update(capture_time="2026-09-04T12:00:00+08:00")),
        ("evidence_hash", lambda m: m["assets"][0]["frames"][0].update(sha256="0" * 64)),
    ):
        invalid = copy.deepcopy(profile)
        mutation(invalid)
        invalid_path = profile_root / ("codex_reject_" + name + ".json")
        emit(invalid_path, invalid)
        try:
            load_app_library_bundle(invalid_path)
        except ValueError as exc:
            input_checks.append({"case": name, "runtime_loader_rejected": True, "reason": str(exc)})
        else:
            raise AssertionError("loader accepted input mismatch: " + name)
    try:
        x02.run_x02_v03(profile_path, SyntheticGateway({"groups": []}))
    except x02.X02ContractError as exc:
        input_checks.append({"case": "bundle_v03_on_historical_x02_v03", "runtime_loader_rejected": True, "reason": str(exc)})
    else:
        raise AssertionError("historical V03 unexpectedly accepted Bundle V03")

    good, bundle_path = results["visible"]
    assert len(good["chapters"][0]["storyline_identity"]["beat_map"]) == 4
    assert len(good["chapters"][0]["selected_media"]) == 3
    mutations = {
        "wrong_result_version": lambda r: r.update(schema_version="DIARY_ONE_X02_STAGED_PREVIEW_V03"),
        "wrong_storyline_version": lambda r: r.update(storyline_contract_version="DIARY_ONE_X02_STORYLINE_V02"),
        "invented_time": lambda r: r.update(timeline_date="2026-09-04"),
        "wrong_hero_reference": lambda r: r["chapters"][0].update(hero_asset_id=str(uuid.UUID(int=1))),
        "wrong_media_frame": lambda r: r["chapters"][0]["selected_media"][0].update(evidence_frame_ids=["frame_not_in_this_bundle"]),
        "wrong_bundle_hash": lambda r: r.update(bundle_manifest_sha256="0" * 64),
    }
    rejected = []
    for name, change in mutations.items():
        invalid = copy.deepcopy(good)
        change(invalid)
        checks = {}
        for layer, check in (
            ("existing_schema", lambda: schema_check(result_schema, invalid)),
            ("existing_runtime_state", lambda: x02._validate_v041_result_state(invalid)),
            ("handoff_binding_assertions", lambda: bindings_check(invalid, bundle_path)),
        ):
            try:
                check()
            except (AssertionError, ValueError, x02.X02ContractError) as exc:
                checks[layer] = {"rejected": True, "reason": str(exc)[:280]}
            else:
                checks[layer] = {"rejected": False}
        assert any(check["rejected"] for check in checks.values()), (name, "UNDETECTED")
        emit(output / "codex_rejections" / ("codex_" + name + ".json"), invalid)
        rejected.append({"case": name, "checks": checks})

    class SourceHealth:
        path = "/health"
        stage_gateway = x02.FixtureStageGateway()
        max_assets = x01_server.DEFAULT_MAX_ASSETS
        max_sidecar_bytes = x01_server.DEFAULT_MAX_SIDECAR_BYTES
        _origin_allowed = lambda self: True
        _authorized = lambda self: True
        def _json(self, status, body):
            self.body = body
    health = SourceHealth()
    x01_server.X01RequestHandler.do_GET(health)
    emit(output / "codex_source_health_shape_NOT_LIVE.json", {"evidence_kind": "HANDLER_EXECUTED_IN_MEMORY_NO_SOCKET_NOT_LIVE_HEALTH", "body": health.body})
    identities = {name: getattr(x02, name) for name in (
        "X02_SCHEMA_VERSION", "X02_PIPELINE_VERSION", "X02_PREVIEW_PATH", "X02_RUN_SIDECAR_PATH",
        "X02_OBSERVATION_COMPATIBILITY_VERSION", "X02_OBSERVATION_COMPATIBILITY_SHA256",
        "X02_FIELD_DEGRADATION_VERSION", "X02_FIELD_DEGRADATION_SHA256",
        "X02_STORYLINE_CONTRACT_VERSION", "X02_STORYLINE_CONTRACT_SHA256",
        "X02_WRITER_SURFACE_POLICY_VERSION", "X02_WRITER_GROUNDING_POLICY", "X02_FACT_RETENTION_POLICY_VERSION")}
    identities.update(chapter_media_policy=codex_chapter_media.POLICY_VERSION,
        content_brief_policy=codex_content_brief.POLICY_VERSION, output_schema_sha256=sha(schema_path),
        input_bundle_version=APP_LIBRARY_BUNDLE_VERSION_V03,
        service_live_identity="UNVERIFIED_NO_HEALTH_RESPONSE")
    emit(output / "codex_contract_identities.json", identities)
    emit(output / "codex_stage_request_schemas.json", {
        "evidence_kind": "EXTRACTED_FROM_PINNED_SOURCE_NOT_PROVIDER_ENFORCED_SCHEMA",
        "S04": x02.PERCEPTION_SCHEMA, "S05_S07": x02.STRUCTURE_SCHEMA,
        "S10": codex_chapter_media.SELECTION_SCHEMA, "S11": x02.WRITER_SCHEMA,
        "provider_response_format": {"type": "json_object"},
        "strict_json_schema_activated": False,
    })
    report = {"candidate_id": source_manifest["candidate_id"], "python": sys.version,
        "status": "OFFLINE_CONTRACT_CHECKS_PASS_NOT_APP_OR_QUALITY_ACCEPTANCE",
        "synthetic_only": True, "real_model_calls": 0, "network_enabled": False,
        "real_media_or_user_text_included": False, "examples": examples, "rejections": rejected,
        "input_rejections": input_checks, "duration_profile_counts": [1, 3, 4, 8, 12],
        "schema_validation_limit": "Existing repository subset validator; not independent Draft 2020-12 certification",
        "fixtures_are_not_training_data_or_semantic_rules": True,
        "rerun_note": "Result run IDs and timings vary; source archive and archived artifact hashes are the fixed evidence."}
    emit(output / "codex_offline_evidence.json", report)
    print(json.dumps({"examples_passed": len(examples), "negative_cases_detected": len(rejected), "real_model_calls": 0}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with patch.object(socket.socket, "connect", no_network), patch.object(socket.socket, "connect_ex", no_network), patch.object(socket.socket, "bind", no_network):
        run(args.output.resolve())

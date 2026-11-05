"""Direct VLM core regression: all-frame order, failed [] retry, identity gates."""
import copy
import json
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest
from diary_one_ci import direct_vlm as direct
from diary_one_ci.x02 import StageRun, X02ExecutionError


def specimen(tmp_path):
    sid = str(uuid.uuid4())
    bundle = {"session": {"session_id": sid}, "assets": []}
    owners = {}
    for index in range(4):
        aid = "asset_" + str(uuid.uuid4())
        fid = "f" + str(index)
        frame = {"frame_id": fid, "source_timestamp_ms": 2500}
        asset = {"asset_id": aid, "media_kind": "VIDEO", "original_duration_ms": 9000}
        bundle["assets"].append(asset)
        owners[fid] = {"asset": asset, "frame": frame, "sequence": index + 1, "path": tmp_path / fid}
        (tmp_path / fid).write_bytes(b"x")
    manifest = tmp_path / "bundle.json"
    manifest.write_text(json.dumps(bundle))
    wrapped = SimpleNamespace(manifest=bundle, manifest_path=manifest)
    evidence = [(owners[f]["asset"], owners[f]["frame"], owners[f]["path"]) for f in owners]
    proposal = {"schema_version": direct.MODEL_SCHEMA_VERSION,
        "day_summary": "日常城市漫步，途中出现不同地点和景观。",
        "chapter_count_rationale": "这些画面在同一主题下，合并成一章。",
        "excluded_non_lived_frame_ids": [],
        "chapters": [{"id": "C01", "title": "城市漫步", "story": "看见城市街区、道路和不同的建筑景观。",
            "hero_frame_id": "f0", "gallery_frame_ids": ["f0", "f1", "f2"],
            "experience_frame_ids": ["f0", "f1", "f2", "f3"],
            "key_moments": [{"description": "街区及建筑景观", "frame_ids": ["f0", "f2"]}],
            "editorial_summary": "同一组街区主题图像互补。"}]}
    return wrapped, evidence, owners, proposal


class StubGateway:
    provider = "test"
    model = "qwen3.8-flash"
    ready = True
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []
    def call(self, stage, prompt, schema, evidence, context):
        self.calls.append([frame["frame_id"] for _, frame, _ in evidence])
        return StageRun(stage=stage, output=self.outputs[len(self.calls) - 1],
                        provider=self.provider, model=self.model,
                        request_id="test-" + str(len(self.calls)),
                        input_tokens=100, output_tokens=40, latency_seconds=0.01,
                        model_frame_count=len(evidence), model_calls=1, pricing_currency="CNY",
                        input_rate_per_million=0.8, output_rate_per_million=2.7,
                        native_currency_per_usd=7.2, pricing_basis="test")


def test_all_frames_direct_success(monkeypatch, tmp_path):
    bundle, evidence, owners, proposal = specimen(tmp_path)
    monkeypatch.setattr(direct, "prepare_evidence", lambda _: (bundle, evidence, owners, 4))
    gw = StubGateway([proposal])
    result = direct.run_direct_vlm(tmp_path / "bundle.json", gw)
    assert gw.calls == [["f0", "f1", "f2", "f3"]]
    assert len(result["chapters"]) == 1 and len(result["chapters"][0]["selected_media"]) == 3
    assert result["trace"]["model_calls"] == 1
    assert result["decision_trace"]["no_staged_pipeline"] is True


def test_empty_array_triggers_one_bounded_retry(monkeypatch, tmp_path):
    bundle, evidence, owners, proposal = specimen(tmp_path)
    monkeypatch.setattr(direct, "prepare_evidence", lambda _: (bundle, evidence, owners, 4))
    gw = StubGateway([[], proposal])
    result = direct.run_direct_vlm(tmp_path / "bundle.json", gw)
    assert len(gw.calls) == 2 and result["trace"]["model_calls"] == 2
    assert result["trace"]["input_tokens"] == 200
    assert result["decision_trace"]["attempt_validation_errors"][0] == ["model_output_not_object"]


def test_persistent_invalid_output_fails_closed(monkeypatch, tmp_path):
    bundle, evidence, owners, proposal = specimen(tmp_path)
    monkeypatch.setattr(direct, "prepare_evidence", lambda _: (bundle, evidence, owners, 4))
    gw = StubGateway([[], []])
    with pytest.raises(X02ExecutionError) as error:
        direct.run_direct_vlm(tmp_path / "bundle.json", gw)
    assert error.value.code == "DIRECT_VLM_OUTPUT_INVALID"
    assert len(error.value.stage_runs) == 2


def test_unknown_or_excluded_frame_rejected(tmp_path):
    _, _, owners, good = specimen(tmp_path)
    bad = copy.deepcopy(good)
    bad["chapters"][0]["gallery_frame_ids"][1] = "invented"
    assert any("unknown_frame_id" in e for e in direct.validate_proposal(bad, owners))
    bad = copy.deepcopy(good)
    bad["excluded_non_lived_frame_ids"] = ["f0"]
    assert any("excluded_frame" in e for e in direct.validate_proposal(bad, owners))


def test_same_clip_different_actual_frames_allowed(tmp_path):
    _, _, owners, good = specimen(tmp_path)
    owners["f1"]["asset"] = owners["f0"]["asset"]
    assert not direct.validate_proposal(good, owners)


def test_frame_cap_preflight_is_fail_closed(tmp_path, monkeypatch):
    bundle, evidence, owners, proposal = specimen(tmp_path)
    monkeypatch.setattr(direct, "prepare_evidence", lambda _: (_ for _ in ()).throw(
        X02ExecutionError("over 250",stage=direct.STAGE,code="DIRECT_VLM_FRAME_LIMIT",stage_runs=[])))
    gw = StubGateway([proposal])
    with pytest.raises(X02ExecutionError) as error:
        direct.run_direct_vlm(tmp_path / "bundle.json", gw)
    assert error.value.code == "DIRECT_VLM_FRAME_LIMIT"
    assert len(gw.calls) == 0

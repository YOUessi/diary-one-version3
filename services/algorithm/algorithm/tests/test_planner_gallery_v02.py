"""V02 isolated-switch end-to-end tests: algorithm -> BFF -> publisher.

All images real JPEG. All model runs are fake in-memory providers: no API spend.
"""
from __future__ import annotations

import copy
import hashlib
import json
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

from diary_one_ci import direct_vlm, planner_gallery_v02 as pg
from diary_one_ci.x02 import StageRun, X02ExecutionError
from shared.planner_gallery_result_contract import validate_planner_gallery_result
from shared.result_admit import apply_admission
from shared.result_contract import (
    PLANNER_GALLERY, SCHEMA_SHA256, validate_result_contract,
)
from jsonschema import Draft202012Validator


PLAN = {
    "chapters": [
        {"title": "海港步道漫游", "story": "沿海港缓慢步行，观察码头建筑和轮渡的变化。", "end_clip": 2},
        {"title": "街区与商店参观", "story": "转入城市内部街道，观察店铺橱窗与周边活动。", "end_clip": 4},
    ],
    "excluded_images": [],
}
GAL1 = {"selected_images": [1, 3], "key_moments": [{"text": "海港中可见的轮渡", "image_index": 2}]}
GAL2 = {"selected_images": [1, 4], "key_moments": [{"text": "商店旁边的街景", "image_index": 3}]}


class FakeGateway:
    ready = True
    provider = "fixture"
    model = "fake-qwen-vlm"

    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = []

    def call(self, stage, prompt, schema, evidence=(), context=None):
        assert self.answers, "Unexpected extra model call"
        answer = self.answers.pop(0)
        n = len(evidence)
        assert n > 0
        assert all(Path(p).exists() for _, _, p in evidence)
        labels = context["_direct_vlm_frame_chronology"]
        assert len(labels) == n
        assert set(labels) == {str(frame["frame_id"]) for _, frame, _ in evidence}
        assert list(labels.values())[0].startswith("IMAGE_INDEX_1_BASED=1 CLIP_SEQUENCE_1_BASED=")
        self.calls.append({
            "stage": stage, "evidence_asset_ids": sorted({a["asset_id"] for a, _, _ in evidence}),
            "frame_count": n, "prompt": prompt, "labels": labels,
        })
        return StageRun(
            stage=stage, output=copy.deepcopy(answer), provider=self.provider,
            model=self.model, request_id=f"req-{len(self.calls):02d}",
            input_tokens=500, output_tokens=100, latency_seconds=.03,
            model_frame_count=n, model_calls=1,
            pricing_currency="CNY", input_rate_per_million=.8,
            output_rate_per_million=2.7, native_currency_per_usd=7.2,
            pricing_basis="test",
        )


@pytest.fixture
def evidence(tmp_path, monkeypatch):
    session_id = str(uuid.uuid4())
    assets = []
    rows = []
    owners = {}
    frames_dir = tmp_path / "frames"
    frames_dir.mkdir()
    for clip in range(1, 5):
        aid = f"asset_{clip:02d}"
        asset = {
            "asset_id": aid, "sequence_index": clip - 1,
            "media_kind": "VIDEO", "original_duration_ms": 10000,
            "frames": [],
        }
        for frame_no, ms in enumerate((1500, 7500)):
            fid = f"{aid}-w0-f{frame_no}"
            rel = f"frames/{fid}.jpg"
            dst = tmp_path / rel
            im = Image.new("RGB", (768, 1024), (clip * 40, frame_no * 70, 120))
            im.save(dst, "JPEG", quality=78)
            frame = {
                "frame_id": fid, "relative_path": rel, "width": 768,
                "height": 1024, "sha256": hashlib.sha256(dst.read_bytes()).hexdigest(),
                "source_timestamp_ms": ms,
            }
            asset["frames"].append(frame)
            rows.append((asset, frame, dst))
            owners[fid] = {"asset": asset, "frame": frame, "path": dst, "sequence": clip}
        assets.append(asset)
    manifest = {
        "bundle_version": "DIARY_ONE_APP_LIBRARY_BUNDLE_V04",
        "session": {"session_id": session_id}, "assets": assets,
    }
    manifest_path = tmp_path / "bundle.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False))
    bundle = SimpleNamespace(manifest=manifest, manifest_path=manifest_path)
    monkeypatch.setattr(direct_vlm, "prepare_evidence", lambda _: (
        bundle, rows, owners, sum(p.stat().st_size for _, _, p in rows)
    ))
    return bundle, rows, owners


def make_result(evidence, answers=None, audit_dir=None):
    bundle, _, _ = evidence
    provider = FakeGateway(answers if answers is not None else [PLAN, GAL1, GAL2])
    result = pg.run_planner_gallery(
        bundle.manifest_path, provider, audit_dir=audit_dir,
    )
    return result, provider


def test_default_route_off(monkeypatch):
    from diary_one_ci import x01_server
    monkeypatch.delenv("DIARY_ONE_X02_EDITOR", raising=False)
    assert x01_server._direct_vlm_enabled()
    assert not x01_server._planner_gallery_enabled()
    monkeypatch.setenv("DIARY_ONE_X02_EDITOR", "planner_gallery_v02")
    assert x01_server._planner_gallery_enabled()
    assert not x01_server._direct_vlm_enabled()
    monkeypatch.setenv("DIARY_ONE_X02_EDITOR", "product_v1")
    assert not x01_server._planner_gallery_enabled()


def test_end_to_end_bff_bound_and_physically_scoped(evidence):
    result, provider = make_result(evidence)
    bundle, _, _ = evidence
    assert [call["stage"] for call in provider.calls] == [
        pg.PLAN_STAGE, pg.GALLERY_STAGE, pg.GALLERY_STAGE,
    ]
    assert provider.calls[0]["frame_count"] == 8
    assert [x["frame_count"] for x in provider.calls[1:]] == [4, 4]
    assert provider.calls[1]["evidence_asset_ids"] == ["asset_01", "asset_02"]
    assert provider.calls[2]["evidence_asset_ids"] == ["asset_03", "asset_04"]
    # Model uses local IMAGE numbers while clip IDs remain original global numbers.
    assert "CLIP_SEQUENCE_1_BASED=3" in list(provider.calls[2]["labels"].values())[0]
    assert [ch["source_clip_start"] for ch in result["chapters"]] == [1, 3]
    assert [ch["source_clip_end"] for ch in result["chapters"]] == [2, 4]
    assert result["trace"]["model_calls"] == 3
    assert result["trace"]["model_frame_count"] == 16
    assert result["trace"]["request_ids"] == ["req-01", "req-02", "req-03"]
    assert result["schema_version"] == pg.SCHEMA_VERSION
    validate_planner_gallery_result(result, bundle.manifest_path.read_bytes(),
                                    bundle.manifest_path.parent)
    assert validate_result_contract(
        result, bundle.manifest_path.read_bytes(), bundle.manifest_path.parent
    ) == SCHEMA_SHA256[PLANNER_GALLERY]
    assert not list(Draft202012Validator(
        json.loads((Path(__file__).parents[3] /
                    "bff/shared/contracts/planner_gallery_chapter_v02.schema.json").read_text())
    ).iter_errors(result))


def test_publication_disabled_without_separate_bff_opt_in(evidence, monkeypatch):
    result, _ = make_result(evidence)
    bundle = evidence[0]
    monkeypatch.delenv("DIARY_ONE_ALLOW_PLANNER_GALLERY_V02_PUBLISH", raising=False)
    _, envelope = apply_admission(
        result, bundle_version=bundle.manifest["bundle_version"],
        allow_mock=False, manifest_bytes=bundle.manifest_path.read_bytes(),
        bundle_dir=bundle.manifest_path.parent,
    )
    assert not envelope["publish_admit"]
    assert envelope["fail_job"]
    assert envelope["admit_reason"] == "planner_gallery_v02_not_enabled"
    monkeypatch.setenv("DIARY_ONE_ALLOW_PLANNER_GALLERY_V02_PUBLISH", "1")
    _, accepted = apply_admission(
        result, bundle_version=bundle.manifest["bundle_version"],
        allow_mock=False, manifest_bytes=bundle.manifest_path.read_bytes(),
        bundle_dir=bundle.manifest_path.parent,
    )
    assert accepted["publish_admit"], accepted
    assert accepted["input_bound"] is True


@pytest.mark.parametrize("mutation", [
    lambda x: x["chapters"][0].update(source_clip_end=3),
    lambda x: x["chapters"][1].update(source_clip_start=2),
    lambda x: x["chapters"][0]["selected_media"][0].update(
        representative_frame_id="asset_04-w0-f0"),
    lambda x: x["chapters"][1]["experience_frame_ids"].pop(),
    lambda x: x["decision_trace"]["chapter_clip_intervals"][0].update(end_clip=3),
    lambda x: x["decision_trace"]["gallery_model_input_frames"].__setitem__(0, 0),
    lambda x: x["trace"].update(model_calls=2),
])
def test_bff_rejects_cross_field_tampering(evidence, mutation):
    result, _ = make_result(evidence)
    bundle = evidence[0]
    mutation(result)
    with pytest.raises((ValueError, KeyError, TypeError)):
        validate_result_contract(result, bundle.manifest_path.read_bytes(),
                                 bundle.manifest_path.parent)


def test_invalid_planner_boundary_never_calls_gallery(evidence):
    p1 = copy.deepcopy(PLAN)
    p2 = copy.deepcopy(PLAN)
    p1["chapters"][-1]["end_clip"] = 3
    p2["chapters"][0]["end_clip"] = 4
    provider = FakeGateway([p1, p2])
    with pytest.raises(X02ExecutionError) as e:
        pg.run_planner_gallery(evidence[0].manifest_path, provider)
    assert e.value.code == "PLANNER_GALLERY_PLAN_INVALID"
    assert len(provider.calls) == 2
    assert all(x["stage"] == pg.PLAN_STAGE for x in provider.calls)


def test_only_invalid_gallery_retried_without_replanning(evidence, tmp_path):
    bad = {"selected_images": [100], "key_moments": [{
        "text": "图片索引不存在", "image_index": 1}]}
    result, provider = make_result(
        evidence, answers=[PLAN, GAL1, bad, GAL2],
        audit_dir=tmp_path / "private_audits",
    )
    assert result["trace"]["model_calls"] == 4
    assert [x["stage"] for x in provider.calls] == [
        pg.PLAN_STAGE, pg.GALLERY_STAGE, pg.GALLERY_STAGE, pg.GALLERY_STAGE,
    ]
    assert provider.calls[2]["evidence_asset_ids"] == provider.calls[3]["evidence_asset_ids"]
    audit = sorted((tmp_path / "private_audits" /
                    evidence[0].manifest["session"]["session_id"]).glob("attempt_*.json"))
    assert len(audit) == 4
    assert all((x.stat().st_mode & 0o777) == 0o600 for x in audit)
    assert json.loads(audit[2].read_text())["validation_errors"]
    assert result["trace"]["model_calls"] == len(audit)


def test_repeated_invalid_gallery_fails_closed(evidence):
    bad = {"selected_images": [9], "key_moments": [{
        "text": "图像不存在索引", "image_index": 1}]}
    provider = FakeGateway([PLAN, GAL1, bad, bad])
    with pytest.raises(X02ExecutionError) as e:
        pg.run_planner_gallery(evidence[0].manifest_path, provider)
    assert e.value.code == "PLANNER_GALLERY_GALLERY_INVALID"
    assert len(provider.calls) == 4


def test_bad_chinese_plan_never_publishes(evidence):
    bad = copy.deepcopy(PLAN)
    bad["chapters"][0]["title"] = "Only English title"
    provider = FakeGateway([bad, bad])
    with pytest.raises(X02ExecutionError) as e:
        pg.run_planner_gallery(evidence[0].manifest_path, provider)
    assert e.value.code == "PLANNER_GALLERY_PLAN_INVALID"

"""BFF direct VLM admission requires actual evidence and exact input lineage."""
import copy
import hashlib
import io
import json
import uuid

import pytest
from PIL import Image

from shared.result_admit import apply_admission
from shared.result_contract import validate_result_contract, SCHEMA_SHA256, DIRECT


def direct_sample(tmp_path):
    content = io.BytesIO()
    Image.new("RGB", (768, 1024), "orange").save(content, format="JPEG")
    image_bytes = content.getvalue()
    file = tmp_path / "frames" / "f000.jpg"
    file.parent.mkdir()
    file.write_bytes(image_bytes)
    sid = str(uuid.uuid4())
    source = "asset_" + str(uuid.uuid4())
    fid = "f000"
    manifest = {
        "bundle_version": "DIARY_ONE_APP_LIBRARY_BUNDLE_V05",
        "session": {"session_id": sid},
        "assets": [{
            "asset_id": source, "media_kind": "PHOTO",
            "original_duration_ms": None,
            "frames": [{
                "frame_id": fid, "relative_path": "frames/f000.jpg",
                "sha256": hashlib.sha256(image_bytes).hexdigest(),
                "width": 768, "height": 1024,
            }],
        }],
    }
    raw = json.dumps(manifest).encode()
    public_id = str(uuid.uuid5(uuid.UUID(sid), "direct_vlm_v01:C01"))
    chapter = {
        "id": public_id, "candidate_id": "C01", "title": "街区一景",
        "story": "一个阳光下的街区画面，可以看见建筑和街道。",
        "preview_story": "街区一景",
        "tags": [], "moment_ids": [], "highlights": [], "claims": [],
        "hero_frame_id": fid, "hero_asset_id": source[6:],
        "experience_frame_ids": [fid],
        "key_moments": [{"description": "清晰的建筑街区", "frame_ids": [fid]}],
        "selected_media": [{
            "asset_id": source[6:], "source_asset_id": source,
            "media_kind": "PHOTO", "role": "HERO", "representative_frame_id": fid,
            "evidence_frame_ids": [fid], "start_ms": None, "end_ms": None,
            "focus_pts_ms": None, "range_basis": "STILL_IMAGE",
        }],
        "publication_status": "STAGED_PREVIEW_VALIDATED",
    }
    result = {
        "schema_version": DIRECT, "editor_policy": "DIRECT_VLM_GLOBAL_EDITOR_V01",
        "experimental": True, "production_ready": False,
        "session_id": sid, "bundle_manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "delivery_state": "READY_PRIMARY_COPY", "coverage_status": "INPUT_ALL_FRAMES_SUBMITTED",
        "unresolved_asset_ids": [], "chapters": [chapter], "ahas": [],
        "moments": [], "observations": [], "day_summary": "一天的街区生活。",
        "chapter_count_rationale": "单张图片仅有一个主题。",
        "excluded_non_lived_frame_ids": [],
        "selected_memory_outcomes": [{
            "memory_type": "CHAPTER", "memory_id": public_id,
            "visibility_state": "VISIBLE_PREVIEW",
        }],
        "trace": {
            "pipeline_version": "X02_DIRECT_VLM_CHAPTER_V01",
            "provider": "mock-test", "model": "fixture",
            "request_ids": ["test-001"], "model_calls": 1,
            "input_tokens": 50, "output_tokens": 30,
            "estimated_cost_usd": 0.001, "stage_metrics": [{"stage": "DIRECT_VLM_GLOBAL_EDITOR"}],
        },
        "decision_trace": {
            "no_staged_pipeline": True, "visual_fact_reviewed": False,
            "semantic_copy_verified": False, "prompt_sha256": "f" * 64,
            "input_coverage": {"frames_submitted": 1, "clips_received": 1,
                               "image_bytes": len(image_bytes)},
        },
    }
    return result, raw, file


def test_direct_input_bound_publish_passes(tmp_path):
    result, raw, _ = direct_sample(tmp_path)
    assert validate_result_contract(result, raw, tmp_path) == SCHEMA_SHA256[DIRECT]
    prepared, env = apply_admission(result, manifest_bytes=raw,
        bundle_dir=tmp_path, bundle_version="DIARY_ONE_APP_LIBRARY_BUNDLE_V05",
        allow_mock=False)
    assert env["publish_admit"] and env["input_bound"]


@pytest.mark.parametrize("mutate", [
    lambda r: r["chapters"][0].update(hero_frame_id="unknown"),
    lambda r: r["chapters"][0]["selected_media"][0].update(representative_frame_id="unknown"),
    lambda r: r["chapters"][0]["selected_media"][0].update(source_asset_id="other"),
    lambda r: r["chapters"][0]["selected_media"][0].update(range_basis="WHOLE_SOURCE_CLIP"),
    lambda r: r["chapters"][0].update(claims=[{"text": "fabricated old verified fact"}]),
    lambda r: r["selected_memory_outcomes"].clear(),
    lambda r: r["decision_trace"]["input_coverage"].update(frames_submitted=0),
    lambda r: r["excluded_non_lived_frame_ids"].append("f000"),
    lambda r: r["trace"].update(pipeline_version="X02_PRODUCT_EDITOR_V07"),
])
def test_direct_mutations_fail_closed(tmp_path, mutate):
    result, raw, _ = direct_sample(tmp_path)
    mutate(result)
    _, env = apply_admission(result, manifest_bytes=raw,
        bundle_dir=tmp_path, bundle_version="DIARY_ONE_APP_LIBRARY_BUNDLE_V05",
        allow_mock=False)
    assert not env["publish_admit"] and env["fail_job"], env


def test_direct_missing_or_corrupt_jpeg_rejected(tmp_path):
    result, raw, file = direct_sample(tmp_path)
    file.write_bytes(b"not-a-jpeg")
    _, env = apply_admission(result, manifest_bytes=raw,
        bundle_dir=tmp_path, bundle_version="DIARY_ONE_APP_LIBRARY_BUNDLE_V05",
        allow_mock=False)
    assert not env["publish_admit"]
    file.unlink()
    _, env2 = apply_admission(result, manifest_bytes=raw,
        bundle_dir=tmp_path, bundle_version="DIARY_ONE_APP_LIBRARY_BUNDLE_V05",
        allow_mock=False)
    assert not env2["publish_admit"]

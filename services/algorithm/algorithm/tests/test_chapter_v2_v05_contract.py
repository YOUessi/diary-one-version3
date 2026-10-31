"""Opt-in V05 capture-provenance, balanced media contract tests.

Falsifiable checks: V03/V04 remain strict; a timestamp is not automatically
trustworthy; no original video bytes enter cloud evidence.
"""
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from diary_one_ci import chapter_media_pool, scenelet_builder
from diary_one_ci.bundle import load_app_library_bundle
from test_mobileclip_evidence import MobileClipIntakeTests


def v05(tmp_path):
    path, original=MobileClipIntakeTests().make(tmp_path,2,10000)
    original["bundle_version"]="DIARY_ONE_APP_LIBRARY_BUNDLE_V05"
    for index, asset in enumerate(original["assets"]):
        asset.update({
            "capture_time_ms":1730000000000+index*120000,
            "capture_time_source":"EXIF_OFFSET" if index==0 else "ASSET_TIMESTAMP",
            "capture_time_confidence":"VERIFIED" if index==0 else "ESTIMATED",
        })
    path.write_text(json.dumps(original))
    return path,original


def test_v05_strict_opt_in_accepts_clock_provenance(tmp_path):
    path,original=v05(tmp_path)
    bundle=load_app_library_bundle(path)
    assert bundle.validation["passed"] is True
    assert all(a["original_included"] is False for a in bundle.manifest["assets"])
    for a in bundle.manifest["assets"]:
        assert not any("video.mp4" in f.get("relative_path","") for f in a["frames"])


def test_v05_estimated_source_timestamp_cannot_become_verified_timeline(tmp_path):
    _,original=v05(tmp_path)
    assets={f"V{i+1:03d}":{**asset,"asset_id":asset["asset_id"],
                           "sequence_index":asset["sequence_index"]}
            for i,asset in enumerate(original["assets"])}
    times=[scenelet_builder.time_record(v) for v in assets.values()]
    assert times[0]["time_reliability"]=="VERIFIED"
    assert times[1]["capture_time_ms"] is None
    assert times[1]["time_reliability"]=="UNKNOWN"
    assert scenelet_builder.build_scene_map(assets,{},[])["time_basis"]=="IMPORT_SEQUENCE_ONLY"


@pytest.mark.parametrize("field,value",[
    ("capture_time_ms", True),
    ("capture_time_ms", -1),
    ("capture_time_ms", float("inf")),
    ("capture_time_source", "DEVICE_CLOCK_GUESSED"),
    ("capture_time_confidence", "TRUST_ME"),
])
def test_v05_fails_closed_on_invalid_capture_provenance(tmp_path,field,value):
    path,contents=v05(tmp_path)
    contents["assets"][0][field]=value
    path.write_text(json.dumps(contents))
    with pytest.raises((ValueError,TypeError)):
        load_app_library_bundle(path)


def test_v04_rejects_v05_fields_to_preserve_version_contract(tmp_path):
    path,contents=v05(tmp_path)
    contents["bundle_version"]="DIARY_ONE_APP_LIBRARY_BUNDLE_V04"
    path.write_text(json.dumps(contents))
    with pytest.raises(ValueError,match="unsupported fields"):
        load_app_library_bundle(path)


def test_balanced_chapter_media_pool_reserves_every_evidence_group(tmp_path):
    facts,assets,chapters={},{},{}
    for group in range(4):
        cid=f"C{group+1:02d}"
        chapters[cid]=[]
        for index in range(9):
            n=group*9+index
            aid=f"V{n:03d}"
            fid=f"F{n:03d}"
            frame_id=f"asset-{n}-f0"
            assets[aid]={"asset_id":f"asset-{n}","sequence_index":n,
                "original_duration_ms":10000,
                "frames":[{"frame_id":frame_id,"source_timestamp_ms":4000,
                    "relative_path":f"frames/{aid}.jpg"}]}
            facts[fid]={"asset_id":aid,"visual_reviewed":True,
                        "evidence_frame_ids":[frame_id]}
            chapters[cid].append(fid)
    shown,evidence,audit=chapter_media_pool.select_balanced_candidates(
        facts,assets,SimpleNamespace(manifest_path=tmp_path/"bundle.json"),
        chapters,max_per_chapter=3,max_total=12)
    assert len(evidence)==12
    assert len(shown)==12
    assert len(audit["shown_frames"])==12
    assert all(c["status"]=="COVERED" and len(c["candidate_ids"])==3
               for c in audit["chapter_coverage"])
    assert all(c["fact_ids"] and c["frame_id"] in shown[c["asset_id"]]
               for c in audit["shown_frames"])


def test_no_unverified_anchor_enters_balanced_media_pool(tmp_path):
    assets={"V1":{"asset_id":"asset-1","sequence_index":0,
                  "original_duration_ms":10000,"frames":[{
                      "frame_id":"asset-1-f0","relative_path":"frames/V1.jpg",
                      "source_timestamp_ms":5000}]}}
    facts={"F1":{"asset_id":"V1","visual_reviewed":False,
                 "evidence_frame_ids":["asset-1-f0"]}}
    _,_,audit=chapter_media_pool.select_balanced_candidates(
        facts,assets,SimpleNamespace(manifest_path=tmp_path/"bundle.json"),
        {"C01":["F1"]})
    assert audit["shown_frames"]==[]
    assert audit["chapter_coverage"][0]["status"]=="NO_VERIFIED_CANDIDATE"

"""Restored V1 one-call natural Chapter + fail-closed Gallery unit/integration.

Real fixture JPEGs; only provider API is mocked. Original output never fixed.
"""
from __future__ import annotations
import copy,json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from diary_one_ci import direct_v1_single_quality as v1
from diary_one_ci import x01_server
from diary_one_ci.x02 import X02ExecutionError
from shared.result_contract import validate_result_contract
from shared.result_admit import apply_admission
from test_planner_gallery_v02 import FakeGateway, evidence

GOOD={
 "chapters":[
  {"title":"海港码头漫步",
   "story":"沿着海港步行，途经停靠的渡轮与滨水建筑，随后进入相邻的步行平台。",
   "selected_images":[1,3],
   "key_moments":[{"text":"渡轮经过港湾","image_index":2}]},
  {"title":"街道商铺与休憩",
   "story":"离开码头前往城区，沿着商业街慢慢走过店铺，在街角观察建筑与人流。",
   "selected_images":[5,7],
   "key_moments":[{"text":"街边店铺橱窗","image_index":8}]},
 ],
 "excluded_images":[]
}

def _fake_in_memory_bundle(evidence,answers=None, audit=None):
    bundle,_,_=evidence
    gateway=FakeGateway(answers or [GOOD])
    result=v1.run_direct_v1_quality(bundle.manifest_path,gateway,audit_dir=audit)
    return bundle,gateway,result

def test_default_editor_remains_direct(monkeypatch):
    monkeypatch.delenv("DIARY_ONE_X02_EDITOR",raising=False)
    assert x01_server._direct_vlm_enabled()
    assert not x01_server._direct_v1_quality_enabled()
    monkeypatch.setenv("DIARY_ONE_X02_EDITOR","direct_v1_quality")
    assert x01_server._direct_v1_quality_enabled()
    assert not x01_server._direct_vlm_enabled()

def test_frozen_v1_copy_and_noquota_model_schema_are_independent():
    p=v1.model_prompt(234,160)
    assert "一个 Chapter 对应一段连续、主题完整的体验" in p
    assert "作品是 Chapter 的内容，不是 Chapter 边界" in p
    assert "10–20 张" not in p
    assert "不将任何图库数量阈值理解成目标" in p
    schema=v1.model_schema(234)
    g=schema["properties"]["chapters"]["items"]["properties"]["selected_images"]
    assert "maxItems" not in g
    assert g["items"]["maximum"]==234
    assert schema["properties"]["chapters"]["items"]["properties"]["key_moments"]["items"]["properties"]["image_index"]["maximum"]==234
    assert schema["properties"]["excluded_images"]["items"]["maximum"]==234

def test_full_success_real_jpeg_and_bff_contract(evidence,tmp_path):
    bundle,gateway,result=_fake_in_memory_bundle(evidence,audit=tmp_path/"private")
    assert len(gateway.calls)==1
    assert gateway.calls[0]["frame_count"]==8
    assert result["schema_version"]=="DIARY_ONE_DIRECT_VLM_CHAPTER_V01"
    assert result["experiment"]==v1.EXPERIMENT
    assert result["trace"]["model_calls"]==1
    assert result["decision_trace"]["gallery_repair_count"]==0
    assert result["decision_trace"]["model_output_no_silent_truncation"] is True
    assert result["decision_trace"]["hard_published_gallery_limit"]==8
    assert [ch["title"] for ch in result["chapters"]]==[ch["title"] for ch in GOOD["chapters"]]
    assert [ch["story"] for ch in result["chapters"]]==[ch["story"] for ch in GOOD["chapters"]]
    assert [len(c["selected_media"]) for c in result["chapters"]]==[2,2]
    assert validate_result_contract(result,bundle.manifest_path.read_bytes(),
                                   bundle.manifest_path.parent)
    audits=sorted((tmp_path/"private").glob("attempt_*.json"))
    assert len(audits)==1
    assert audits[0].stat().st_mode&0o777 == 0o600
    assert json.loads(audits[0].read_text())["model_output_raw"]==GOOD

def test_opt_in_bff_publication_gate_default_off(evidence,monkeypatch):
    bundle,_,result=_fake_in_memory_bundle(evidence)
    monkeypatch.delenv("DIARY_ONE_ALLOW_DIRECT_V1_QUALITY_PUBLISH",raising=False)
    _,env=apply_admission(result,bundle_version=bundle.manifest["bundle_version"],
         allow_mock=False,manifest_bytes=bundle.manifest_path.read_bytes(),
         bundle_dir=bundle.manifest_path.parent)
    assert not env["publish_admit"]
    assert env["admit_reason"]=="direct_v1_quality_research_not_enabled"
    monkeypatch.setenv("DIARY_ONE_ALLOW_DIRECT_V1_QUALITY_PUBLISH","1")
    _,env=apply_admission(result,bundle_version=bundle.manifest["bundle_version"],
         allow_mock=False,manifest_bytes=bundle.manifest_path.read_bytes(),
         bundle_dir=bundle.manifest_path.parent)
    assert env["publish_admit"],env
    assert env["input_bound"]

@pytest.mark.parametrize("bad",[
    {"selected_images":[1,9]},
    {"selected_images":[1,2,3,4,5,6,7,8,9]},
    {"key_moments":[{"text":"越界图片","image_index":200}]},
    {"key_moments":[{"text":"过多瞬间","image_index":1}]*11},
    {"selected_images":[1,1]},
    {"selected_images":[5,7]},
])
def test_bad_first_stage_output_always_fails_closed(evidence,bad,tmp_path):
    wrong=copy.deepcopy(GOOD)
    wrong["chapters"][0].update(bad)
    gateway=FakeGateway([wrong,wrong])
    with pytest.raises(X02ExecutionError) as ex:
        v1.run_direct_v1_quality(evidence[0].manifest_path,gateway,
                                 audit_dir=tmp_path/"audit")
    assert ex.value.code=="V1_SINGLE_GALLERY_QUALITY_REJECTED"
    assert len(gateway.calls)==2
    files=sorted((tmp_path/"audit").glob("attempt_*.json"))
    assert len(files)==2
    assert all(json.loads(f.read_text())["validation_errors"] for f in files)

def test_cross_chapter_same_clip_different_image_rejected(evidence):
    _,e,_=evidence
    raw=copy.deepcopy(GOOD)
    raw["chapters"][0]["selected_images"]=[1,4]  # clip 1 and 2
    raw["chapters"][1]["selected_images"]=[3,7]  # clip 2 and 4, no shared JPEG
    errs,_,info=v1.validate_editorial_gallery(raw,e)
    assert any("CHAPTER_IMAGE_TIME_OVERLAP" in x for x in errs),errs
    assert not any("REUSED_GALLERY" in x for x in errs)

def test_reject_missing_tail_even_if_input_indices_valid(evidence):
    _,e,_=evidence
    raw=copy.deepcopy(GOOD)
    raw["chapters"]=raw["chapters"][:1]
    raw["chapters"][0]["selected_images"]=[1,2]  # Only clip 1/4 selected.
    raw["chapters"][0]["key_moments"]=[{"text":"来自开头的画面","image_index":2}]
    errs,_,_=v1.validate_editorial_gallery(raw,e)
    assert any("LAST_20_PERCENT_OF_CLIPS_NOT_REPRESENTED" in x for x in errs),errs

def test_reject_mechanical_consecutive_full_blocks_without_mutation():
    # Synthetic 30 independent clips, one image each. Each chapter exactly 8
    # consecutive IMAGE indices, then a large unrepresented tail.
    ev=[({"asset_id":f"s{i:02d}"},{"frame_id":f"F{i:02d}"},Path(f"/tmp/F{i:02d}.jpg"))
        for i in range(1,31)]
    raw={"chapters":[],"excluded_images":[]}
    for k in range(3):
        ids=list(range(k*8+1,(k+1)*8+1))
        raw["chapters"].append({"title":f"第{k+1}段连续经历",
        "story":"沿时间先后记录此段完整活动及其实际画面内容。","selected_images":ids,
        "key_moments":[{"text":"实际片段证据","image_index":ids[0]}]})
    copyraw=copy.deepcopy(raw)
    errors,_,_=v1.validate_editorial_gallery(raw,ev)
    assert "GALLERY_MECHANICAL_CONSECUTIVE_FULL_BLOCKS" in errors
    assert raw==copyraw, "Validator must not modify model output"

def test_harmless_bad_attempt_retried_once_same_prompt(evidence,tmp_path):
    wrong=copy.deepcopy(GOOD)
    wrong["chapters"][0]["selected_images"]=[99]
    gateway=FakeGateway([wrong,GOOD])
    out=v1.run_direct_v1_quality(evidence[0].manifest_path,gateway,
                                 audit_dir=tmp_path/"private")
    assert len(gateway.calls)==2
    assert gateway.calls[0]["prompt"]==gateway.calls[1]["prompt"]
    assert out["trace"]["model_calls"]==2
    assert out["decision_trace"]["gallery_repair_count"]==0
    assert len(list((tmp_path/"private").glob("attempt_*.json")))==2

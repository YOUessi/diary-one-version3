"""V03+ opt-in path, actual JPEG fixtures, safe output and zero silent repairs."""
from __future__ import annotations
import copy
import json

import pytest

from diary_one_ci import direct_vlm_v03plus as plus
from diary_one_ci import direct_vlm_compact as v03
from diary_one_ci import x01_server
from diary_one_ci.x02 import X02ExecutionError
from test_planner_gallery_v02 import evidence, FakeGateway
from shared.result_contract import validate_result_contract
from shared.result_admit import apply_admission

GOOD={
 "chapters":[
  {"title":"海港步道漫游","story":"沿着码头步道参观海港船只与水岸建筑，经过渡轮停靠处。",
   "selected_images":[1,3],
   "key_moments":[{"text":"港湾停泊的渡轮","image_index":2}]},
  {"title":"市场街区散步","story":"随后进入城市市场区域，欣赏不同摊位和店铺的建筑细节。",
   "selected_images":[5,8],
   "key_moments":[{"text":"市场里的特色商铺","image_index":6}]},
 ],
 "excluded_images": []
}

def test_base_v03_frozen_and_plus_only_small_addition():
    original=v03.prompt(image_count=235,clip_count=160)
    updated=plus.prompt(image_count=235,clip_count=160)
    assert v03.MODEL_PROTOCOL=="DIRECT_VLM_COMPACT_EDITOR_V03"
    assert v03.MAX_GALLERY==8==plus.MAX_SELECTED
    assert len(original)==1210
    assert 300<=len(updated)-len(original)<=750
    assert original.split("【输出只需要编辑决策")[0] in updated
    assert "连续完整" in updated or "完整经历" in updated
    assert "3–6 张" in updated and "最多 8 张" in updated
    assert "10–20 张" not in updated and "20 张" not in updated
    assert "简体中文" in updated and "重要" in updated
    assert v03.SCHEMA["properties"]["chapters"]["items"]["properties"]["selected_images"]["maxItems"]==8
    minimal=plus.prompt_minimal(image_count=235,clip_count=160)
    assert 1400<len(minimal)<1700
    assert "【精选视觉证据" in minimal and "10–20 张" not in minimal

def test_route_default_stays_unchanged(monkeypatch):
    monkeypatch.delenv("DIARY_ONE_X02_EDITOR",raising=False)
    assert x01_server._direct_vlm_enabled()
    assert not x01_server._v03plus_enabled()
    monkeypatch.setenv("DIARY_ONE_X02_EDITOR","direct_vlm_v03plus")
    assert not x01_server._direct_vlm_enabled()
    assert x01_server._v03plus_enabled()

def test_original_v03plus_contract_and_no_inferred_frames(evidence,tmp_path):
    bundle,frames,_=evidence
    fake=FakeGateway([GOOD])
    result=plus.run_direct_vlm_v03plus(
        bundle.manifest_path,fake,audit_dir=tmp_path/"audit")
    assert len(fake.calls)==1
    assert fake.calls[0]["frame_count"]==8
    assert "【精选视觉证据" in fake.calls[0]["prompt"]
    assert result["schema_version"]=="DIARY_ONE_DIRECT_VLM_CHAPTER_V01"
    assert result["experiment"]==plus.EXPERIMENT
    assert result["trace"]["model_calls"]==1
    assert result["decision_trace"]["gallery_structural_verified"] is True
    assert result["decision_trace"]["gallery_semantic_verified"] is False
    assert result["decision_trace"]["explicit_selected_frame_lineage_only"] is True
    assert [x["title"] for x in result["chapters"]]==[x["title"] for x in GOOD["chapters"]]
    assert [x["story"] for x in result["chapters"]]==[x["story"] for x in GOOD["chapters"]]
    assert [len(x["selected_media"]) for x in result["chapters"]]==[2,2]
    assert [len(x["experience_frame_ids"]) for x in result["chapters"]]==[3,3]
    assert validate_result_contract(result,bundle.manifest_path.read_bytes(),bundle.manifest_path.parent)
    audit=tmp_path/"audit"/"v03plus_attempt_01.json"
    assert audit.exists() and audit.stat().st_mode&0o777==0o600
    assert json.loads(audit.read_text())["raw_model_output"]==GOOD

@pytest.mark.parametrize("mutation,errorcode",[
 (lambda x: x["chapters"][0].update(selected_images=list(range(1,9))+[1]),"MAXITEMS"),
 (lambda x: x["chapters"][0].update(selected_images=[1,999]),""),
 (lambda x: x["chapters"][0].update(selected_images=[1,1]),"DUPLICATE"),
 (lambda x: x["chapters"][0].update(selected_images=[1,3,5]),"OVERLAP"),
 (lambda x: x["chapters"][0].update(key_moments=[{"text":"图片索引越界","image_index":999}]),""),
 (lambda x: x["chapters"][0].update(key_moments=[]),"KEY"),
 (lambda x: x["chapters"][0].update(title="Sydney Harbour"),"CHINESE"),
])
def test_rejection_does_not_silently_fix(evidence,mutation,errorcode):
    raw=copy.deepcopy(GOOD)
    mutation(raw)
    before=copy.deepcopy(raw)
    errors,_,_=plus.validate_raw(raw,evidence[1])
    assert errors
    assert raw==before
    assert any(errorcode in x.upper() for x in errors),errors

def test_rejects_jpeg_different_index_same_clip_across_chapters(evidence):
    raw=copy.deepcopy(GOOD)
    raw["chapters"][0]["selected_images"]=[1,4] # source clip 1..2
    raw["chapters"][1]["selected_images"]=[3,7] # starts source clip 2
    errs,_,_=plus.validate_raw(raw,evidence[1])
    assert any("CHAPTER_SOURCE_CLIP_OVERLAP" in x for x in errs)

def test_model_failure_one_retry_never_drops_wrong_frame(evidence,tmp_path):
    bundle,_,_=evidence
    wrong=copy.deepcopy(GOOD)
    wrong["chapters"][0]["selected_images"]=[1,99]
    provider=FakeGateway([wrong,GOOD])
    result=plus.run_direct_vlm_v03plus(
        bundle.manifest_path,provider,audit_dir=tmp_path/"audit")
    assert result["trace"]["model_calls"]==2
    assert provider.calls[0]["prompt"]==provider.calls[1]["prompt"]
    assert len(list((tmp_path/"audit").glob("v03plus_attempt_*.json")))==2

def test_rejects_twice_without_fallback(evidence):
    bundle,_,_=evidence
    wrong=copy.deepcopy(GOOD)
    wrong["chapters"][0]["selected_images"]=[1,99]
    with pytest.raises(X02ExecutionError) as ex:
        plus.run_direct_vlm_v03plus(bundle.manifest_path,FakeGateway([wrong,wrong]))
    assert ex.value.code=="DIRECT_V03PLUS_OUTPUT_REJECTED"

def test_bff_research_publication_default_denied(evidence,monkeypatch):
    bundle,_,_=evidence
    r=plus.run_direct_vlm_v03plus(bundle.manifest_path,FakeGateway([GOOD]))
    monkeypatch.delenv("DIARY_ONE_ALLOW_V03PLUS_PUBLISH",raising=False)
    _,envelope=apply_admission(r,bundle_version=bundle.manifest["bundle_version"],
        allow_mock=False,manifest_bytes=bundle.manifest_path.read_bytes(),
        bundle_dir=bundle.manifest_path.parent)
    assert not envelope["publish_admit"]
    assert envelope["admit_reason"]=="direct_v03plus_research_not_enabled"
    monkeypatch.setenv("DIARY_ONE_ALLOW_V03PLUS_PUBLISH","1")
    _,envelope=apply_admission(r,bundle_version=bundle.manifest["bundle_version"],
        allow_mock=False,manifest_bytes=bundle.manifest_path.read_bytes(),
        bundle_dir=bundle.manifest_path.parent)
    assert envelope["publish_admit"]

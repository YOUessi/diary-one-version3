"""Compact protocol tests: only VLM decides story/ordering; frame references are exact."""
import copy
import json
import uuid
from pathlib import Path

import pytest

from diary_one_ci import direct_vlm_compact as c
from diary_one_ci import direct_vlm
from diary_one_ci.x02 import StageRun


def sample(tmp_path):
    sid=str(uuid.uuid4())
    assets=[]
    evidence=[]
    for clip in range(1,5):
        asset={"asset_id": f"asset_{clip}","sequence_index":clip-1,
               "media_kind":"VIDEO","original_duration_ms":10000}
        assets.append(asset)
        for part in (1,2):
            fid=f"frame{clip}_{part}"
            f={"frame_id":fid,"source_timestamp_ms":part*3000}
            path=tmp_path/(fid+".jpg")
            path.write_bytes(b"data")
            evidence.append((asset,f,path))
    raw={"chapters":[
        {"title":"海港与码头","story":"沿着海岸步道行走，观察船只与海港建筑。",
         "selected_images":[1,3],
         "key_moments":[{"text":"岸边的船只与码头","image_index":2}]},
        {"title":"城市商业街","story":"街道两边有商业楼宇和行走的路人。",
         "selected_images":[5,8],
         "key_moments":[{"text":"商业街道与店铺","image_index":6}]},
    ],"excluded_images":[]}
    return evidence,raw


def test_model_does_not_generate_frame_ids_and_converter_restores_exact_ids(tmp_path):
    evidence,raw=sample(tmp_path)
    assert c.prompt(image_count=8,clip_count=4).count("Frame ID")==0
    proposal,errors,repairs=c.convert(raw,evidence)
    assert not errors and not repairs
    assert proposal["chapters"][0]["hero_frame_id"]=="frame1_1"
    assert proposal["chapters"][0]["gallery_frame_ids"]==["frame1_1","frame2_1"]
    assert proposal["chapters"][0]["experience_frame_ids"]==[
        "frame1_1","frame1_2","frame2_1","frame2_2"]
    assert proposal["chapters"][1]["hero_frame_id"]=="frame3_1"
    assert proposal["chapters"][1]["key_moments"][0]["frame_ids"]==["frame3_2"]


def test_empty_list_is_explicit_rejection(tmp_path):
    evidence,_=sample(tmp_path)
    proposal,errors,_=c.convert([],evidence)
    assert proposal is None and errors==["top_level_not_object"]


def test_safe_dedupe_and_lossless_digit_string_repair(tmp_path):
    evidence,raw=sample(tmp_path)
    raw["chapters"][0]["selected_images"]=[1,"1",3,3]
    proposal,errors,repairs=c.convert(raw,evidence)
    assert not errors and proposal["chapters"][0]["gallery_frame_ids"]==["frame1_1","frame2_1"]
    assert repairs==["C01:duplicate_gallery_index_deduplicated","C01:duplicate_gallery_index_deduplicated"]


@pytest.mark.parametrize("mutation,reason", [
    (lambda x:x["chapters"][0].update(selected_images=[0,3]),"selected_image_outside_input"),
    (lambda x:x["chapters"][0].update(selected_images=[100,3]),"selected_image_outside_input"),
    (lambda x:x["chapters"][0].update(selected_images=[]),"invalid_gallery_length"),
    (lambda x:x["chapters"][0].update(selected_images=[True,3]),"selected_image_outside_input"),
    (lambda x:x["chapters"][1].update(selected_images=[1]),"gallery_reused_across_chapters"),
    (lambda x:x.update(excluded_images=[1]),"excluded_gallery_image"),
    (lambda x:x["chapters"][1].update(selected_images=[1,8]),"gallery_reused_across_chapters"),
])
def test_no_guessing_unknown_or_wrong_image(mutation,reason,tmp_path):
    evidence,raw=sample(tmp_path)
    mutation(raw)
    proposal,errors,_=c.convert(raw,evidence)
    assert proposal is None and any(reason in e for e in errors),errors


def test_noncamera_time_label_uses_order_not_invented_wall_time(tmp_path):
    evidence,raw=sample(tmp_path)
    labels={f["frame_id"]:"CLIP_SEQUENCE_1_BASED=1 INTER_CLIP_ELAPSED_TIME_UNKNOWN=true" for _,f,_ in evidence}
    out=c.image_labels(evidence,labels)
    assert out["frame1_1"].startswith("IMAGE_INDEX_1_BASED=1 CLIP_SEQUENCE_1_BASED=")
    assert out["frame4_2"].startswith("IMAGE_INDEX_1_BASED=8 CLIP_SEQUENCE_1_BASED=")


def test_missing_key_moments_uses_existing_selected_image_without_inventing_event(tmp_path):
    evidence,raw=sample(tmp_path)
    raw["chapters"][0].pop("key_moments")
    proposal,errors,repairs=c.convert(raw,evidence)
    assert not errors
    assert "C01:no_key_moment_use_selected_cover" in repairs
    assert proposal["chapters"][0]["key_moments"][0]["frame_ids"]==["frame1_1"]


def test_model_excluded_promo_not_in_derived_experience(tmp_path):
    evidence,raw=sample(tmp_path)
    raw["excluded_images"]=[4]
    proposal,errors,_=c.convert(raw,evidence)
    assert not errors
    assert proposal["excluded_non_lived_frame_ids"]==["frame2_2"]
    assert "frame2_2" not in proposal["chapters"][0]["experience_frame_ids"]


def test_original_story_and_chapter_count_not_rewritten(tmp_path):
    evidence,raw=sample(tmp_path)
    original=copy.deepcopy(raw)
    proposal,errors,_=c.convert(raw,evidence)
    assert not errors
    assert len(proposal["chapters"])==len(raw["chapters"])
    assert [c["story"] for c in proposal["chapters"]]==[c["story"] for c in original["chapters"]]


def test_audit_persists_raw_empty_and_success_with_private_mode(tmp_path,monkeypatch):
    # Model stub uses compact outputs; no network and no JPEG data persisted.
    from types import SimpleNamespace
    evidence,proposal=sample(tmp_path)
    asset_ids=list(dict.fromkeys(a["asset_id"] for a,_,_ in evidence))
    sid=str(uuid.uuid4())
    obj={"session":{"session_id":sid},"assets":[{"asset_id":aid} for aid in asset_ids]}
    p=tmp_path/"bundle.json";p.write_text(json.dumps(obj))
    bundle=SimpleNamespace(manifest=obj,manifest_path=p)
    owners={f["frame_id"]:{"asset":a,"frame":f,"path":path,
                           "sequence":int(a["sequence_index"])+1} for a,f,path in evidence}
    monkeypatch.setattr(direct_vlm,"prepare_evidence",lambda _:(bundle,evidence,owners,100))
    class Fake:
        ready=True
        provider="fixture"
        model="fake"
        def __init__(self):self.outputs=[[],proposal]
        def call(self,stage,prompt,schema,evidence,context):
            n=2-len(self.outputs)
            return StageRun(stage=stage,output=self.outputs.pop(0),
                  provider=self.provider,model=self.model,request_id=f"fake_{n}",
                  input_tokens=100,output_tokens=10,latency_seconds=.1,
                  model_frame_count=len(evidence),model_calls=1,
                  pricing_currency="CNY",input_rate_per_million=.8,
                  output_rate_per_million=2.7,native_currency_per_usd=7.2,pricing_basis="test")
    audit=tmp_path/"audit"
    result=direct_vlm.run_direct_vlm(p,Fake(),audit_dir=audit)
    assert result["trace"]["model_calls"]==2
    assert result["decision_trace"]["compact_model_protocol"]==c.MODEL_PROTOCOL
    entries=[json.loads(f.read_text()) for f in sorted(audit.glob("attempt_*.json"))]
    assert len(entries)==2
    assert entries[0]["model_output"]==[]
    assert entries[0]["validation_errors"]==["top_level_not_object"]
    assert entries[1]["model_output"]["chapters"][0]["title"]=="海港与码头"
    assert (audit.stat().st_mode & 0o777)==0o700
    assert all((p.stat().st_mode & 0o777)==0o600 for p in audit.iterdir())



def test_redundant_old_clip_bounds_ignored_not_a_reason_to_replan(tmp_path):
    evidence,raw=sample(tmp_path)
    raw["chapters"][0].update(start_clip=99,end_clip=2)
    raw["chapters"][1].update(start_clip=123,end_clip=160)
    proposal,errors,repairs=c.convert(raw,evidence)
    assert not errors and proposal is not None
    assert [ch["hero_frame_id"] for ch in proposal["chapters"]]==["frame1_1","frame3_1"]
    assert "C01:redundant_model_clip_bounds_ignored" in repairs
    assert "C02:redundant_model_clip_bounds_ignored" in repairs



def test_out_of_order_chapter_is_only_resequenced_not_regenerated(tmp_path):
    evidence,raw=sample(tmp_path)
    raw["chapters"][0].update(selected_images=[5,6],key_moments=[{"text":"商业街区", "image_index":5}])
    raw["chapters"][1].update(selected_images=[1,2],key_moments=[{"text":"海港码头", "image_index":1}])
    proposal,errors,repairs=c.convert(raw,evidence)
    assert not errors
    assert "chapters_reordered_by_verified_source_chronology" in repairs
    assert [z["title"] for z in proposal["chapters"]]==["城市商业街","海港与码头"]
    assert [z["id"] for z in proposal["chapters"]]==["C01","C02"]
    assert proposal["chapters"][0]["story"]==raw["chapters"][1]["story"]
    assert proposal["chapters"][1]["story"]==raw["chapters"][0]["story"]

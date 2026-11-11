"""Opt-in one-call Frozen V1 natural Chapter editor with strict Gallery admission.

Phone MobileCLIP and 3-second Live/Motion stay unchanged. The server uses the
same real JPEGs, preserves full V1 editorial principles and removes only numeric
Gallery quota cues. Unlike legacy compact.convert, every invalid original model
output is rejected BEFORE conversion: no trimming, dropping moments, reordering
or inferred attribution repair is permitted. An invalid first response may be
retried once, with the SAME prompt and same JPEGs. Never silently fallback to
Planner/Gallery or V03; default production editor remains unchanged.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import uuid
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator

from . import direct_vlm as direct, direct_vlm_compact as compact
from .x02 import StageModelGateway, StageRun, X02ExecutionError, X02ModelNotReady, X02StageCallError

PROFILE = "DIRECT_V1_NARRATIVE_NO_QUOTA_20261112"
GATE_VERSION = "V1_SINGLE_GALLERY_ADMISSION_20261112"
EXPERIMENT = "DIRECT_V1_SINGLE_QUALITY_RESEARCH_V01"
MAX_PUBLISHED_GALLERY = 8  # Existing, independently locked phone/BFF V01 contract.
MAX_ATTEMPTS = 2
RESOURCES = Path(__file__).parent / "v1_frozen_resources"
FROZEN_PROMPT_SHA = "9b510d4d1b660cb478198d79999644af8c56f175333fa9982ff5bfd644663259"
# These are the two historical numeric count cues, not new Chapter boundary rules.
OLD_RULE = ("- 不按固定时间、每章固定照片数或全日固定比例强行选图。"
            "每张入选图必须提供与其他入选图不同的具体信息价值。"
            "宁可少选，也不为达到 10–20 张而凑数；不可因为想填满 20 张而增加 Chapter。")
OLD_COUNT = ("每章 selected_images 是精心挑选的图库（包括封面），**20 张是允许的上限，不是必须达到的目标**。"
             "长章节有足够丰富且不同的真实场景时，可以选择约 10–20 张；短章只选真正有价值的图片，不准凑数。")
NEW_RULE = ("- 不按固定时间、每章固定照片数或全日固定比例强行选图。"
            "每张入选图必须提供与其他入选图不同的具体信息价值。"
            "仅根据内容信息增量决定图库数量，不将任何图库数量阈值理解成目标。")
NEW_COUNT = ("每章 selected_images 仅包含精心挑选的封面和互补图库，"
             "数量由该章真实经历的视觉信息决定；长章不自动多选，短章也不为了达到某个数量而凑图。")


def _frozen_baseline() -> str:
    path = RESOURCES / "frozen_v1_prompt.txt"
    b = path.read_bytes()
    if hashlib.sha256(b).hexdigest() != FROZEN_PROMPT_SHA:
        raise RuntimeError("Frozen V1 source prompt changed; refusing experiment")
    return b.decode("utf-8")


def model_prompt(image_count: int, clip_count: int) -> str:
    if not 1 <= image_count <= 250 or not 1 <= clip_count <= 250:
        raise ValueError("V1 editor input outside supported source evidence bounds")
    p = _frozen_baseline()
    assert p.count("输入共有 86 张 JPEG、55 个按时间排列的片段")==1
    assert p.count("IMAGE_INDEX_1_BASED（1 到 86）")==2
    assert p.count("CLIP_SEQUENCE_1_BASED（1 到 55）")==1
    p=p.replace("输入共有 86 张 JPEG、55 个按时间排列的片段",
                f"输入共有 {image_count} 张 JPEG、{clip_count} 个按时间排列的片段",1)
    p=p.replace("IMAGE_INDEX_1_BASED（1 到 86）",f"IMAGE_INDEX_1_BASED（1 到 {image_count}）")
    p=p.replace("CLIP_SEQUENCE_1_BASED（1 到 55）",f"CLIP_SEQUENCE_1_BASED（1 到 {clip_count}）")
    if p.count(OLD_RULE)!=1 or p.count(OLD_COUNT)!=1:
        raise RuntimeError("Frozen V1 quota sentences changed; refusing model call")
    p=p.replace(OLD_RULE,NEW_RULE,1).replace(OLD_COUNT,NEW_COUNT,1)
    if "10–20 张" in p or "**20 张" in p:
        raise RuntimeError("Numerical gallery target remains in user prompt")
    return p


def model_schema(image_count: int) -> dict[str,Any]:
    schema=json.loads((RESOURCES/"frozen_v1_model_schema.json").read_text())
    g=schema["properties"]["chapters"]["items"]["properties"]["selected_images"]
    if g.pop("maxItems")!=20:
        raise RuntimeError("Frozen V1 schema maximum changed")
    g["uniqueItems"]=True
    g["items"]["maximum"]=image_count
    schema["properties"]["chapters"]["items"]["properties"]["key_moments"]["items"]["properties"]["image_index"]["maximum"]=image_count
    schema["properties"]["excluded_images"]["items"]["maximum"]=image_count
    Draft202012Validator.check_schema(schema)
    return schema


def validate_editorial_gallery(raw: object, evidence: Sequence, *,
                               hard_gallery_limit: int = MAX_PUBLISHED_GALLERY) -> tuple[list[str],list[str],list[dict]]:
    """Pure fail-closed source reference check; NEVER mutates original output.

    Hard failures: unknown images, unbound moments, repeated Gallery IDs,
    source clip overlap, near-all input quota collapse, major unrepresented tail.
    Narrative correctness (work name, cover, story) requires independent image QA.
    """
    n=len(evidence)
    if not isinstance(raw,dict):
        return ["TOP_LEVEL_NOT_OBJECT"],[],[]
    schema=model_schema(n)
    errors=["/".join(map(str,e.absolute_path))+":"+e.validator
            for e in Draft202012Validator(schema).iter_errors(raw)]
    if errors:return sorted(set(errors)),[],[]
    if set(raw) - {"chapters", "excluded_images"}:
        errors.append("UNEXPECTED_TOP_LEVEL_FIELDS")
    chapters=raw["chapters"]
    clip_seq={}
    for asset,fr,_ in evidence:
        source=str(asset["asset_id"])
        if source not in clip_seq:clip_seq[source]=len(clip_seq)+1
    clips=len(clip_seq)
    source_seq=[clip_seq[str(asset["asset_id"])] for asset,_,_ in evidence]
    excluded=raw.get("excluded_images",[])
    if type(excluded)!=list:errors.append("EXCLUDED_NOT_LIST");excluded=[]
    used:set[int]=set()
    prev_end=0
    all_gallery=[]
    per_ch=[]
    warnings=[]
    max_block_run=0
    current_block_run=0
    for j,ch in enumerate(chapters,1):
        if set(ch) - {"title", "story", "selected_images", "key_moments"}:
            errors.append(f"C{j}:UNEXPECTED_CHAPTER_FIELDS")
        gallery=ch["selected_images"]
        if not 1<=len(gallery)<=hard_gallery_limit:
            errors.append(f"C{j}:PUBLISH_GALLERY_LIMIT:{len(gallery)}>{hard_gallery_limit}")
        if any(type(i) is not int or not 1<=i<=n for i in gallery):
            errors.append(f"C{j}:GALLERY_INDEX_INVALID")
            continue
        if len(set(gallery))!=len(gallery):
            errors.append(f"C{j}:REPEATED_GALLERY_IN_CHAPTER")
        if used.intersection(gallery):
            errors.append(f"C{j}:REUSED_GALLERY_ACROSS_CHAPTER")
        used.update(gallery)
        all_gallery+=gallery
        if any(i in excluded for i in gallery):
            errors.append(f"C{j}:EXCLUDED_PUBLISHED")
        moments=ch.get("key_moments")
        if not isinstance(moments,list) or not 1<=len(moments)<=10:
            errors.append(f"C{j}:MOMENT_CARDINALITY")
            moments=moments if isinstance(moments,list) else []
        valid=[]
        for k,m in enumerate(moments,1):
            if not isinstance(m,dict):
                errors.append(f"C{j}:INVALID_MOMENT_{k}");continue
            if set(m) - {"text", "image_index"}:
                errors.append(f"C{j}:UNEXPECTED_MOMENT_FIELDS_{k}")
            i=m.get("image_index")
            if type(i) is not int or not 1<=i<=n:
                errors.append(f"C{j}:MOMENT_INDEX_{k}_INVALID")
            elif i in excluded:
                errors.append(f"C{j}:MOMENT_EXCLUDED_{k}")
            else:
                valid.append(i)
            if not isinstance(m.get("text"),str) or len(m["text"].strip())<4:
                errors.append(f"C{j}:MOMENT_TEXT_INVALID")
        if ch["title"].strip()!=ch["title"] or ch["story"].strip()!=ch["story"]:
            errors.append(f"C{j}:TEXT_REQUIRES_NORMALIZATION")
        span=gallery+valid
        start=min(source_seq[i-1] for i in span)
        end=max(source_seq[i-1] for i in span)
        if start<=prev_end:
            errors.append(f"C{j}:CHAPTER_IMAGE_TIME_OVERLAP:{start}<=PREV_END_{prev_end}")
        prev_end=end
        contiguous=(len(gallery)>1 and all(b==a+1 for a,b in zip(gallery,gallery[1:])))
        if len(gallery)==hard_gallery_limit and contiguous:
            current_block_run+=1
            max_block_run=max(current_block_run,max_block_run)
        else:current_block_run=0
        per_ch.append({"chapter":j,"title":ch["title"],"start_clip":start,
                       "end_clip":end,"gallery_count":len(gallery),"cover_image_index":gallery[0],
                       "sequential_full_block":contiguous and len(gallery)==hard_gallery_limit})
    if any(type(i) is not int or not 1<=i<=n for i in excluded):
        errors.append("EXCLUDED_IMAGE_INDEX_INVALID")
    if len(excluded)!=len(set(map(str,excluded))):
        errors.append("EXCLUDED_IMAGE_REUSED")
    if set(excluded)&used:errors.append("EXCLUDED_IMAGE_PUBLISHED")
    if len(all_gallery)>=n*.75:
        warnings.append("PUBLISHED_AT_LEAST_75_PERCENT_OF_ALL_JPEG")
    if max_block_run>=3:
        errors.append("GALLERY_MECHANICAL_CONSECUTIVE_FULL_BLOCKS")
    if per_ch:
        tail=clips-per_ch[-1]["end_clip"]
        head=per_ch[0]["start_clip"]-1
        if tail>=max(1,math.ceil(clips*.20)):
            errors.append(f"LAST_20_PERCENT_OF_CLIPS_NOT_REPRESENTED:{tail}")
        if head>=max(1,math.ceil(clips*.20)):
            errors.append(f"FIRST_20_PERCENT_OF_CLIPS_NOT_REPRESENTED:{head}")
        selected_clips={source_seq[i-1] for i in all_gallery}
        bins={min(9,int((i-1)*10/clips)) for i in selected_clips}
        if len(bins)<6:warnings.append(f"LOW_TIMELINE_BIN_RECALL:{len(bins)}/10")
    return sorted(set(errors)),warnings,per_ch


def _audit_private(folder:Path|None,number:int,run:StageRun,errors,notes):
    if folder is None:return
    folder.mkdir(parents=True,exist_ok=True,mode=0o700)
    folder.chmod(0o700)
    dest=folder/f"attempt_{number:02d}.json"
    obj={"attempt":number,"protocol":PROFILE,"model":run.model,
         "provider":run.provider,"request_id":run.request_id,
         "input_tokens":run.input_tokens,"output_tokens":run.output_tokens,
         "cost_native":run.estimated_cost_native,
         "validation_errors":errors,"warnings":notes,
         "model_output_raw":run.output}
    fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,"w") as f:json.dump(obj,f,ensure_ascii=False,indent=2)


def _fail(code:str,why:str,runs):
    raise X02ExecutionError(why,stage="DIRECT_V1_SINGLE_QUALITY",code=code,stage_runs=runs)


def run_direct_v1_quality(manifest_path:Path,gateway:StageModelGateway,
                          *,audit_dir:Path|None=None)->dict:
    if not gateway.ready:
        raise X02ModelNotReady("V1 quality editor requires a configured real image VLM")
    bundle,evidence,owners,total_bytes=direct.prepare_evidence(manifest_path)
    prompt=model_prompt(len(evidence),len(bundle.manifest["assets"]))
    schema=model_schema(len(evidence))
    budget=direct._positive_float_env("DIARY_ONE_V1_SINGLE_BUDGET_CNY",1.20)
    labels=compact.image_labels(evidence,direct.frame_chronology_labels(evidence))
    runs=[]
    errors_by_attempt=[]
    for attempt in range(1,MAX_ATTEMPTS+1):
        try:
            run=gateway.call(direct.STAGE,prompt,schema,evidence=evidence,context={
              "_audit_stage_failures":True,
              "_x02_policy_version":"V04_1",
              "_direct_vlm_frame_chronology":labels,
              "_direct_vlm_compact":True})
        except X02StageCallError as exc:
            runs.append(exc.stage_run)
            _audit_private(audit_dir,len(runs),exc.stage_run,[exc.code],[])
            _fail(exc.code,"Real model provider request failed",runs)
        except Exception as exc:
            _fail("V1_SINGLE_TRANSPORT_FAILED",type(exc).__name__,runs)
        runs.append(run)
        if sum(x.estimated_cost_native for x in runs)>budget:
            _audit_private(audit_dir,len(runs),run,["BUDGET_EXCEEDED"],[])
            _fail("V1_SINGLE_BUDGET_EXCEEDED","Actual API cost exceeds configured day cap",runs)
        errors,warnings,per_ch=validate_editorial_gallery(run.output,evidence)
        proposal=None
        repairs=[]
        if not errors:
            proposal,conversion_errors,repairs=compact.convert(run.output,evidence,
                        max_gallery=MAX_PUBLISHED_GALLERY)
            if conversion_errors:errors+=conversion_errors
            if repairs:errors+=["FORBIDDEN_SILENT_CONVERTER_REPAIR:"+x for x in repairs]
            if proposal is not None and not errors:
                errors+=direct.validate_proposal(proposal,owners)
        _audit_private(audit_dir,len(runs),run,errors,warnings)
        if not errors and proposal is not None:
            result=direct.build_result(proposal,bundle,owners,runs,
                        total_bytes=total_bytes,attempt_errors=errors_by_attempt)
            result["experiment"]=EXPERIMENT
            result["decision_trace"].update({
              "editorial_profile":PROFILE,"gallery_quality_gate":GATE_VERSION,
              "model_output_no_silent_truncation":True,
              "gallery_repair_count":0,
              "prompt_sha256":hashlib.sha256(prompt.encode()).hexdigest(),
              "hard_published_gallery_limit":MAX_PUBLISHED_GALLERY,
              "gallery_quality_warnings":warnings,
              "model_input_gallery_max_items":None,
              "scene_naming_and_cover_semantics_certified":False,
              "chapter_gallery_clip_spans":per_ch,
            })
            return result
        errors_by_attempt.append(errors)
    _fail("V1_SINGLE_GALLERY_QUALITY_REJECTED",
          ";".join(errors_by_attempt[-1][:6]),runs)

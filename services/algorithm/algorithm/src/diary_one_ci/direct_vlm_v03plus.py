"""V03+ selective V04 rules; exact original V03 one-call image protocol.

Research opt-in only. The original V03 prompt, schema and router stay unchanged.
New instructions are ADDITIVE and bounded (complete experience, hero/coverage,
distinct artwork/activity evidence, conservative names, simplified Chinese).
NO V04 20-photo quota, GPS boilerplate, extra model translation, or global
round-robin truncation. The original chosen gallery and Story never get edited.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator
from . import direct_vlm as direct
from . import direct_vlm_compact as compact
from .x02 import StageModelGateway, StageRun, X02ExecutionError, X02ModelNotReady, X02StageCallError

PROTOCOL = "DIRECT_VLM_COMPACT_EDITOR_V03_PLUS_SELECTIVE_V04_20261112"
EXPERIMENT = "DIRECT_VLM_V03PLUS_ONECALL_EXPERIMENT_20261112"
GATE = "V03PLUS_SOURCE_BOUND_GALLERY_V01"
MAX_SELECTED = 8            # same hard max as ORIGINAL V03
MAX_MODEL_CALLS = 2          # baseline V03 behavior: one call, at most one retry
ADDITIONS = """\

【补充编辑原则（保持原版V03的单次全局决策及输出结构）】
- Chapter 代表一段按真实先后发生的完整经历；短暂路过一个建筑、看到一个新作品，不自动拆章。不同的独立经历也不能因为景物相似就强行合并。
- 先理解这一章的主要经历，再选图片。每章仍建议 3–6 张，最多 8 张；这是上限而非配额，少量独特画面可少选，绝不因为图库容量而凑数。
- selected_images 第一张必须是该章最能说明主题的封面；其他图须有不同的信息角色，例如空间环境、关键活动或作品、独特细节、经历推进与自然收束。普通道路、类似步道、同场景反复拍摄只选有明显信息增量的图。
- 重要但短暂的真实活动、动物、地标或艺术作品不能仅因画面少而遗漏。具体名称仅在图片或清晰铭牌足以支持时才写入 Story 或 key_moments；无法确认身份就客观描述，严禁凭地点和常识猜测作品。
- 每章所选图与 key_moments 必须真实属于这一段经历，而不是后面其他章；同一原视频片段不要跨章重复归属。连续经历中的不同画作是章内内容而不是强制分章点。
- title、story、key_moments.text 使用自然简体中文，允许准确的英文专名括注；保持真正的参观、游玩经历叙事，避免“画面出现、镜头转向”的逐图说明口吻。
"""


MINIMAL_ADDITIONS = """

【精选视觉证据与中文表达：不改变V03原有分章标准】
- 先按前述时间、地点与活动变化判断Chapter；不要因为加入选图要求而新增或合并Chapter。
- 第一个 selected_images 应是真正代表本章主要经历的清晰封面；其余图片只选有新信息的环境、重要活动、独特物件或场景推进，不重复普通道路和同景连拍，也不把其他经历的照片混入本章。
- 如清晰看到重要艺术品、建筑、动物或短暂活动，应在相应Chapter保留信息；具体名称须有可靠视觉证据，不能凭所在城市猜。
- title、story、key_moments.text 用自然简体中文，准确英文专名可括注，不写成逐帧的镜头说明。
"""


def prompt(*, image_count: int, clip_count: int) -> str:
    """Exactly frozen V03 prompt + the six compact, selective V04-derived rules."""
    p = compact.prompt(image_count=image_count, clip_count=clip_count)
    expected = "每章的 selected_images 是该章代表性的真实图片序号，建议 3-6 张，最多 8 张。"
    if p.count(expected) != 1 or p.count("【输出只需要编辑决策，程序负责所有引用转换】") != 1:
        raise RuntimeError("Original V03 prompt changed: refuse silently drifting baseline")
    assert "10–20 张" not in ADDITIONS and "20 张" not in ADDITIONS
    return p.replace("\n【输出只需要编辑决策，程序负责所有引用转换】",
                     ADDITIONS+"\n【输出只需要编辑决策，程序负责所有引用转换】", 1)


def prompt_minimal(*, image_count: int, clip_count: int) -> str:
    """Selective 4-rule addition, keeping all original V03 Chapter rules."""
    p=compact.prompt(image_count=image_count,clip_count=clip_count)
    before="\n【输出只需要编辑决策，程序负责所有引用转换】"
    if p.count(before)!=1:
        raise RuntimeError("V03 baseline prompt marker drift")
    return p.replace(before,MINIMAL_ADDITIONS+before,1)


def prompt_minimal_chrono(*, image_count:int, clip_count:int)->str:
    """Only one source-chronology cue beyond minimal V03+."""
    p=prompt_minimal(image_count=image_count,clip_count=clip_count)
    extra=(
      "- 真实拍摄时间先后是章节归属的硬约束。每一章的图库和关键瞬间应来自本章连续经历，"
      "不能把下一段经历的图片提前选入本章；后章的最早入选图片来源Clip应晚于前章最晚的图库或关键瞬间来源Clip。"
      "不要为了符合约束而机械按编号切分图库。\n"
    )
    marker="\n【输出只需要编辑决策，程序负责所有引用转换】"
    assert p.count(marker)==1
    return p.replace(marker,"\n"+extra+marker,1)


def _image_to_clip(evidence: Sequence) -> list[int]:
    asset_seen: dict[str,int] = {}
    clip_order: list[int] = []
    for asset, _, _ in evidence:
        assetid = str(asset["asset_id"])
        if assetid not in asset_seen:
            asset_seen[assetid] = len(asset_seen)+1
        clip_order.append(asset_seen[assetid])
    return clip_order


def validate_raw(raw: object, evidence: Sequence) -> tuple[list[str], list[str], list[dict]]:
    """Structural and provenance gates. No semantic truth claim, no mutation."""
    n=len(evidence)
    if not isinstance(raw,dict):
        return ["TOP_LEVEL_NOT_OBJECT"], [], []
    # Keep exactly the ORIGINAL V03 output schema as one controlled factor.
    errors=["/".join(map(str,issue.absolute_path))+":"+str(issue.validator)
            for issue in Draft202012Validator(compact.SCHEMA).iter_errors(raw)]
    if errors:
        return sorted(set(errors)), [], []
    if set(raw)-{"chapters","excluded_images"}:
        errors.append("UNKNOWN_TOP_LEVEL_FIELDS")
    rows=raw["chapters"]
    if not isinstance(rows,list) or not 1<=len(rows)<=compact.MAX_CHAPTERS:
        return ["INVALID_CHAPTER_COUNT"], [], []
    img_clip=_image_to_clip(evidence)
    count=max(img_clip) if img_clip else 0
    used:set[int]=set()
    spans=[]
    trace=[]
    warnings=[]
    excluded=raw.get("excluded_images",[])
    if not isinstance(excluded,list):
        return ["EXCLUDED_IMAGES_NOT_LIST"], [], []
    if any(type(i)!=int or not 1<=i<=n for i in excluded):
        errors.append("EXCLUDED_INDEX_NOT_IN_INPUT")
    if len(excluded)!=len(set(str(i) for i in excluded)):
        errors.append("DUPLICATE_EXCLUDED_INDEX")
    maxsaturated=0
    for seq,row in enumerate(rows,1):
        if not isinstance(row,dict):
            errors.append(f"C{seq}:NOT_OBJECT")
            continue
        prefix=f"C{seq}"
        if set(row)-{"title","story","selected_images","key_moments"}:
            errors.append(prefix+":UNKNOWN_FIELDS")
        title,story=row.get("title"),row.get("story")
        if not isinstance(title,str) or len(title.strip())<2:
            errors.append(prefix+":TITLE_INVALID")
        if not isinstance(story,str) or len(story.strip())<12:
            errors.append(prefix+":STORY_INVALID")
        if (isinstance(title,str) and title != title.strip()) or (isinstance(story,str) and story != story.strip()):
            errors.append(prefix+":TEXT_NEEDS_SILENT_NORMALIZATION")
        # V04's useful zh-Hans requirement, without a SECOND model invocation.
        for key,value,minimum in (("title",title,2),("story",story,8)):
            if isinstance(value,str) and sum('\u3400'<=c<='\u9fff' for c in value)<minimum:
                errors.append(prefix+":"+key+"_NOT_CHINESE")
        picks=row.get("selected_images")
        if not isinstance(picks,list) or not 1<=len(picks)<=MAX_SELECTED:
            errors.append(prefix+":GALLERY_CARDINALITY")
            picks=picks if isinstance(picks,list) else []
        if len(picks)!=len(set(str(x) for x in picks)):
            errors.append(prefix+":DUPLICATE_SELECTED_IMAGES")
        if any(type(i)!=int or not 1<=i<=n for i in picks):
            errors.append(prefix+":INVALID_GALLERY_IMAGE")
        valid_picks=[i for i in picks if type(i)==int and 1<=i<=n]
        if set(valid_picks)&used:
            errors.append(prefix+":REUSED_GALLERY_ACROSS_CHAPTERS")
        used.update(valid_picks)
        if set(valid_picks)&set(excluded):
            errors.append(prefix+":GALLERY_EXCLUDED")
        moments=row.get("key_moments")
        if not isinstance(moments,list) or not 1<=len(moments)<=10:
            errors.append(prefix+":KEY_MOMENTS_CARDINALITY")
            moments=moments if isinstance(moments,list) else []
        moment_ids=[]
        for mindex,moment in enumerate(moments,1):
            if not isinstance(moment,dict) or set(moment)-{"text","image_index"}:
                errors.append(prefix+f":INVALID_MOMENT_STRUCTURE_{mindex}")
                continue
            mi=moment.get("image_index")
            t=moment.get("text")
            if type(mi)!=int or not 1<=mi<=n or mi in excluded:
                errors.append(prefix+f":INVALID_MOMENT_INDEX_{mindex}")
            else:
                moment_ids.append(mi)
            if not isinstance(t,str) or sum('\u3400'<=c<='\u9fff' for c in t)<2:
                errors.append(prefix+f":INVALID_MOMENT_TEXT_{mindex}")
        src=[img_clip[i-1] for i in valid_picks+moment_ids]
        if src:
            span=(min(src),max(src))
            spans.append(span)
        else:
            span=None
        if (len(picks)==MAX_SELECTED
           and len(picks)>1
           and all(type(a)==int and type(b)==int and b==a+1
                   for a,b in zip(picks,picks[1:]))):
            maxsaturated+=1
        trace.append({"chapter":seq,"title":title,"image_count":len(picks),
                      "source_clip_span":span,
                      "image_indices":picks,
                      "cover":picks[0] if picks else None})
    for i in range(1,len(spans)):
        if spans[i][0]<=spans[i-1][1]:
            errors.append(f"C{i+1}:CHAPTER_SOURCE_CLIP_OVERLAP")
    if maxsaturated>=3:
        errors.append("MULTIPLE_CHAPTERS_MECHANICALLY_FILL_EIGHT_IN_SEQUENCE")
    if len(used)>=n*.75 and n>=60:
        errors.append("SELECTED_NEAR_ALL_SOURCE_JPEGS")
    if spans and count:
        if count-spans[-1][1]>=max(3,math.ceil(count*.20)):
            errors.append("LAST_FIFTH_OF_DAY_NOT_REPRESENTED")
        if spans[0][0]-1>=max(3,math.ceil(count*.20)):
            errors.append("FIRST_FIFTH_OF_DAY_NOT_REPRESENTED")
        # No fixed quota per timeline bin; low coverage is a warning, not
        # a semantic proof of missing important content.
        present={img_clip[i-1] for i in used}
        bins={min(9,(clip-1)*10//count) for clip in present}
        if len(bins)<6:
            warnings.append(f"TIMELINE_GALLERY_COVERS_ONLY_{len(bins)}_OF_10_BINS")
    return sorted(set(errors)),warnings,trace


def _explicit_evidence_only(proposal:dict)->dict:
    """Prevent old converter from claiming every unselected image in clip span."""
    out=copy.deepcopy(proposal)
    for ch in out["chapters"]:
        chosen=ch["gallery_frame_ids"]
        moments=[fid for row in ch["key_moments"] for fid in row["frame_ids"]]
        ch["experience_frame_ids"]=list(dict.fromkeys([*chosen,*moments]))
    return out


def _audit(folder:Path|None,attempt:int,run:StageRun,errors,warnings,trace)->None:
    if folder is None:
        return
    folder.mkdir(parents=True,exist_ok=True,mode=0o700)
    folder.chmod(0o700)
    file=folder/f"v03plus_attempt_{attempt:02d}.json"
    fd=os.open(file,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,"w") as out:
            json.dump({
               "attempt":attempt,"model":run.model,"request_id":run.request_id,
               "input_tokens":run.input_tokens,"output_tokens":run.output_tokens,
               "estimated_cost_native":run.estimated_cost_native,
               "raw_model_output":run.output,"errors":errors,
               "warnings":warnings,"chapter_evidence":trace
            },out,ensure_ascii=False,indent=2)
    except:
        file.unlink(missing_ok=True)
        raise


def run_direct_vlm_v03plus(manifest_path:Path,gateway:StageModelGateway,
                           *,audit_dir:Path|None=None,
                           prompt_variant:str="minimal")->dict:
    """Same single global Qwen request interface and old result schema."""
    if not gateway.ready:
        raise X02ModelNotReady("V03+ requires model credentials on server")
    bundle,evidence,owners,total_bytes=direct.prepare_evidence(manifest_path)
    clip_count=len(bundle.manifest["assets"])
    labels=compact.image_labels(evidence,direct.frame_chronology_labels(evidence))
    # Billing preflight is required even for research retries.
    budget=direct._positive_float_env("DIARY_ONE_DIRECT_V03PLUS_BUDGET_CNY",1.20)
    adapter=getattr(gateway,"adapter",None)
    if adapter is not None:
        conservative_input=len(evidence)*800+12000
        conservative_output=5000
        projected=MAX_MODEL_CALLS*(
            conservative_input*adapter.input_rate_per_million+
            conservative_output*adapter.output_rate_per_million)/1_000_000
        if projected>budget:
            raise X02ExecutionError("V03+ request exceeds model billing budget preflight",
                stage=direct.STAGE,code="V03PLUS_BUDGET_PREFLIGHT",stage_runs=[])
    variants={"minimal":prompt_minimal,"minimal_chrono":prompt_minimal_chrono,"full":prompt}
    if prompt_variant not in variants:
        raise ValueError("Unknown V03+ prompt variant")
    p=variants[prompt_variant](image_count=len(evidence),clip_count=clip_count)
    runs=[]
    allerrors=[]
    for attempt in range(1,MAX_MODEL_CALLS+1):
        try:
            run=gateway.call(direct.STAGE,p,compact.SCHEMA,evidence=evidence,
               context={"_audit_stage_failures":True,"_x02_policy_version":"V04_1",
                        "_direct_vlm_frame_chronology":labels,
                        "_direct_vlm_compact":True})
        except X02StageCallError as e:
            raise X02ExecutionError("V03+ transport/provider failed",stage=direct.STAGE,
                                    code=e.code,stage_runs=[*runs,e.stage_run]) from e
        runs.append(run)
        if sum(x.estimated_cost_native for x in runs)>budget:
            raise X02ExecutionError("V03+ actual model calls exceeded budget",
               stage=direct.STAGE,code="V03PLUS_BUDGET_EXCEEDED",stage_runs=runs)
        errors,warnings,trace=validate_raw(run.output,evidence)
        proposal=None;repairs=[]
        if not errors:
            proposal,conversion_errs,repairs=compact.convert(run.output,evidence)
            errors.extend(conversion_errs)
            if repairs:
                errors.extend("FORBIDDEN_CONVERTER_REPAIR:"+x for x in repairs)
            if proposal is not None and not errors:
                proposal=_explicit_evidence_only(proposal)
                errors.extend(direct.validate_proposal(proposal,owners))
        _audit(audit_dir,attempt,run,errors,warnings,trace)
        if not errors and proposal is not None:
            result=direct.build_result(proposal,bundle,owners,runs,
                total_bytes=total_bytes,attempt_errors=allerrors)
            result["experiment"]=EXPERIMENT
            result["decision_trace"].update({
               "compact_model_protocol":PROTOCOL,
               "source": "FROZEN_V03_PROMPT_PLUS_SELECTIVE_V04_RULES",
               "prompt_variant":prompt_variant,
               "prompt_sha256":hashlib.sha256(p.encode()).hexdigest(),
               "gallery_limit":MAX_SELECTED,
               "gallery_quality_gate":GATE,
               "gallery_structural_verified":True,
               "gallery_semantic_verified":False,
               "chapter_visual_fact_reviewed":False,
               "no_silent_truncation_or_order_repair":True,
               "explicit_selected_frame_lineage_only":True,
               "chapter_evidence":trace,
               "quality_warnings":warnings,
            })
            return result
        allerrors.append(errors)
    raise X02ExecutionError("V03+ quality gate rejected original output: "+";".join(allerrors[-1][:8]),
                            stage=direct.STAGE,
                            code="DIRECT_V03PLUS_OUTPUT_REJECTED",
                            stage_runs=runs)

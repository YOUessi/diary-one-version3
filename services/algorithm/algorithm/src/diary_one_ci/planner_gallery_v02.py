"""Opt-in Chapter Planner -> physically scoped per-Chapter Gallery V02.

Default Direct VLM remains untouched. The model decides chapter topics, stories
and ordered end_clip boundaries; deterministic code owns exclusive clip
intervals and exact JPEG identity. Every gallery call sees ONLY JPEGs assigned
to its chapter. Invalid model output is never silently repaired or published.

The input is the existing phone-selected Bundle V04/V05 JPEG evidence: this
module does not change MobileCLIP selection or the phone's Live/Motion export.
"""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator

from . import direct_vlm as old
from . import direct_vlm_compact as compact
from .x02 import StageModelGateway, StageRun, X02ExecutionError, X02ModelNotReady, X02StageCallError

SCHEMA_VERSION = "DIARY_ONE_PLANNER_GALLERY_CHAPTER_V02"
PIPELINE_VERSION = "X02_PLANNER_GALLERY_CHAPTER_V02"
EDITOR_POLICY = "PLANNER_GALLERY_SCOPED_EDITOR_V02"
PLAN_STAGE = "DIRECT_VLM_CHAPTER_PLANNER_V02"
GALLERY_STAGE = "DIRECT_VLM_CHAPTER_GALLERY_V02"
MODEL_PROTOCOL = "PLANNER_GALLERY_PHYSICAL_SCOPE_V02"

MAX_CHAPTERS = 14
MAX_GALLERY = 20
MAX_MOMENTS = 10
MAX_PER_STAGE_ATTEMPTS = 2
MAX_MODEL_CALLS = (MAX_CHAPTERS + 1) * MAX_PER_STAGE_ATTEMPTS


def _schema_failures(value: object, schema: Mapping[str, Any]) -> list[str]:
    return ["/".join(map(str, issue.absolute_path)) + ":" + issue.validator
            for issue in Draft202012Validator(schema).iter_errors(value)]


def planner_schema(image_count: int, clip_count: int) -> dict[str, Any]:
    return {
        "type": "object", "additionalProperties": False,
        "required": ["chapters", "excluded_images"],
        "properties": {
            "chapters": {
                "type": "array", "minItems": 1, "maxItems": MAX_CHAPTERS,
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["title", "story", "end_clip"],
                    "properties": {
                        "title": {"type": "string", "minLength": 2, "maxLength": 80},
                        "story": {"type": "string", "minLength": 12, "maxLength": 1800},
                        "end_clip": {"type": "integer", "minimum": 1, "maximum": clip_count},
                    },
                },
            },
            "excluded_images": {
                "type": "array", "uniqueItems": True, "maxItems": image_count,
                "items": {"type": "integer", "minimum": 1, "maximum": image_count},
            },
        },
    }


def gallery_schema(image_count: int) -> dict[str, Any]:
    return {
        "type": "object", "additionalProperties": False,
        "required": ["selected_images", "key_moments"],
        "properties": {
            "selected_images": {
                "type": "array", "minItems": 1, "maxItems": min(MAX_GALLERY, image_count),
                "uniqueItems": True, "items": {"type": "integer", "minimum": 1, "maximum": image_count},
            },
            "key_moments": {
                "type": "array", "minItems": 1, "maxItems": MAX_MOMENTS,
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["text", "image_index"],
                    "properties": {
                        "text": {"type": "string", "minLength": 4, "maxLength": 300},
                        "image_index": {"type": "integer", "minimum": 1, "maximum": image_count},
                    },
                },
            },
        },
    }


def _has_chinese(value: object, *, short: bool) -> bool:
    if not isinstance(value, str):
        return False
    han = sum("\u3400" <= x <= "\u9fff" for x in value)
    latin = sum(x.isascii() and x.isalpha() for x in value)
    return han >= (2 if short else 8) and (
        short or latin <= 30 or han / max(1, han + latin) >= 0.13
    )


def planner_prompt(*, image_count: int, clip_count: int, retry: bool = False) -> str:
    # Frozen V1 editorial principles, reduced to chapter planning only.
    result = (
        f"你是第一人称生活记录的全局 Chapter 规划者。输入 {image_count} 张实际 JPEG，"
        f"来自时间顺序明确的 {clip_count} 个原始片段。\n"
        "图片提供 IMAGE_INDEX_1_BASED 和 CLIP_SEQUENCE_1_BASED；源片段内时间不是一天中的时钟。\n"
        "先看完全部图片，再按连续完整的经历划 Chapter。真正的主要地点或活动变化可产生新章；"
        "同一次关联经历不必按地标逐个拆章，不因都是 Citywalk 就合并不同经历。"
        "不预设章数或强行按时间等长拆分。短暂独特事件也应在 Story 中保留。\n"
        "只凭画面证明事实。不要猜测作品名、主观情绪、购买行为、星期或夕阳时间。"
        "非实录的片头总结/地图/广告可列在 excluded_images，普通重复实录不能排除。\n"
        "本阶段只输出每章 title、story、end_clip；不选择封面或图库。"
        "end_clip 是本章最后一个 CLIP_SEQUENCE_1_BASED，必须严格递增。"
        f"第1章从片段1开始；最后一章 end_clip 必须为 {clip_count}。"
        "程序负责根据这些边界计算每章唯一连续的图片归属。\n"
        "标题和正文使用简体中文，准确英文专名可括号保留。只返回 JSON 对象，"
        '例如 {"chapters":[{"title":"...","story":"...","end_clip":1}],"excluded_images":[]}。'
    )
    if retry:
        result += "\n之前的结构未通过机器合同校验。本次严格遵守现有 JSON 字段和尾段归属。"
    return result


def gallery_prompt(*, title: str, story: str, chapter_index: int,
                   start_clip: int, end_clip: int, image_count: int,
                   retry: bool = False) -> str:
    # Gallery receives NO other Chapter images; local numbering is 1..N.
    result = (
        f"你是第 {chapter_index} 章的图库编辑。该章已确定为原始片段 {start_clip} 至 {end_clip}。"
        f"标题：{title}\n正文：{story}\n"
        f"此次只提供本章实际的 {image_count} 张 JPEG；IMAGE_INDEX_1_BASED 从 1 重新编号，"
        "和其他章节编号无关。请看图决定首张封面、互补图库和关键瞬间。\n"
        "每张入选图需有不同的信息价值；优先地点/活动建立画面、关键主体、独特细节、"
        "场景变化及清晰构图，不凑图、不因时间相隔就误当不同经历。"
        "首个 selected_images 是封面，短章可以只保留少量图片，"
        "每章最多20张。不能杜撰没展示的图片、作品或活动。\n"
        "只返回 selected_images 和 key_moments，"
        '例如 {"selected_images":[1],"key_moments":[{"text":"现场可见的活动","image_index":1}]}。'
        "所有图片编号都只能引用本次提供的局部 IMAGE_INDEX_1_BASED，"
        "Key Moment 文本使用简体中文。"
    )
    if retry:
        result += "\n上一次图库 JSON 或引用不合法；保持已有 Chapter，不添加图片，不改事实。"
    return result


def _source_sequences(evidence):
    sources: dict[str, int] = {}
    for asset, _, _ in evidence:
        source = str(asset["asset_id"])
        sources.setdefault(source, len(sources) + 1)
    return sources


def validate_plan(raw: object, evidence: Sequence, clip_count: int) -> tuple[list[dict], set[int], list[str]]:
    n = len(evidence)
    failures = _schema_failures(raw, planner_schema(n, clip_count))
    if failures:
        return [], set(), failures
    assert isinstance(raw, dict)
    excluded = set(raw["excluded_images"])
    chapters = raw["chapters"]
    ends = [chapter["end_clip"] for chapter in chapters]
    if any(type(end) is not int for end in ends):
        failures.append("end_clip_not_integer")
    elif any(end <= left for left, end in zip([0] + ends[:-1], ends)):
        failures.append("chapter_end_not_strictly_increasing")
    if not ends or ends[-1] != clip_count:
        failures.append("last_end_clip_must_cover_all_input")
    mapping = _source_sequences(evidence)
    intervals: list[dict] = []
    start = 1
    if not failures:
        for idx, chapter in enumerate(chapters, 1):
            end = chapter["end_clip"]
            if not _has_chinese(chapter["title"], short=True) or not _has_chinese(chapter["story"], short=False):
                failures.append(f"C{idx:02d}:not_zh_CN")
            eligible = [i for i, (a, _, _) in enumerate(evidence, 1)
                        if start <= mapping[str(a["asset_id"])] <= end and i not in excluded]
            if not eligible:
                failures.append(f"C{idx:02d}:no_selectable_jpeg")
            intervals.append({"id": f"C{idx:02d}", "title": chapter["title"],
                              "story": chapter["story"], "start_clip": start,
                              "end_clip": end, "image_indices": eligible})
            start = end + 1
    return intervals, excluded, failures


def validate_gallery(raw: object, local_count: int) -> list[str]:
    errors = _schema_failures(raw, gallery_schema(local_count))
    if errors or not isinstance(raw, dict):
        return errors or ["gallery_not_object"]
    if any(not _has_chinese(moment["text"], short=True) for moment in raw["key_moments"]):
        errors.append("key_moments_must_be_zh_CN")
    return errors


def _audit_raw(directory: Path | None, attempt: int, *, run: StageRun, errors: Sequence[str]) -> None:
    if directory is None:
        return
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory.chmod(0o700)
    dst = directory / f"attempt_{attempt:02d}.json"
    data = json.dumps({
        "attempt": attempt, "stage": run.stage, "request_id": run.request_id,
        "provider": run.provider, "model": run.model,
        "model_frame_count": run.model_frame_count,
        "input_tokens": run.input_tokens, "output_tokens": run.output_tokens,
        "estimated_cost_native": run.estimated_cost_native,
        "validation_errors": list(errors), "model_output": run.output,
    }, ensure_ascii=False, indent=2).encode("utf-8")
    fd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)


def _fail(code: str, why: str, runs: Sequence[StageRun]) -> None:
    raise X02ExecutionError(why, stage="PLANNER_GALLERY_V02", code=code, stage_runs=runs)


def _safe_call(gateway: StageModelGateway, stage: str, prompt: str, schema: dict, evidence,
               labels: Mapping[str, str], runs: list[StageRun],
               max_budget_cny: float, audit_dir: Path | None) -> StageRun:
    if len(runs) >= MAX_MODEL_CALLS:
        _fail("PLANNER_GALLERY_CALL_LIMIT", "Model-call budget exhausted", runs)
    try:
        response = gateway.call(
            stage, prompt, schema, evidence=evidence,
            context={"_audit_stage_failures": True, "_x02_policy_version": "V04_1",
                     "_direct_vlm_compact": True, "_direct_vlm_frame_chronology": dict(labels)},
        )
    except X02StageCallError as exc:
        runs.append(exc.stage_run)
        _audit_raw(audit_dir, len(runs), run=exc.stage_run, errors=[exc.code])
        _fail(exc.code, "Provider request failed: " + exc.code, runs)
    except Exception as exc:
        _fail("PLANNER_GALLERY_TRANSPORT_FAILURE", type(exc).__name__, runs)
    runs.append(response)
    if sum(run.estimated_cost_native for run in runs) > max_budget_cny:
        _audit_raw(audit_dir, len(runs), run=response, errors=["cumulative_model_budget_exceeded"])
        _fail("PLANNER_GALLERY_BUDGET_EXCEEDED", "Real API usage exceeded per-day cap", runs)
    return response


def _proposal_from_gallery(intervals: list[dict], galleries: list[dict], evidence,
                           excluded: set[int]) -> dict:
    rows = []
    for chapter, gallery in zip(intervals, galleries, strict=True):
        eligible = chapter["image_indices"]
        selected = [eligible[i - 1] for i in gallery["selected_images"]]
        moments = [(x["text"], eligible[x["image_index"] - 1]) for x in gallery["key_moments"]]
        frame_id = lambda i: str(evidence[i - 1][1]["frame_id"])
        rows.append({
            "id": chapter["id"], "title": chapter["title"], "story": chapter["story"],
            "hero_frame_id": frame_id(selected[0]),
            "gallery_frame_ids": [frame_id(i) for i in selected],
            "experience_frame_ids": [frame_id(i) for i in eligible],
            "key_moments": [{"description": text, "frame_ids": [frame_id(i)]} for text, i in moments],
            "editorial_summary": (f"时间范围 {chapter['start_clip']} 至 {chapter['end_clip']} 源片段；"
                                  "图库只来自该区间，图片由独立 VLM 选择。"),
        })
    return {
        "schema_version": old.MODEL_SCHEMA_VERSION,
        "day_summary": ("当天按顺序记录了：" + "、".join(ch["title"] for ch in intervals))[:1600],
        "chapter_count_rationale": (f"根据实际图像时间线规划 {len(intervals)} 个连续经历 Chapter。"),
        "excluded_non_lived_frame_ids": [str(evidence[i - 1][1]["frame_id"]) for i in sorted(excluded)],
        "chapters": rows,
    }


def run_planner_gallery(manifest_path: Path, gateway: StageModelGateway,
                        *, audit_dir: Path | None = None) -> dict:
    """Opt-in real two-stage calls, fail-closed. Never auto-fallback to V01."""
    if not gateway.ready:
        raise X02ModelNotReady("Planner/Gallery requires a configured real VLM model")
    bundle, evidence, owners, total_bytes = old.prepare_evidence(manifest_path)
    clip_count = len(bundle.manifest["assets"])
    image_count = len(evidence)
    budget = old._positive_float_env("DIARY_ONE_PLANNER_GALLERY_BUDGET_CNY", 1.20)
    audit_folder = Path(audit_dir) / str(bundle.manifest["session"]["session_id"]) if audit_dir else None
    runs: list[StageRun] = []
    failures: list[list[str]] = []
    full_chronology = old.frame_chronology_labels(evidence)
    labels = compact.image_labels(evidence, full_chronology)
    intervals: list[dict] = []
    excluded: set[int] = set()
    plan_raw = None
    for attempt in range(MAX_PER_STAGE_ATTEMPTS):
        response = _safe_call(gateway, PLAN_STAGE, planner_prompt(
            image_count=image_count, clip_count=clip_count, retry=attempt > 0),
            planner_schema(image_count, clip_count), evidence, labels, runs, budget, audit_folder)
        intervals, excluded, issues = validate_plan(response.output, evidence, clip_count)
        _audit_raw(audit_folder, len(runs), run=response, errors=issues)
        if not issues:
            plan_raw = response.output
            break
        failures.append(issues)
    if plan_raw is None:
        _fail("PLANNER_GALLERY_PLAN_INVALID", ";".join(failures[-1][:6]), runs)

    all_galleries = []
    for chapter in intervals:
        subset = [evidence[i - 1] for i in chapter["image_indices"]]
        # Local IMAGE_INDEX, but globally authoritative CLIP_SEQUENCE: never
        # renumber source clips when physically filtering chapter evidence.
        sublabels = compact.image_labels(subset, full_chronology)
        valid = None
        for attempt in range(MAX_PER_STAGE_ATTEMPTS):
            response = _safe_call(gateway, GALLERY_STAGE,
                gallery_prompt(
                    title=chapter["title"], story=chapter["story"],
                    chapter_index=int(chapter["id"][1:]),
                    start_clip=chapter["start_clip"], end_clip=chapter["end_clip"],
                    image_count=len(subset), retry=attempt > 0,
                ), gallery_schema(len(subset)), subset, sublabels, runs, budget, audit_folder)
            issues = validate_gallery(response.output, len(subset))
            _audit_raw(audit_folder, len(runs), run=response, errors=issues)
            if not issues:
                valid = response.output
                break
            failures.append(issues)
        if valid is None:
            _fail("PLANNER_GALLERY_GALLERY_INVALID",
                  "Invalid gallery for " + chapter["id"] + ":" + ";".join(failures[-1][:6]), runs)
        all_galleries.append(valid)

    proposal = _proposal_from_gallery(intervals, all_galleries, evidence, excluded)
    result = old.build_result(
        proposal, bundle, owners, runs, total_bytes=total_bytes, attempt_errors=failures
    )
    namespace = uuid.UUID(str(bundle.manifest["session"]["session_id"]))
    new_ids = {}
    for row, interval in zip(result["chapters"], intervals, strict=True):
        candidate = interval["id"]
        old_id = row["id"]
        row["id"] = str(uuid.uuid5(namespace, "planner_gallery_v02:" + candidate))
        new_ids[old_id] = row["id"]
        row["source_clip_start"] = interval["start_clip"]
        row["source_clip_end"] = interval["end_clip"]
        row["hero_reason"] = "本章原始 JPEG 中由独立 Gallery VLM 选出"
    for outcome in result["selected_memory_outcomes"]:
        outcome["memory_id"] = new_ids[outcome["memory_id"]]
    result["schema_version"] = SCHEMA_VERSION
    result["editor_policy"] = EDITOR_POLICY
    result["experiment"] = "PLANNER_GALLERY_PHYSICAL_SCOPE_V02"
    result["validation_scope"] = "STRUCTURE_LINEAGE_AND_CLIP_OWNERSHIP_ONLY"
    result["trace"]["pipeline_version"] = PIPELINE_VERSION
    result["trace"]["execution_mode"] = "GLOBAL_PLANNER_SCOPED_GALLERY_WITH_BOUNDED_RETRY"
    result["trace"]["s13_status"] = "NOT_EXECUTED_PLANNER_GALLERY"
    result["decision_trace"].update({
        "trace_type": "PLANNER_GALLERY_V02",
        "no_staged_pipeline": False,
        "clip_ownership": "EXPLICIT_CONTIGUOUS_ONE_CHAPTER_PER_CLIP",
        "model_protocol": MODEL_PROTOCOL,
        "planner_prompt_sha256": hashlib.sha256(
            planner_prompt(image_count=image_count, clip_count=clip_count).encode()).hexdigest(),
        "gallery_prompt_sha256": [
            hashlib.sha256(gallery_prompt(
                title=x["title"], story=x["story"],
                chapter_index=int(x["id"][1:]),
                start_clip=x["start_clip"], end_clip=x["end_clip"],
                image_count=len(x["image_indices"])
            ).encode()).hexdigest()
            for x in intervals
        ],
        "chapter_clip_intervals": [
            {"candidate_id": x["id"], "start_clip": x["start_clip"], "end_clip": x["end_clip"]}
            for x in intervals
        ],
        "gallery_model_input_frames": [len(x["image_indices"]) for x in intervals],
        "semantic_content_coverage_certified": False,
    })
    result["decision_trace"]["prompt_sha256"] = result["decision_trace"]["planner_prompt_sha256"]
    result["trace"]["model_call_failed_count"] = sum(bool(x) for x in failures)
    return result

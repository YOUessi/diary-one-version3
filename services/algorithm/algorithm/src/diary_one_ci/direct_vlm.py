"""Direct VLM Chapter V01: one global image-aware editorial call, deterministic gates.

This path intentionally does NOT call S04/S07/S09/S11. Images are already sampled
by the phone; all submitted JPEG frames are delivered to a single Qwen VLM
request. Retries are bounded and billable failures remain in trace.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator

from .bundle import load_app_library_bundle
from .core import sha256_file
from . import direct_vlm_compact as compact
from .x02 import (
    StageModelGateway,
    StageRun,
    X02ExecutionError,
    X02ModelNotReady,
    X02StageCallError,
    _app_asset_uuid,
    _manifest_frame_path,
)

SCHEMA_VERSION = "DIARY_ONE_DIRECT_VLM_CHAPTER_V01"
PIPELINE_VERSION = "X02_DIRECT_VLM_CHAPTER_V01"
EDITOR_POLICY = "DIRECT_VLM_GLOBAL_EDITOR_V01"
MODEL_SCHEMA_VERSION = "DIRECT_VLM_ALL_FRAMES_V01"
STAGE = "DIRECT_VLM_GLOBAL_EDITOR"
MAX_FRAMES = 250  # Provider Base64 per-request image count; do not silently crop
MAX_RAW_IMAGE_BYTES = 35 * 1024 * 1024
MAX_CHAPTERS = 14
MAX_GALLERY = 8
MAX_CALLS = 2

ITEM = {"type": "string", "minLength": 1}
FRAMES = {"type": "array", "minItems": 1, "maxItems": 250, "uniqueItems": True, "items": ITEM}
MODEL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "day_summary", "chapter_count_rationale",
                 "excluded_non_lived_frame_ids", "chapters"],
    "properties": {
        "schema_version": {"const": MODEL_SCHEMA_VERSION},
        "day_summary": {"type": "string", "minLength": 8, "maxLength": 1600},
        "chapter_count_rationale": {"type": "string", "minLength": 4, "maxLength": 500},
        "excluded_non_lived_frame_ids": {"type": "array", "maxItems": 250, "uniqueItems": True, "items": ITEM},
        "chapters": {
            "type": "array", "minItems": 1, "maxItems": MAX_CHAPTERS,
            "items": {
                "type": "object", "additionalProperties": False,
                "required": ["id", "title", "story", "hero_frame_id",
                             "gallery_frame_ids", "experience_frame_ids", "key_moments", "editorial_summary"],
                "properties": {
                    "id": {"type": "string", "pattern": r"^C[0-9]{2}$"},
                    "title": {"type": "string", "minLength": 2, "maxLength": 80},
                    "story": {"type": "string", "minLength": 12, "maxLength": 1800},
                    "hero_frame_id": ITEM,
                    "gallery_frame_ids": {"type": "array", "minItems": 1, "maxItems": MAX_GALLERY,
                                          "uniqueItems": True, "items": ITEM},
                    "experience_frame_ids": FRAMES,
                    "key_moments": {
                        "type": "array", "minItems": 1, "maxItems": 12,
                        "items": {
                            "type": "object", "additionalProperties": False,
                            "required": ["description", "frame_ids"],
                            "properties": {
                                "description": {"type": "string", "minLength": 4, "maxLength": 300},
                                "frame_ids": {"type": "array", "minItems": 1, "maxItems": 12,
                                              "uniqueItems": True, "items": ITEM}
                            },
                        },
                    },
                    "editorial_summary": {"type": "string", "minLength": 4, "maxLength": 400},
                },
            },
        },
    },
}
_MODEL_VALIDATOR = Draft202012Validator(MODEL_SCHEMA)

# One explicit *dataset* content constraint, not a rule for real user days.
# The Sydney public source video has 00:00–01:20 recap/route-map footage.
# These asset IDs encode physical 10-second source clip indices (1 = 0s).
# Failing closed here prevents accidentally sending a historical, unsanitized
# Sydney bundle to the VLM. All other inputs keep their own timeline intact.
_SYDNEY_CLIP_ID = re.compile(r"^sydney_\d{2}_(\d{6})$")
_SYDNEY_INTRO_CUTOFF_SECONDS = 80


def guard_sydney_intro_not_in_input(assets: Sequence[Mapping[str, Any]]) -> None:
    for asset in assets:
        aid = str(asset.get("asset_id", ""))
        match = _SYDNEY_CLIP_ID.fullmatch(aid)
        if match is None:
            continue
        original_start_seconds = (int(match.group(1)) - 1) * 10
        if original_start_seconds < _SYDNEY_INTRO_CUTOFF_SECONDS:
            _fail(
                "SYDNEY_INTRO_NOT_REMOVED",
                "Sydney source 00:00–01:20 is forbidden in VLM input. "
                "Use scripts/trim_sydney_intro_for_chapter.py to rebuild "
                "the image-only bundle before calling the provider.",
            )



def frame_chronology_labels(
    evidence: Sequence[tuple[Mapping[str, Any], Mapping[str, Any], Path]],
) -> dict[str, str]:
    """Per-frame time labels exposed next to each JPEG in Direct VLM calls.

    All inputs have upload order; source video time is reconstructed only for
    the explicitly numbered Sydney split dataset. Verified wall-clock metadata
    may also be forwarded. Never invent times for other user recordings.
    """
    labels: dict[str, str] = {}
    sequence_fallback: dict[str, int] = {}
    prev_source_start_ms: int | None = None
    for asset, frame, _ in evidence:
        aid = str(asset["asset_id"])
        if aid not in sequence_fallback:
            sequence_fallback[aid] = len(sequence_fallback)
        idx = asset.get("sequence_index")
        seq = idx + 1 if isinstance(idx, int) and not isinstance(idx, bool) else sequence_fallback[aid] + 1
        parts = [f"CLIP_SEQUENCE_1_BASED={seq}", "CHRONOLOGICAL_ORDER=true"]
        match = _SYDNEY_CLIP_ID.fullmatch(aid)
        pts_ms = frame.get("source_timestamp_ms")
        if match:
            # Sydney original video was split into numbered 10-second segments:
            # clip 1 = 0s, clip 9 = 80s, clip 17 = 160s, etc.
            start_ms = (int(match.group(1)) - 1) * 10_000
            if prev_source_start_ms is not None and start_ms < prev_source_start_ms:
                _fail("SYDNEY_CHRONOLOGY_ORDER_INVALID", "Sydney evidence is not ordered by source time")
            prev_source_start_ms = start_ms
            parts.append(f"SOURCE_VIDEO_CLIP_START_MS={start_ms}")
            if isinstance(pts_ms, int) and not isinstance(pts_ms, bool):
                # Relative timestamp WITHIN the 10-second clip.
                parts.append(f"SOURCE_VIDEO_FRAME_TIME_MS={start_ms + pts_ms}")
            parts.append("SOURCE_VIDEO_TIME_IS_RELATIVE_NOT_WALL_CLOCK=true")
        else:
            # A V05 capture timestamp is only reliable when the phone explicitly
            # classifies its provenance as independently VERIFIED.
            timestamp = asset.get("capture_time_ms")
            confidence = asset.get("capture_time_confidence")
            source = asset.get("capture_time_source")
            if (confidence == "VERIFIED" and source in ("EXIF_OFFSET", "DEVICE_VERIFIED")
                    and isinstance(timestamp, int) and not isinstance(timestamp, bool)):
                parts.append(f"VERIFIED_CAPTURE_TIME_UNIX_MS={timestamp}")
                if isinstance(pts_ms, int) and not isinstance(pts_ms, bool):
                    parts.append(f"FRAME_OFFSET_WITHIN_CLIP_MS={pts_ms}")
            else:
                parts.append("INTER_CLIP_ELAPSED_TIME_UNKNOWN=true")
        labels[str(frame["frame_id"])] = " ".join(parts)
    return labels


def _positive_float_env(name: str, default: float) -> float:
    value = float(os.getenv(name, default))
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite positive number")
    return value


def prompt_for_day(*, retry: bool = False) -> str:
    prompt = """你是一位负责整理可穿戴第一人称生活记录的专业日记编辑。收到的是某天完整、按采集顺序排列的抽帧 JPEG，不是完整视频。
每张图片旁附有来源片段的 asset_id、准确的 frame_id、片内相对 source_timestamp_ms；这是该10秒片段内的真实PTS，不是一天中的绝对时刻。canonical_offset_ms是抽帧角色的名义偏移，不能代替真实PTS。
相机已对每段视频做稀疏语义抽帧：单帧不意味着片段没有变化，多帧不意味着场景更重要。
请直接看完全部图片，在一个全局编辑决策中给出 Day 的章节、封面、互补图库、正文以及重要瞬间。不要逐帧分类、不要固定章节数，不按等长时间拆章。
【时间线优先】图片按真实采集时间排序。每张图旁的 CLIP_SEQUENCE_1_BASED 是源片段顺序；如果提供 SOURCE_VIDEO_CLIP_START_MS / SOURCE_VIDEO_FRAME_TIME_MS，是原视频起点以来的毫秒，不是当日真实时钟时间。如果只知道顺序、无法核定片段间隔，不得编造时间。
把“连续时间内发生的完整经历”当作 Chapter 的主要组织单元。随着时间推进，当画面地点、活动或经历主题发生实质变化时，通常应考虑开启新 Chapter；特别是不同区域和不同活动，不要仅因为都属于 citywalk 就合并掉。
同一地点的连续相似活动可以合理合章；但相隔很远时间才重新出现的同一地标，不应仅因为外观相同就把中间无关经历并入同章。它也可能只是后续经历中的背景。
不强制每两分钟或每个片段新开章节。时间先后与有证据的视觉场景变化必须同时考虑；章内来源尽量时间连续，允许有依据的少量非连续补图，但不能破坏实际发生顺序。
重要的市集、演出、建筑、海事、商业街、教堂、公园、动物、餐饮等不同真实经历，不要被相似景物标签或笼统“城市漫步”吸收。
Chapter 的正文和图库都要反映章内重要经历，而不只是封面。
关键视觉内容即使短暂出现，也要考虑是否在 key_moments 或图库中保留。
禁止把视频片头预览/路线缩略图、字幕 UI、广告片尾当作用户真实经历；字幕叠加在真实场景上时要区分实际现场与视频标题。
不能凭图片确定星期、时钟时间、旅行起终点、真实行动路线、购买完成、进入建筑内部、身份、情绪、用户意图时，不要写作确定事实。
地标名称只在形象/招牌充分支持时写出；不确定时描述真实视觉外观，避免强行专名。
gallery_frame_ids 必须包含 hero_frame_id；跨章不得重复使用同一图库 Frame ID。最多 8 张互补图库，每章建议 3–6 张。
experience_frame_ids 是本章主要证据引用，允许多于 64 张，不是上传全帧覆盖率的保证。
key_moments 应覆盖多个有区别的真实场景，并引用准确的 Frame ID；绝对不能发明任何 Frame ID。
章节数由整天的内容复杂度决定，可 1–14 章，不必凑 5 章。story 用自然中文，保持事实和限定语。
完全不使用外部路线图、人工标注、旧 S04/S07/S09 事实，不想象没拍到的内容。
输出的 JSON 最外层必须是一个对象，不是数组。schema_version 填 DIRECT_VLM_ALL_FRAMES_V01。
包含 day_summary、chapter_count_rationale、excluded_non_lived_frame_ids、chapters。
chapters 每项包含 id（C01、C02...连续编号）、title、story、hero_frame_id、gallery_frame_ids、experience_frame_ids、key_moments、editorial_summary。
key_moments 每项包含 description 和 frame_ids。所有 frame_id 均原样复制模型可见列表中的真实 ID。
注意：本次会一次传入全部图片，请基于实际图片而非默认城市路线做判断。"""
    if retry:
        prompt += (
            "\n前一次返回格式或引用未通过机械校验。本次务必输出非空 JSON 对象，"
            "不能输出 []、{}、解释文字或 Markdown。全部 Frame ID 必须从输入准确复制。"
        )
    return prompt


def _fail(code: str, message: str, runs: Sequence[StageRun] = ()) -> None:
    raise X02ExecutionError(message, stage=STAGE, code=code, stage_runs=runs)


def prepare_evidence(manifest_path: Path):
    bundle = load_app_library_bundle(manifest_path)
    guard_sydney_intro_not_in_input(bundle.manifest["assets"])
    evidence = []
    owners: dict[str, dict[str, Any]] = {}
    total_bytes = 0
    for sequence, asset in enumerate(bundle.manifest["assets"], 1):
        for frame in asset["frames"]:
            fid = str(frame["frame_id"])
            if fid in owners:
                _fail("DUPLICATE_FRAME_ID", "Duplicate input frame identity")
            path = _manifest_frame_path(bundle, frame)
            size = path.stat().st_size
            total_bytes += size
            owners[fid] = {"asset": asset, "frame": frame, "path": path, "sequence": sequence}
            evidence.append((asset, frame, path))
    # No silent dropping, sampling, first-N slicing, or hidden fallback to old pipeline.
    if not evidence or len(evidence) > MAX_FRAMES:
        _fail("DIRECT_VLM_FRAME_LIMIT", f"Direct VLM supports 1–{MAX_FRAMES} images; got {len(evidence)}")
    if total_bytes > MAX_RAW_IMAGE_BYTES:
        _fail("DIRECT_VLM_INPUT_TOO_LARGE", "Base64 request would exceed image byte guard")
    return bundle, evidence, owners, total_bytes


def validate_proposal(value: object, owners: Mapping[str, dict[str, Any]]) -> list[str]:
    if not isinstance(value, dict):
        return ["model_output_not_object"]
    errors = ["/".join(map(str, error.path)) + ":" + error.validator
              for error in _MODEL_VALIDATOR.iter_errors(value)]
    if errors:
        return errors[:12]
    known = set(owners)
    excluded = set(value["excluded_non_lived_frame_ids"])
    if excluded - known:
        errors.append("excluded_unknown_frame")
    published: list[str] = []
    ids = [ch["id"] for ch in value["chapters"]]
    if ids != [f"C{i:02d}" for i in range(1, len(ids) + 1)]:
        errors.append("chapter_identity_not_sequential")
    for ch in value["chapters"]:
        gallery = ch["gallery_frame_ids"]
        refs = [ch["hero_frame_id"], *gallery, *ch["experience_frame_ids"]]
        for km in ch["key_moments"]:
            refs += km["frame_ids"]
        if set(refs) - known:
            errors.append(ch["id"] + ":unknown_frame_id")
        if set(refs) & excluded:
            errors.append(ch["id"] + ":excluded_frame_published")
        if ch["hero_frame_id"] not in gallery:
            errors.append(ch["id"] + ":hero_outside_gallery")
        published.extend(gallery)
    if len(published) != len(set(published)):
        errors.append("cross_chapter_gallery_frame_reused")
    return errors[:24]


def _media_for(fid: str, owners: Mapping[str, dict[str, Any]], *, hero: bool) -> dict:
    meta = owners[fid]
    asset, frame = meta["asset"], meta["frame"]
    source = str(asset["asset_id"])
    kind = str(asset["media_kind"])
    duration = asset.get("original_duration_ms")
    duration = duration if isinstance(duration, int) and duration > 0 else None
    pts = frame.get("source_timestamp_ms")
    if kind == "PHOTO":
        start, end, focus, range_basis = None, None, None, "STILL_IMAGE"
    else:
        start, end, focus, range_basis = 0, duration, pts, "WHOLE_SOURCE_CLIP"
        # Unknown duration must not become a fabricated time range.
        if duration is None:
            start, end, focus, range_basis = None, None, None, "EVIDENCE_ONLY_NO_VIDEO_RANGE"
    return {
        "asset_id": _app_asset_uuid(source),
        "source_asset_id": source,
        "media_kind": kind,
        "role": "HERO" if hero else "SUPPORT",
        "representative_frame_id": fid,
        "evidence_frame_ids": [fid],
        "source_sequence_index": meta["sequence"],
        "selection_role": "PRIMARY" if hero else "SUPPORT",
        "selection_reason": "VLM global editorial choice; frame identity checked against uploaded JPEG",
        "start_ms": start, "end_ms": end, "focus_pts_ms": focus, "range_basis": range_basis,
    }


def build_result(proposal: Mapping[str, Any], bundle, owners, runs: Sequence[StageRun],
                 *, total_bytes: int, attempt_errors: Sequence[list[str]]) -> dict:
    sid = str(bundle.manifest["session"]["session_id"])
    namespace = uuid.UUID(sid)
    chapters = []
    outcomes = []
    for chapter in proposal["chapters"]:
        hero = chapter["hero_frame_id"]
        gallery = chapter["gallery_frame_ids"]
        media = [_media_for(fid, owners, hero=fid == hero) for fid in gallery]
        sources = {owners[fid]["asset"]["asset_id"] for fid in chapter["experience_frame_ids"]}
        all_evidence = list(dict.fromkeys([
            *chapter["experience_frame_ids"], *gallery,
            *(f for km in chapter["key_moments"] for f in km["frame_ids"]),
        ]))
        chapter_id = str(uuid.uuid5(namespace, "direct_vlm_v01:" + chapter["id"]))
        chapter_out = {
            "id": chapter_id, "candidate_id": chapter["id"],
            "title": chapter["title"], "story": chapter["story"],
            "preview_story": chapter["story"][:180],
            "time_label": "采集顺序中的主题回顾",
            "tags": [],
            "hero_frame_id": hero,
            "hero_asset_id": _app_asset_uuid(str(owners[hero]["asset"]["asset_id"])),
            "hero_reason": "模型全局挑选的主题代表帧",
            "selected_media": media,
            "experience_frame_ids": all_evidence,
            "key_moments": chapter["key_moments"],
            "editorial_summary": chapter["editorial_summary"],
            "source_asset_ids": sorted(sources),
            "moment_ids": [],
            "highlights": [],
            "claims": [],
            "publication_status": "STAGED_PREVIEW_VALIDATED",
        }
        chapters.append(chapter_out)
        outcomes.append({
            "memory_type": "CHAPTER", "memory_id": chapter_id,
            "selection_state": "DIRECT_VLM_SELECTED",
            "media_state": "DIRECT_VLM_MEDIA_READY",
            "surface_state": "DIRECT_VLM_STORY",
            "visibility_state": "VISIBLE_PREVIEW",
        })
    input_tokens = sum(run.input_tokens for run in runs)
    output_tokens = sum(run.output_tokens for run in runs)
    cost_usd = sum(run.estimated_cost_usd for run in runs)
    # Cost is a trace of the model calls, including structurally invalid responses.
    return {
        "schema_version": SCHEMA_VERSION, "editor_policy": EDITOR_POLICY,
        "experiment": "DIRECT_FULL_DAY_JPEG_VLM", "experimental": True,
        "production_ready": False, "leaderboard_eligible": False,
        "session_id": sid, "bundle_manifest_sha256": sha256_file(bundle.manifest_path),
        "day_summary": proposal["day_summary"],
        "chapter_count_rationale": proposal["chapter_count_rationale"],
        "excluded_non_lived_frame_ids": proposal["excluded_non_lived_frame_ids"],
        "output_mode": "CHAPTER_DAY", "semantic_day_state": "CHAPTER_DAY",
        "delivery_state": "READY_PRIMARY_COPY",
        "coverage_status": "INPUT_ALL_FRAMES_SUBMITTED",
        "unresolved_asset_ids": [], "chapters": chapters,
        "ahas": [], "moments": [], "observations": [],
        "selected_memory_outcomes": outcomes,
        "timeline_basis": "SYNTHETIC_SEQUENCE_ONLY", "timeline_date": None,
        "time_reliability": {"capture_time_reliable": False, "interval_reliable": False,
                             "timezone_reliable": False},
        "validation_scope": "DIRECT_ID_AND_STRUCTURE_CHECK_ONLY",
        "decision_trace": {
            "trace_type": "DIRECT_VLM_GLOBAL_EDIT",
            "contains_hidden_reasoning": False,
            "visual_fact_reviewed": False,
            "semantic_copy_verified": False,
            "no_staged_pipeline": True,
            "chronology_model_input": "CLIP_SEQUENCE_PER_FRAME_AND_VERIFIED_TIMELINE_IF_AVAILABLE",
            "attempt_validation_errors": list(attempt_errors),
            "prompt_sha256": hashlib.sha256(prompt_for_day().encode()).hexdigest(),
            "input_coverage": {"frames_submitted": len(owners), "clips_received": len(bundle.manifest["assets"]),
                               "image_bytes": total_bytes,
                               "semantic_content_coverage_certified": False},
        },
        "trace": {
            "run_id": str(uuid.uuid4()), "pipeline_version": PIPELINE_VERSION,
            "execution_mode": "DIRECT_VLM_ONE_GLOBAL_CALL_WITH_BOUNDED_RETRY",
            "evaluation_run_mode": "FRESH_FULL_RUN", "cross_run_semantic_cache_used": False,
            "provider": runs[-1].provider, "model": runs[-1].model,
            "request_id": runs[-1].request_id,
            "request_ids": [r.request_id for r in runs],
            "model_calls": len(runs), "model_call_completed_count": len(runs),
            "model_call_failed_count": len(attempt_errors),
            "asset_count": len(bundle.manifest["assets"]), "evidence_frame_count": len(owners),
            "model_frame_count": sum(r.model_frame_count for r in runs),
            "input_tokens": input_tokens, "output_tokens": output_tokens,
            "estimated_cost_usd": round(cost_usd, 8),
            "pricing_basis": runs[-1].pricing_basis,
            "latency_seconds": round(sum(r.latency_seconds for r in runs), 3),
            "stage_metrics": [{
                "stage": run.stage, "model_calls": run.model_calls, "input_tokens": run.input_tokens,
                "output_tokens": run.output_tokens, "estimated_cost_usd": round(run.estimated_cost_usd, 8),
                "latency_seconds": round(run.latency_seconds, 3),
                "request_id": run.request_id,
            } for run in runs],
            "originals_uploaded": 0, "s13_status": "NOT_EXECUTED_DIRECT_VLM",
        },
    }


def _write_attempt_audit(
    audit_dir: Path | None, attempt: int, run: StageRun,
    errors: Sequence[str], repairs: Sequence[str],
) -> None:
    # Local private model text only; never store JPEG Base64 or provider API key.
    # The response itself can contain private diary text: restrict file permissions.
    if audit_dir is None:
        return
    audit_dir = Path(audit_dir)
    audit_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    audit_dir.chmod(0o700)
    obj = {
        "attempt": attempt,
        "stage": STAGE,
        "model_protocol": compact.MODEL_PROTOCOL,
        "request_id": run.request_id, "provider": run.provider, "model": run.model,
        "input_tokens": run.input_tokens, "output_tokens": run.output_tokens,
        "estimated_cost_native": run.estimated_cost_native,
        "latency_seconds": run.latency_seconds, "finish_reason": run.finish_reason,
        "validation_errors": list(errors),
        "safe_repairs": list(repairs), "model_output": run.output,
    }
    data = json.dumps(obj, ensure_ascii=False, indent=2).encode()
    dst = audit_dir / f"attempt_{attempt:02d}.json"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(dst, flags, 0o600)
    with os.fdopen(fd, "wb") as output:
        output.write(data)


def run_direct_vlm(
    manifest_path: Path,
    gateway: StageModelGateway,
    *,
    audit_dir: Path | None = None,
) -> dict:
    """Single direct full-day VLM call; at most one whole-call retry.

    VLM returns compact chapter decisions only. All public Frame IDs, hero,
    clips, evidence lineage and app metadata come from deterministic conversion.
    """
    if not gateway.ready:
        raise X02ModelNotReady("Direct VLM requires a configured real model API key")
    bundle, evidence, owners, total_bytes = prepare_evidence(manifest_path)
    max_budget = _positive_float_env("DIARY_ONE_DIRECT_VLM_BUDGET_CNY", 1.20)
    input_est = len(evidence) * 800 + 12_000
    output_est = 5_000
    adapter = getattr(gateway, "adapter", None)
    if adapter is not None:
        approximate_cost = MAX_CALLS * (
            input_est * adapter.input_rate_per_million
            + output_est * adapter.output_rate_per_million
        ) / 1_000_000
        if approximate_cost > max_budget:
            _fail("DIRECT_VLM_BUDGET_PREFLIGHT", "Model cost estimate exceeds configured guard")
    runs: list[StageRun] = []
    errors_by_attempt: list[list[str]] = []
    clip_count = len(bundle.manifest["assets"])
    labels = compact.image_labels(evidence, frame_chronology_labels(evidence))
    for i in range(MAX_CALLS):
        try:
            run = gateway.call(
                STAGE,
                compact.prompt(
                    image_count=len(evidence), clip_count=clip_count, retry=i > 0,
                ),
                compact.SCHEMA,
                evidence=evidence,
                context={
                    "_audit_stage_failures": True,
                    "_x02_policy_version": "V04_1",
                    "_direct_vlm_frame_chronology": labels,
                    "_direct_vlm_compact": True,
                },
            )
        except X02StageCallError as exc:
            _fail(exc.code, "Direct VLM provider request failed", [*runs, exc.stage_run])
        except Exception as exc:
            _fail("DIRECT_VLM_TRANSPORT_FAILURE", type(exc).__name__ + " during direct VLM call", runs)
        runs.append(run)
        proposal, errors, repairs = compact.convert(run.output, evidence)
        if not errors and proposal is not None:
            errors = validate_proposal(proposal, owners)
        _write_attempt_audit(audit_dir, i + 1, run, errors, repairs)
        if proposal is not None and not errors:
            result = build_result(
                proposal, bundle, owners, runs,
                total_bytes=total_bytes, attempt_errors=errors_by_attempt,
            )
            result["decision_trace"]["compact_model_protocol"] = compact.MODEL_PROTOCOL
            result["decision_trace"]["deterministic_structure_repairs"] = repairs
            result["decision_trace"]["model_output_requires_no_frame_ids"] = True
            result["decision_trace"]["prompt_sha256"] = hashlib.sha256(
                compact.prompt(image_count=len(evidence), clip_count=clip_count).encode()
            ).hexdigest()
            return result
        errors_by_attempt.append(errors)
    _fail(
        "DIRECT_VLM_OUTPUT_INVALID",
        "Compact Direct VLM returned invalid chapter decisions after bounded retry: "
        + ";".join(errors_by_attempt[-1][:8]),
        runs,
    )

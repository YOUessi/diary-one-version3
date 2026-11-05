"""Compact Direct VLM editorial protocol and deterministic, evidence-bound converter.

A multimodal model makes only editorial decisions. It receives 1-based image
indices and source-grounded clip chronology. It does not copy UUID Frame IDs,
author giant evidence lists, choose JSON media IDs, or duplicate hero references.

This module makes NO API calls. All conversion is pure and fail-closed.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator

MODEL_PROTOCOL = "DIRECT_VLM_COMPACT_EDITOR_V03"
MAX_CHAPTERS = 14
MAX_GALLERY = 8
SCHEMA = {
    "type": "object",
    "required": ["chapters"],
    "properties": {
        "chapters": {
            "type": "array", "minItems": 1, "maxItems": MAX_CHAPTERS,
            "items": {
                "type": "object",
                "required": ["title", "story", "selected_images"],
                "properties": {
                    "title": {"type": "string"},
                    "story": {"type": "string"},
                    "selected_images": {
                        "type": "array", "minItems": 1, "maxItems": MAX_GALLERY,
                        "items": {"type": "integer", "minimum": 1}
                    },
                    "key_moments": {
                        "type": "array", "maxItems": 10,
                        "items": {
                            "type": "object",
                            "required": ["text", "image_index"],
                            "properties": {
                                "text": {"type": "string"},
                                "image_index": {"type": "integer", "minimum": 1}
                            },
                        },
                    },
                },
            }
        },
        "excluded_images": {
            "type": "array", "maxItems": 250,
            "items": {"type": "integer", "minimum": 1}
        },
    },
}
_VALIDATOR = Draft202012Validator(SCHEMA)


def prompt(*, image_count: int, clip_count: int, retry: bool = False) -> str:
    """Single global visual timeline editor. Format does not force chapter count."""
    if image_count <= 0 or clip_count <= 0:
        raise ValueError("Empty direct VLM input")
    basic = f"""你是第一人称生活记录的全局 Chapter 编辑。输入共有 {image_count} 张 JPEG、{clip_count} 个按时间排列的片段。
每张图片紧前方标注 IMAGE_INDEX_1_BASED（1 到 {image_count}）、CLIP_SEQUENCE_1_BASED（1 到 {clip_count}）和可核实的原视频相对时间。原视频相对时间不是时钟时间。
请看完所有图片，理解完整时间线，直接划分最自然的 Chapter，并写故事及选取互补图片。

【内容原则】
1. 优先依据真实时间先后、地点变化及活动变化分章。新地点/新活动/新经历应考虑新 Chapter，但不要按固定时间间隔机械拆分，也不要为了满足预设数量拆章。
2. 同一地点连续相似场景可以合章；不同时刻重复出现同一地标，不应跨过无关经历强制合并。章节应反映实际发生的连续经历。
3. 不要遗漏市集、海事馆、商业街、历史建筑、教堂、园林、特殊活动等短暂且独特的场景，也不要因为都属于 Citywalk 就归为一个泛泛的章。
4. 仅凭画面可见证据作事实描述：不可凭视频相对时间推断“黄昏”“下午”“周末”、购物完成、主观心情和用户意图。地标身份不确定时保守描述。
5. 忽略前后宣传片、地图介绍、视频水印上的不真实信息。excluded_images 可记录明确不是实际生活内容的图片序号，禁止把它们选入章节图库。

【输出只需要编辑决策，程序负责所有引用转换】
仅返回最外层为对象的 JSON：{{"chapters":[{{"title":"...","story":"...","selected_images":[1,3,9],"key_moments":[{{"text":"...","image_index":9}}]}}],"excluded_images":[]}}
必须是对象而不是空数组。不要输出 Markdown、模型内部分析、冗长的 frame_id/asset_id/UUID、证据全集、hero_frame_id、start_clip、end_clip、editorial_summary、schema_version。
整个输出只使用一种编号：真实 IMAGE_INDEX_1_BASED（1 到 {image_count}）。不要输出 CLIP_SEQUENCE 作为图片编号，不要输出时间范围编号。
每章的 selected_images 是该章代表性的真实图片序号，建议 3-6 张，最多 8 张。第一个数字就是封面，按你认为重要的顺序排列；跨章节不可复用同一图片。
key_moments 也只引用 IMAGE_INDEX_1_BASED；章节按照真实发生的时间从早到晚输出。程序会根据所有入选图片的实际来源自动计算该章时间跨度，你无需手工填写时间边界。
保持标题、图片和故事对应，不要因为同一地标重复出现就跨时间合并不相干经历。
不确定时输出保守的、证据明确的章节，不得凭空猜想不存在的图片序号。"""
    if retry:
        basic += "\n上一次返回不符合结构或真实索引约束。本次必须给出非空 JSON 对象，且只用 1-based 输入图片索引；不要重新解释这些规则。"
    return basic


def image_labels(evidence: Sequence[tuple[Mapping[str, Any], Mapping[str, Any], Path]],
                 chronology: Mapping[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for idx, (_, frame, _) in enumerate(evidence, 1):
        fid = str(frame["frame_id"])
        label = chronology[fid]
        if not label.startswith("CLIP_SEQUENCE_1_BASED="):
            raise ValueError("Chronology missing clip sequence for image")
        result[fid] = f"IMAGE_INDEX_1_BASED={idx} " + label
    return result


def _index(value: Any, bound: int) -> int | None:
    # Allow only lossless decimal-string -> integer repair; never guess a frame.
    if type(value) is int:
        result = value
    elif isinstance(value, str) and value.isascii() and value.isdecimal():
        result = int(value)
    else:
        return None
    return result if 1 <= result <= bound else None


def _text(value: Any, maximum: int) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value if 1 <= len(value) <= maximum else None


def convert(raw: object,
            evidence: Sequence[tuple[Mapping[str, Any], Mapping[str, Any], Path]],
            *, max_gallery: int = MAX_GALLERY) -> tuple[dict | None, list[str], list[str]]:
    """Convert model editorial choices to source-bound legacy internal proposal.

    All chapter time spans are inferred from the selected true image indices,
    never guessed from an incompatible second "clip index" numbering system.
    Model-selected stories, order and real gallery images are preserved.
    """
    repairs: list[str] = []
    errors: list[str] = []
    if not isinstance(raw, dict):
        return None, ["top_level_not_object"], repairs
    rows = raw.get("chapters")
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_CHAPTERS:
        return None, ["missing_or_invalid_chapters"], repairs
    n_images = len(evidence)
    if not n_images:
        return None, ["empty_input"], repairs
    source_to_seq: dict[str, int] = {}
    images: dict[int, tuple[str, int]] = {}
    for i, (asset, frame, _) in enumerate(evidence, 1):
        source = str(asset["asset_id"])
        if source not in source_to_seq:
            source_to_seq[source] = len(source_to_seq) + 1
        images[i] = (str(frame["frame_id"]), source_to_seq[source])
    excluded: set[int] = set()
    excluded_raw = raw.get("excluded_images", [])
    if not isinstance(excluded_raw, list):
        return None, ["excluded_images_not_array"], repairs
    for x in excluded_raw:
        idx = _index(x, n_images)
        if idx is None:
            repairs.append("unknown_excluded_index_ignored")
        else:
            excluded.add(idx)
    chapters: list[dict] = []
    seen_gallery: set[int] = set()
    chapter_start_clips: list[int] = []
    for pos, item in enumerate(rows, 1):
        label = f"C{pos:02d}"
        if not isinstance(item, dict):
            errors.append(f"{label}:not_object")
            continue
        title, story = _text(item.get("title"), 80), _text(item.get("story"), 1800)
        if title is None or len(title) < 2:
            errors.append(f"{label}:invalid_title")
        if story is None or len(story) < 12:
            errors.append(f"{label}:invalid_story")
        gallery_raw = item.get("selected_images")
        if not isinstance(gallery_raw, list) or not gallery_raw:
            errors.append(f"{label}:invalid_gallery_length")
            continue
        indices: list[int] = []
        for x in gallery_raw:
            idx = _index(x, n_images)
            if idx is None:
                errors.append(f"{label}:selected_image_outside_input")
                continue
            if idx in indices:
                repairs.append(f"{label}:duplicate_gallery_index_deduplicated")
                continue
            if idx in excluded:
                errors.append(f"{label}:excluded_gallery_image")
            if idx in seen_gallery:
                errors.append(f"{label}:gallery_reused_across_chapters")
            indices.append(idx)
        if not indices:
            errors.append(f"{label}:empty_gallery_after_validation")
            continue
        if len(indices) > max_gallery:
            # Model output already ranks photos, so keep the highest priority.
            # This never invents, moves or replaces a semantic photo choice.
            indices = indices[:max_gallery]
            repairs.append(f"{label}:gallery_tail_over_limit_dropped")
        seen_gallery.update(indices)
        events_raw = item.get("key_moments", [])
        if not isinstance(events_raw, list):
            errors.append(f"{label}:key_moments_not_array")
            continue
        moments: list[tuple[str, int]] = []
        for event in events_raw[:10]:
            if not isinstance(event, dict):
                repairs.append(f"{label}:unstructured_key_moment_dropped")
                continue
            text = _text(event.get("text"), 300)
            idx = _index(event.get("image_index"), n_images)
            if text is None or len(text) < 4 or idx is None or idx in excluded:
                repairs.append(f"{label}:invalid_key_moment_dropped")
                continue
            moments.append((text, idx))
        all_selected = indices + [i for _, i in moments]
        scope_start = min(images[idx][1] for idx in all_selected)
        scope_end = max(images[idx][1] for idx in all_selected)
        chapter_start_clips.append(scope_start)
        # Ignore old redundant model-supplied clip bounds, even on archived
        # V02 responses. Actual selected JPEG provenance defines the span.
        if "start_clip" in item or "end_clip" in item:
            repairs.append(f"{label}:redundant_model_clip_bounds_ignored")
        if not moments:
            moments = [(f"代表画面：{title or '所选章节'}", indices[0])]
            repairs.append(f"{label}:no_key_moment_use_selected_cover")
        scoped = [fid for idx,(fid,seq) in images.items()
                  if scope_start <= seq <= scope_end and idx not in excluded]
        if not scoped:
            errors.append(f"{label}:empty_derived_clip_span")
            continue
        chapters.append({
            "id": label, "title": title or "", "story": story or "",
            "hero_frame_id": images[indices[0]][0],
            "gallery_frame_ids": [images[idx][0] for idx in indices],
            "experience_frame_ids": scoped,
            "key_moments": [
                {"description": text, "frame_ids": [images[idx][0]]}
                for text,idx in moments
            ],
            "editorial_summary": (
                f"按所选真实图片来源推导片段序号范围：{scope_start}至{scope_end}；"
                "模型独立决定主题、故事与图库。"
            ),
        })
    if errors or not chapters:
        return None, sorted(set(errors or ["no_valid_chapters"])), repairs
    # Source clip chronology is authoritative. Sorting changes only display
    # order and deterministic IDs, never model stories or selected images.
    indexed = list(zip(chapter_start_clips, range(len(chapters)), chapters))
    indexed.sort(key=lambda x: (x[0], x[1]))
    if [original_i for _, original_i, _ in indexed] != list(range(len(chapters))):
        repairs.append("chapters_reordered_by_verified_source_chronology")
    chapters = [item for _, _, item in indexed]
    for i, chapter in enumerate(chapters, 1):
        chapter["id"] = f"C{i:02d}"
    heading = "、".join(ch["title"] for ch in chapters)
    summary = "当天按时间顺序记录了：" + heading
    rationale = f"模型依据原始图片的时间线和场景变化组织了{len(chapters)}个章节；章节时间范围来自真实所选图片。"
    result = {
        "schema_version": "DIRECT_VLM_ALL_FRAMES_V01",
        "day_summary": summary[:1600],
        "chapter_count_rationale": rationale,
        "excluded_non_lived_frame_ids": [images[idx][0] for idx in sorted(excluded)],
        "chapters": chapters,
    }
    return result, [], repairs

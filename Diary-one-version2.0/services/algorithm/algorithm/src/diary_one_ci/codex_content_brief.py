"""Versioned, mechanical content handoff; never a semantic judge or model call."""

import copy
import json

from . import codex_writer_exit as writer_exit
from . import codex_editorial_allocation as allocation


POLICY_VERSION = "DIARY_ONE_X02_CONTENT_BRIEF_V01"
POLICY_FIELD = "content_brief_policy_version"


def compact_facts(memory):
    """Preserve approved fact IDs/text verbatim; provenance stays in the ledger."""
    return [{"fact_id": fact["fact_id"], "text": fact["text"]}
            for fact in memory["facts"]]


def build_brief(memory):
    """Project existing guidance onto this memory's actual material/fact scope.

    Hints are not facts. Empty hints remain empty and never block a memory.
    No text interpretation, interest scoring, reordering or new relationship.
    """
    allowed = {fact["fact_id"] for fact in memory["facts"]}
    identity = memory.get("storyline_identity", {})
    beats = {beat["observation_id"]: beat for beat in identity.get("beat_map", [])}
    is_chapter = memory["memory_type"] == "CHAPTER"
    materials = []
    for media in memory.get("selected_media", []):
        observation_id = media["observation_id"]
        beat = beats.get(observation_id, {})
        source_ids = beat.get("fact_ids", []) if is_chapter else memory.get("event_fact_ids", [])
        fact_ids = [value for value in source_ids if value in allowed]
        materials.append({
            "observation_id": observation_id,
            "fact_ids": fact_ids,
            # Do not imply that a partially unavailable source supports the full hint.
            "contribution_hint": (beat.get("contribution", "")
                                  if is_chapter and source_ids and set(source_ids) <= allowed else ""),
        })
    return {
        "theme_hint": identity.get("thesis", "") if is_chapter else "",
        "moment_hint": memory.get("narrative_duty", "") if not is_chapter else "",
        "materials": materials,
    }


def chapter_selection_content(candidate, members):
    """Use the same brief builder before display selection, for all members."""
    allowed = set(candidate["fact_ids"])
    memory = {
        "memory_type": "CHAPTER",
        "storyline_identity": candidate["storyline_identity"],
        "facts": [fact for member in members for fact in member["facts"]
                  if fact["fact_id"] in allowed],
        "selected_media": [{"observation_id": member["id"]} for member in members],
    }
    return {POLICY_FIELD: POLICY_VERSION, "content_brief": build_brief(memory),
            "facts": compact_facts(memory)}


def writer_input(context):
    """Keep full validation/fallback context untouched; send only useful content."""
    memories = []
    for memory in context["memories"]:
        outgoing = {
            "candidate_id": memory["candidate_id"], "memory_type": memory["memory_type"],
            "content_brief": build_brief(memory), "facts": compact_facts(memory),
        }
        if memory["memory_type"] == "AHA":
            outgoing["event_fact_ids"] = list(memory["event_fact_ids"])
        memories.append(outgoing)
    projected = {
        "locale": context["locale"], POLICY_FIELD: POLICY_VERSION,
        "sequence_basis": "IMPORT_SEQUENCE_ONLY_NOT_CAPTURE_TIME",
        "guidance_scope": "EDITORIAL_HINTS_NOT_FACT_EVIDENCE",
        "memories": memories,
    }
    if writer_exit.soft_length_enabled(context):
        projected[writer_exit.POLICY_FIELD] = context[writer_exit.POLICY_FIELD]
    if context.get(allocation.POLICY_FIELD) == allocation.POLICY_VERSION:
        projected[allocation.POLICY_FIELD] = allocation.POLICY_VERSION
        # Reproject at the final send boundary as well: a narrowed/retry
        # context must not expose another card's out-of-scope guidance.
        projection = allocation.project(context.get("editorial_allocation", {}), context["memories"])
        projected["chapter_aha_relations"] = projection["relations"]
    if "previous_failures" in context:
        projected["previous_failures"] = copy.deepcopy(context["previous_failures"])
    return projected


def writer_prompt(context, *, retry, limits):
    allocation_note = (
        "chapter_aha_relations 是分组阶段已提出的跨卡分工提示，不是新事实。"
        "对列出的两张卡，Chapter 围绕其已有主题，Aha 聚焦关系说明中有自身事实支持的独立瞬间；"
        "不是把同一故事换个说法再写一次。每张卡仍只能引用本条 facts，不能借用另一条事实。"
        "没有可用分工时，不宣称已经证明独立，也不为制造区别补造内容。\n"
        if context.get(allocation.POLICY_FIELD) == allocation.POLICY_VERSION else ""
    )
    retry_note = (
        "这是既有流程中唯一一次修复调用，只改输入中的失败条目。previous_failures 保留了原稿、实际字数及失败原因；按原要求自然改写，不新增记忆。\n"
        if retry and not writer_exit.soft_length_enabled(context) else ""
    )
    aha_length = (
        f"一句，以 {writer_exit.AHA_TARGET} 字为写作目标，{writer_exit.AHA_TARGET + 1}–{writer_exit.AHA_TOLERANCE} 字也可接受；"
        "更长文案会原样保留并标记偏长待评价，但仍应聚焦简洁，不为凑字数截断句子；"
        if writer_exit.soft_length_enabled(context) else f"一句且最多 {limits['aha_max']} 字；"
    )
    return (
        "为 Diary One 写中文记忆卡片。只返回规定的 JSON，不输出分析、评分或取舍记录。\n"
        + retry_note
        + "每条输入都返回到对应的 chapters 或 ahas，不改变分组、素材或数量。\n"
        "content_brief 的 theme_hint、moment_hint、contribution_hint 是已有组织提示，不是事实或必须照抄的文案；"
        "事实只来自本条 facts。提示不完整时仍根据已有事实写，不补造主题。\n"
        "结合主题贴合程度、内容的具体特点和相对其他内容的新增意义，选择最值得说的核心，按需补充细节。"
        "不要逐个列举物体、逐张介绍图片或凑固定数量；素材/封面排序不等于文字重点排序。\n"
        "像翻相册时自然说的一句话，有具体画面，可以有画面支持的适度氛围；不写空泛口号或选材理由。"
        "不新增地点、身份、人物关系、味觉、意图、因果、对话或事件，不代替用户宣称感受和偏好。\n"
        "materials 标明事实的素材归属，不证明不同素材同处一个场景或连续发生。没有可靠拍摄时间，"
        "不把导入排列或提示里的过程性措辞当成先后证据，不编写连接经历。\n"
        "Chapter 概括核心内容；Aha 聚焦自身瞬间。两者应有不同表达职责，但不能为制造区别编造事件。\n"
        + allocation_note
        +
        f"Chapter：title 通常 {limits['title_min']}–{limits['title_target']} 字，必要时最多 {limits['title_max']} 字；"
        f"text 默认一句、最多两句，自然表达下尽量不超过 {limits['chapter_target']} 字，不机械截断。\n"
        "Aha：title 只是内部短标签；text 是唯一展示文案，" + aha_length
        + "只引用 event_fact_ids 指定的事实。汉字、字母、数字、标点各计一字，空白不计，输出前检查长度。\n"
        "每条必须包含 candidate_id、title、text、claim_ids；claim_ids 仅包含实际支持该文案的本条事实编号，原样返回。\n"
        "Input:\n" + json.dumps(writer_input(context), ensure_ascii=False)
    )

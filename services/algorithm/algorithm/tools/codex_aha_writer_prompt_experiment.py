"""Archived V1.38 failed prompt experiment. NOT imported by the live pipeline.

Four real Qwen calls failed the unchanged 20-character contract. Retained only
for reproducible S11 diagnosis; neither a production policy nor a quality fix.
"""

import json
from typing import Mapping

from diary_one_ci.x02 import (
    AHA_MOMENT_LINE_VISIBLE_MAX, WRITER_SCHEMA, X02_WRITER_GROUNDING_POLICY,
    _writer_prompt as _general_writer_prompt,
    _writer_retry_context as _base_retry_context,
)

X02_WRITER_REQUEST_POLICY_VERSION = "DIARY_ONE_X02_WRITER_REQUEST_V04"


def _writer_retry_context(context, invalid_ids, writer_audit):
    retry_context = _base_retry_context(context, invalid_ids, writer_audit)
    if _uses_focused_aha_repair(retry_context, retry=True):
        retry_context["writer_request_policy_version"] = X02_WRITER_REQUEST_POLICY_VERSION
    return retry_context


def _uses_focused_aha_repair(context: Mapping[str, object], retry: bool) -> bool:
    return bool(
        retry
        and context.get("writer_grounding_policy") == X02_WRITER_GROUNDING_POLICY
        and any(item.get("memory_type") == "AHA" for item in context.get("memories", []))
    )


def _writer_request_schema(context: Mapping[str, object], retry: bool) -> Mapping[str, object]:
    if not _uses_focused_aha_repair(context, retry):
        return WRITER_SCHEMA
    # A request hint, not a substitute for the existing visible-character check.
    # Do not mutate the shared schema or change Chapter / first-attempt requests.
    schema = json.loads(json.dumps(WRITER_SCHEMA))
    aha_properties = schema["properties"]["ahas"]["items"]["properties"]
    aha_properties["text"] = {
        "type": "string",
        "description": f"一个瞬间的自然短句，写作目标约12至16字，可更短；含标点最多{AHA_MOMENT_LINE_VISIBLE_MAX}个可见字符。",
    }
    return schema


def _writer_prompt(context: Mapping[str, object], retry: bool) -> str:
    if not _uses_focused_aha_repair(context, retry):
        return _general_writer_prompt(context, retry)
    # Project only the outgoing Aha writing input. The original evidence,
    # candidate membership and validation context remain unchanged.
    projected = dict(context)
    projected["memories"] = []
    for memory in context["memories"]:
        if memory["memory_type"] != "AHA":
            projected["memories"].append(memory)
            continue
        event_ids = set(memory.get("event_fact_ids", [fact["fact_id"] for fact in memory["facts"]]))
        projected["memories"].append({
            "candidate_id": memory["candidate_id"],
            "memory_type": "AHA",
            "narrative_duty": memory.get("narrative_duty", ""),
            "event_fact_ids": sorted(event_ids),
            "facts": [{"fact_id": fact["fact_id"], "text": fact["text"]}
                      for fact in memory["facts"] if fact["fact_id"] in event_ids],
        })
    instruction = (
        "Aha 定向重写：previous_failures 是失败草稿和程序实测字数，不是新的事实证据。"
        f"每条 Aha 的 text 只写一句自然中文，含标点最多{AHA_MOMENT_LINE_VISIBLE_MAX}个可见字符，空白不计。"
        "请以约12至16字为写作目标，给20字上限留余量；可以更短，不要为凑字补充内容。"
        "先从对应 facts 里选定这一个瞬间最值得表达的重点，再重新写短句；"
        "不需要覆盖整条 fact 的所有细节，也不要逐个缩写原句来保留整幅画面的清单。"
        "背景只在帮助表达这个重点时保留；保留必要限定，不改变事实含义。"
        "可以自然转述、克制地表达可见氛围，不编造用户感受、偏好、身份关系、地名、味道或因果。"
        "claim_ids 只填写本条实际用到的 event_fact_ids；其他条目的事实不能借用。"
        "narrative_duty 仅用于组织表达，不是新增事实证据。"
        "返回前检查 text 字数，超长时由你重新措辞，不截断句子，也不遗漏该条目。"
        "title 是简短内部标签，不是第二段文案。"
    )
    if any(item["memory_type"] == "CHAPTER" for item in context["memories"]):
        # Mixed failures still use the same single retry. Chapter instructions
        # and supplied Chapter data remain exactly the general Writer contract.
        return _general_writer_prompt(projected, retry=True) + "\n" + instruction
    return (
        "Diary One S11 / " + X02_WRITER_REQUEST_POLICY_VERSION
        + "。这是唯一一次重写，只修复输入中的失败 Aha，不生成 Chapter，不增删条目。"
        + instruction + "只返回符合给定结构的 JSON。Input:\n"
        + json.dumps(projected, ensure_ascii=False)
    )

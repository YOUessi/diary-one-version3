"""V1.74 request-local Writer references and fail-closed delivery.

The model sees only short identifiers.  Canonical identifiers remain in a
private map and are restored before the existing deterministic Writer gate.
This module does not generate fallback copy or make semantic decisions.
"""

import copy
import json

from . import codex_grounded_recording_editor as grounded


POLICY_FIELD = "codex_v174_writer_policy_version"
POLICY_VERSION = "DIARY_ONE_X02_WRITER_EXIT_V03"


def enabled(context):
    return context.get(POLICY_FIELD) == POLICY_VERSION


def _short_maps(context):
    candidate_to_short = {}
    chapter_index = 0
    aha_index = 0
    fact_to_short = {}
    observation_to_short = {}
    for memory in context.get("memories", []):
        if memory.get("memory_type") == "CHAPTER":
            chapter_index += 1
            short = "C%02d" % chapter_index
        else:
            aha_index += 1
            short = "A%02d" % aha_index
        candidate_to_short[str(memory["candidate_id"])] = short
        for fact in memory.get("facts", []):
            fact_id = str(fact["fact_id"])
            if fact_id not in fact_to_short:
                fact_to_short[fact_id] = "F%03d" % (len(fact_to_short) + 1)
        for media in memory.get("selected_media", []):
            observation_id = str(media.get("observation_id", ""))
            if observation_id and observation_id not in observation_to_short:
                observation_to_short[observation_id] = "O%03d" % (
                    len(observation_to_short) + 1
                )
    return {
        "candidates": {value: key for key, value in candidate_to_short.items()},
        "candidate_short_by_long": candidate_to_short,
        "facts": {value: key for key, value in fact_to_short.items()},
        "fact_short_by_long": fact_to_short,
        "observations": {value: key for key, value in observation_to_short.items()},
        "observation_short_by_long": observation_to_short,
    }


def _map_list(values, mapping):
    return [mapping.get(str(value), str(value)) for value in values]


def encode_context(context):
    """Project the approved Writer context and replace transport identifiers."""
    payload = grounded.writer_input(context)
    maps = _short_maps(context)
    candidates = maps["candidate_short_by_long"]
    facts = maps["fact_short_by_long"]
    observations = maps["observation_short_by_long"]

    for memory in payload.get("memories", []):
        memory["candidate_id"] = candidates[str(memory["candidate_id"])]
        for fact in memory.get("facts", []):
            fact["fact_id"] = facts[str(fact["fact_id"])]
        if "event_fact_ids" in memory:
            memory["event_fact_ids"] = _map_list(memory["event_fact_ids"], facts)
        brief = memory.get("content_brief", {})
        for material in brief.get("materials", []):
            material["observation_id"] = observations.get(
                str(material.get("observation_id", "")),
                str(material.get("observation_id", "")),
            )
            material["fact_ids"] = _map_list(material.get("fact_ids", []), facts)

    candidate_fields = {
        "candidate_id", "chapter_candidate_id", "aha_candidate_id",
        "left_aha_candidate_id", "right_aha_candidate_id",
    }
    observation_fields = {
        "observation_id", "aha_observation_id", "left_observation_id",
        "right_observation_id",
    }
    fact_fields = {"fact_id", "left_fact_id", "right_fact_id"}
    fact_list_fields = {"fact_ids", "chapter_fact_ids", "aha_fact_ids"}
    for relation in payload.get("chapter_aha_relations", []):
        for field in candidate_fields:
            if field in relation:
                relation[field] = candidates.get(str(relation[field]), str(relation[field]))
        for field in observation_fields:
            if field in relation:
                relation[field] = observations.get(str(relation[field]), str(relation[field]))
        for field in fact_fields:
            if field in relation:
                relation[field] = facts.get(str(relation[field]), str(relation[field]))
        for field in fact_list_fields:
            if field in relation:
                relation[field] = _map_list(relation[field], facts)

    payload[POLICY_FIELD] = POLICY_VERSION
    payload["reference_contract"] = (
        "REQUEST_LOCAL_SHORT_IDS_PRIVATE_CANONICAL_MAP_VALIDATED_AFTER_DECODE"
    )
    return payload, maps


def prompt(context, payload, limits):
    """Reuse the accepted writing contract with a short-reference boundary."""
    base = grounded.writer_prompt(context, limits)
    prefix, _ = base.rsplit("Input:\n", 1)
    prefix = prefix.replace("V1.72.1：", "V1.74：")
    instruction = (
        "本次请求中的 C、A、F、O 编号只在本次请求内有效。candidate_id 和 claim_ids "
        "必须从对应卡片现有编号中原样选择；不要补全、改写或猜测编号。每张卡只返回一次。"
        "程序会在本地恢复真实编号并执行原有引用校验；未知或跨卡引用会使该卡失败，且不会重试或用"
        "原始事实、通用套话兜底。\n"
    )
    return prefix + instruction + "Input:\n" + json.dumps(payload, ensure_ascii=False)


def decode_output(output, maps):
    """Restore only known model-returned IDs; leave unknowns to fail closed."""
    if not isinstance(output, dict):
        return output
    result = copy.deepcopy(output)
    candidates = maps["candidates"]
    facts = maps["facts"]
    for bucket in ("chapters", "ahas"):
        values = result.get(bucket)
        if not isinstance(values, list):
            continue
        for item in values:
            if not isinstance(item, dict):
                continue
            candidate = item.get("candidate_id")
            if isinstance(candidate, str) and candidate in candidates:
                item["candidate_id"] = candidates[candidate]
            claims = item.get("claim_ids")
            if isinstance(claims, list):
                item["claim_ids"] = [
                    facts[value] if isinstance(value, str) and value in facts else value
                    for value in claims
                ]
    return result

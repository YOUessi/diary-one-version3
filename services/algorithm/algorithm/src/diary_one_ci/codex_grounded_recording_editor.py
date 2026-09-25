"""V1.72.1 selected relations, focus-frame Aha and single-pass Writer exit.

This module never interprets scene vocabulary and never calls a model.  It
binds one model-authored recommendation to existing candidates and fails local
items closed when the recommendation's pair evidence is incomplete.
"""

import copy
import json
from collections import Counter

from . import codex_content_brief as content_handoff
from . import codex_editorial_allocation as allocation
from . import codex_recording_editor as legacy


POLICY_VERSION = "CODEX_D3_FOCUS_FRAME_WRITER_EXIT_V01"
POLICY_FIELD = legacy.POLICY_FIELD
OUTPUT_FIELD = legacy.OUTPUT_FIELD
CONTEXT_FIELD = legacy.CONTEXT_FIELD
WRITER_POLICY_FIELD = "codex_grounded_writer_policy_version"
AHA_WRITING_TARGET = 20
AHA_VISIBLE_MAX = 24
RELATIONS = ("SAME_STORY", "DISTINCT_STORY", "UNRESOLVED")


def consideration_scope(observations, roles):
    return legacy.consideration_scope(observations, roles)


def input_context():
    return legacy.input_context()


def structure_observations(observations, roles):
    """Send S07 facts and role only; descriptive labels are not fact evidence."""
    role_by_id = {item["observation_id"]: item for item in roles}
    return [{
        "observation_id": item["id"],
        "sequence_index": index,
        "role": role_by_id[item["id"]]["role"],
        "facts": copy.deepcopy(item["facts"]),
    } for index, item in enumerate(observations)]


def structure_moments(moments):
    """Keep only organizational references; derived labels cannot act as facts."""
    return [{
        "id": item["id"],
        "sequence_index": item["sequence_index"],
        "observation_ids": list(item["observation_ids"]),
        "roles": list(item["roles"]),
    } for item in moments]


def _chapter_aha_schema():
    return {
        "type": "object", "additionalProperties": False,
        "required": ["chapter_key", "observation_id", "relation",
                     "chapter_fact_ids", "aha_fact_ids", "reason"],
        "properties": {
            "chapter_key": {"type": "string"},
            "observation_id": {"type": "string"},
            "relation": {"type": "string", "enum": list(RELATIONS)},
            "chapter_fact_ids": {"type": "array", "items": {"type": "string"},
                                 "minItems": 1, "uniqueItems": True},
            "aha_fact_ids": {"type": "array", "items": {"type": "string"},
                             "minItems": 1, "maxItems": 1, "uniqueItems": True},
            "reason": {"type": "string"},
        },
    }


def _aha_aha_schema():
    return {
        "type": "object", "additionalProperties": False,
        "required": ["observation_ids", "relation", "fact_ids", "reason"],
        "properties": {
            "observation_ids": {"type": "array", "items": {"type": "string"},
                                "minItems": 2, "maxItems": 2, "uniqueItems": True},
            "relation": {"type": "string", "enum": list(RELATIONS)},
            "fact_ids": {"type": "array", "items": {"type": "string"},
                         "minItems": 2, "maxItems": 2, "uniqueItems": True},
            "reason": {"type": "string"},
        },
    }


def response_schema(base):
    """Bind the selected relation matrix and one visible focus per Aha."""
    result = copy.deepcopy(base)
    aha_item = result["properties"]["aha_proposals"]["items"]
    aha_facts = aha_item["properties"]["event_fact_ids"]
    aha_facts.update(maxItems=1, uniqueItems=True,
                     description="Exactly one supported fact: the atomic Aha Moment.")
    aha_item["properties"].update({
        "focus_frame_id": {
            "type": "string", "minLength": 1,
            "description": "Exactly one evidence frame belonging to the selected fact.",
        },
        "moment_focus": {
            "type": "string", "minLength": 1, "maxLength": 80,
            "description": (
                "A concise editorial focus: one focal subject and its central action, "
                "state, or discovery. It is not additional fact evidence."
            ),
        },
    })
    for field in ("focus_frame_id", "moment_focus"):
        if field not in aha_item["required"]:
            aha_item["required"].append(field)
    result["properties"][OUTPUT_FIELD] = {
        "type": "object", "additionalProperties": False,
        "required": ["chapter_keys", "aha_selections", "chapter_aha_relations",
                     "aha_aha_relations", "reason"],
        "properties": {
            "chapter_keys": {"type": "array", "items": {"type": "string"},
                             "maxItems": 4, "uniqueItems": True},
            "aha_selections": {
                "type": "array", "maxItems": 3,
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["observation_id", "fact_id", "focus_frame_id",
                                 "moment_focus"],
                    "properties": {
                        "observation_id": {"type": "string"},
                        "fact_id": {"type": "string"},
                        "focus_frame_id": {"type": "string", "minLength": 1},
                        "moment_focus": {"type": "string", "minLength": 1,
                                         "maxLength": 80},
                    },
                },
            },
            "chapter_aha_relations": {"type": "array", "items": _chapter_aha_schema()},
            "aha_aha_relations": {"type": "array", "items": _aha_aha_schema()},
            "reason": {"type": "string"},
        },
    }
    result["properties"][CONTEXT_FIELD] = {
        "type": "object", "additionalProperties": False,
        "required": ["summary", "uncertainty"],
        "properties": {
            "summary": {"type": "string"},
            "uncertainty": {"type": "string"},
        },
    }
    for field in (CONTEXT_FIELD, OUTPUT_FIELD):
        if field not in result["required"]:
            result["required"].append(field)
    for chapter in (result["properties"]["storyline_proposals"],):
        chapter["items"]["properties"]["aha_relations"]["description"] = (
            "Legacy compatibility field. Return an empty array; selected-set relations belong "
            "to the selected-set day_selection matrix."
        )
    return result


def prompt_instruction():
    return (
        "V1.72.1 uses day_selection as one recommendation with a closed pair matrix, not two "
        "complete rankings or a fixed quota. First summarize only what the supplied recording "
        "supports in recording_context and state what remains unknown. It may contain selected "
        "activity segments rather than a complete day. Do not infer wear time, routine, weekday, "
        "personal novelty, missing experiences, capture chronology or GPS from asset count, import "
        "order or video duration. A short recording can still contain worthwhile memories. "
        "Actively consider grounded small discoveries and meaningful ordinary moments across all "
        "usable supported facts; do not require people, action, rarity or a major event, and do not "
        "make an Aha for every observation. Each selected card must add a concrete story duty beyond "
        "the other selected cards. An unselected Chapter does not turn all its fragments into Ahas. "
        "Each aha_proposal must cite exactly one event_fact_id from one observation, choose exactly "
        "one focus_frame_id from that fact's evidence_frame_ids, and give one concise moment_focus "
        "for the focal subject and its central action, state, or discovery. The focus is an editorial "
        "compression hint, not new evidence. Do not join separate actions, states or discoveries "
        "merely because they appear in the same video. A candidate that only supplies a place label, "
        "background explanation, or taxonomy is not sufficient by itself: an Aha must be independently "
        "worth revisiting as a small discovery, interaction, or turn supported by the recording. "
        "In day_selection.aha_selections copy the selected proposal's observation_id, sole fact_id, "
        "focus_frame_id and moment_focus exactly. For EVERY selected "
        "Chapter/Aha pair return exactly one chapter_aha_relations row, and for EVERY unordered "
        "selected Aha/Aha pair return exactly one aha_aha_relations row. Do not return relation "
        "rows for unselected cards. In an Aha/Aha row, observation_ids and fact_ids use the same "
        "order as aha_selections. SAME_STORY means the second card repeats, restates, or extracts "
        "the core story of the first; DISTINCT_STORY requires a concrete different story duty "
        "supported by each cited fact; UNRESOLVED is honest uncertainty. Shared setting, visual "
        "style, subject label or category alone proves neither sameness nor difference. All "
        "selected pairs must be decided as DISTINCT_STORY to coexist. The program will not infer "
        "a missing relation, fill another card, or ask another model call. Return empty legacy "
        "storyline_proposals[*].aha_relations arrays. Descriptive labels are intentionally absent "
        "from V1.72.1 structure input; group and compare only from the supplied facts. Return only "
        "the recommended subset in day_selection.chapter_keys and aha_selections. Existing ceilings "
        "remain: at most four Chapters, at least three KEEP materials per Chapter, at most three "
        "Ahas when Chapters exist and at most one Aha without Chapters. These are ceilings, not quotas. "
    )


def perception_instruction():
    return (
        "V1.72.1 evidence discipline: keep each fact to one coherent visible state, action, or "
        "discovery. If sampled frames show separate events, record them as separate facts instead "
        "of one compound fact. Use exact visible names or text only when clearly legible; otherwise "
        "write the generic visible subject and add an UNCERTAIN_VISIBLE_TEXT limitation. Describe "
        "the weakest action intensity supported by the frames and never upgrade a stationary state "
        "to movement, ordinary movement to faster movement, or uncertainty to certainty. These are "
        "general evidence rules, not rules for any particular scene or object. "
    )


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _unique_text_list(value):
    if (not isinstance(value, list) or not value
            or any(not _text(item) for item in value)
            or len(set(value)) != len(value)):
        return None
    return list(value)


def _chapter_bindings(output, chapter_ledger, chapters):
    counts = Counter(
        item.get("key") for item in chapters
        if isinstance(item, dict) and _text(item.get("key"))
    ) if isinstance(chapters, list) else Counter()
    bindings = {}
    for entry in chapter_ledger:
        index = entry.get("source_index")
        if (entry.get("validation_status") == "PASSED" and isinstance(index, int)
                and isinstance(chapters, list) and 0 <= index < len(chapters)):
            key = chapters[index].get("key") if isinstance(chapters[index], dict) else None
            if _text(key) and counts[key] == 1:
                bindings[key] = entry["candidate_id"]
    return bindings


def _bind_chapters(raw, bindings):
    lane = {"status": "MISSING_OR_INVALID_SELECTION", "recommended_candidate_ids": [],
            "selected_keys": [], "diagnostics": []}
    if not isinstance(raw, list):
        lane["diagnostics"].append({"code": "CHAPTER_SELECTION_LIST_MISSING_OR_INVALID"})
        return lane
    seen = set()
    for index, key in enumerate(raw):
        if not _text(key):
            code = "CHAPTER_SELECTION_REFERENCE_INVALID"
        elif key in seen:
            code = "DUPLICATE_CHAPTER_SELECTION_REFERENCE"
        elif key not in bindings:
            code = "UNKNOWN_OR_AMBIGUOUS_CHAPTER_SELECTION_REFERENCE"
        else:
            code = None
        if _text(key):
            seen.add(key)
        if code:
            lane["diagnostics"].append({"code": code, "index": index, "reference": copy.deepcopy(key)})
        else:
            lane["selected_keys"].append(key)
            lane["recommended_candidate_ids"].append(bindings[key])
    lane["status"] = "PARTIAL_SELECTION_BOUND" if lane["diagnostics"] else "MODEL_SELECTION_BOUND"
    return lane


def _bind_ahas(raw, aha_candidates, proposal_rows, observations):
    lane = {"status": "MISSING_OR_INVALID_SELECTION", "recommended_candidate_ids": [],
            "selections": [], "diagnostics": []}
    if not isinstance(raw, list):
        lane["diagnostics"].append({"code": "AHA_SELECTION_LIST_MISSING_OR_INVALID"})
        return lane
    by_observation = {}
    for candidate in aha_candidates:
        by_observation.setdefault(candidate.get("observation_id"), []).append(candidate)
    proposals_by_observation = {}
    for proposal in proposal_rows if isinstance(proposal_rows, list) else []:
        if isinstance(proposal, dict):
            proposals_by_observation.setdefault(proposal.get("observation_id"), []).append(proposal)
    observations_by_id = {
        item.get("id"): item for item in observations if isinstance(item, dict) and _text(item.get("id"))
    }
    seen = set()
    for index, item in enumerate(raw):
        observation_id = item.get("observation_id") if isinstance(item, dict) else None
        fact_id = item.get("fact_id") if isinstance(item, dict) else None
        focus_frame_id = item.get("focus_frame_id") if isinstance(item, dict) else None
        moment_focus = item.get("moment_focus") if isinstance(item, dict) else None
        matches = by_observation.get(observation_id, []) if _text(observation_id) else []
        proposals = proposals_by_observation.get(observation_id, []) if _text(observation_id) else []
        observation = observations_by_id.get(observation_id)
        fact = next((value for value in observation.get("facts", [])
                     if isinstance(value, dict) and value.get("fact_id") == fact_id), None) \
            if isinstance(observation, dict) else None
        if (not _text(observation_id) or not _text(fact_id)
                or not _text(focus_frame_id) or not _text(moment_focus)):
            code = "AHA_SELECTION_REFERENCE_INVALID"
        elif observation_id in seen:
            code = "DUPLICATE_AHA_SELECTION_REFERENCE"
        elif len(matches) != 1:
            code = "UNKNOWN_OR_AMBIGUOUS_AHA_SELECTION_REFERENCE"
        elif len(matches[0].get("event_fact_ids", [])) != 1:
            code = "AHA_PROPOSAL_NOT_ATOMIC"
        elif matches[0]["event_fact_ids"][0] != fact_id:
            code = "AHA_ATOMIC_FACT_BINDING_MISMATCH"
        elif len(proposals) != 1:
            code = "AHA_FOCUS_PROPOSAL_MISSING_OR_AMBIGUOUS"
        elif proposals[0].get("event_fact_ids") != [fact_id]:
            code = "AHA_FOCUS_PROPOSAL_FACT_MISMATCH"
        elif (proposals[0].get("focus_frame_id") != focus_frame_id
              or proposals[0].get("moment_focus") != moment_focus):
            code = "AHA_SELECTION_FOCUS_COPY_MISMATCH"
        elif fact is None:
            code = "AHA_FOCUS_FACT_NOT_FOUND"
        elif focus_frame_id not in fact.get("evidence_frame_ids", []):
            code = "AHA_FOCUS_FRAME_NOT_IN_SELECTED_FACT"
        else:
            code = None
        if _text(observation_id):
            seen.add(observation_id)
        if code:
            lane["diagnostics"].append({"code": code, "index": index,
                                        "observation_id": observation_id, "fact_id": fact_id,
                                        "focus_frame_id": focus_frame_id})
        else:
            lane["recommended_candidate_ids"].append(matches[0]["candidate_id"])
            lane["selections"].append({"candidate_id": matches[0]["candidate_id"],
                                       "observation_id": observation_id, "fact_id": fact_id,
                                       "focus_frame_id": focus_frame_id,
                                       "moment_focus": moment_focus.strip()})
    lane["status"] = "PARTIAL_SELECTION_BOUND" if lane["diagnostics"] else "MODEL_SELECTION_BOUND"
    return lane


def _relation(reason_code, *, relation="UNRESOLVED", reason="", **fields):
    return {**fields, "relation": relation, "reason": reason,
            "reason_codes": [reason_code]}


def _compile_chapter_aha_rows(raw, chapter_lane, aha_lane, chapters_by_id, ahas_by_id):
    rows = raw if isinstance(raw, list) else []
    diagnostics = [] if isinstance(raw, list) else [{"code": "CHAPTER_AHA_RELATIONS_MISSING_OR_INVALID"}]
    chapter_id_by_key = dict(zip(chapter_lane["selected_keys"], chapter_lane["recommended_candidate_ids"]))
    aha_id_by_observation = {item["observation_id"]: item["candidate_id"] for item in aha_lane["selections"]}
    bound = {}
    for index, row in enumerate(rows):
        key = row.get("chapter_key") if isinstance(row, dict) else None
        observation_id = row.get("observation_id") if isinstance(row, dict) else None
        pair = (chapter_id_by_key.get(key), aha_id_by_observation.get(observation_id))
        if None in pair:
            diagnostics.append({"code": "CHAPTER_AHA_ROW_NOT_IN_SELECTED_SET", "source_index": index})
        else:
            bound.setdefault(pair, []).append((index, row))
    compiled = []
    for chapter_id in chapter_lane["recommended_candidate_ids"]:
        chapter = chapters_by_id[chapter_id]
        for selection in aha_lane["selections"]:
            aha_id = selection["candidate_id"]
            rows_for_pair = bound.get((chapter_id, aha_id), [])
            base = {"chapter_candidate_id": chapter_id, "aha_candidate_id": aha_id,
                    "aha_observation_id": selection["observation_id"],
                    "chapter_fact_ids": [], "aha_fact_ids": []}
            if len(rows_for_pair) != 1:
                code = "CHAPTER_AHA_RELATION_MISSING" if not rows_for_pair else "DUPLICATE_CHAPTER_AHA_RELATION_ROWS"
                item = _relation(code, **base)
            else:
                _, row = rows_for_pair[0]
                chapter_facts = _unique_text_list(row.get("chapter_fact_ids")) if isinstance(row, dict) else None
                aha_facts = _unique_text_list(row.get("aha_fact_ids")) if isinstance(row, dict) else None
                errors = []
                if row.get("relation") not in RELATIONS:
                    errors.append("RELATION_VALUE_INVALID")
                if chapter_facts is None or not set(chapter_facts) <= set(chapter.get("fact_ids", [])):
                    errors.append("CHAPTER_FACT_REFERENCE_INVALID")
                if aha_facts != [selection["fact_id"]]:
                    errors.append("AHA_ATOMIC_FACT_REFERENCE_INVALID")
                if not _text(row.get("reason")):
                    errors.append("RELATION_REASON_MISSING")
                if errors:
                    item = _relation(";".join(errors), **base)
                    item["reason_codes"] = errors
                else:
                    item = _relation(
                        "EXPLICIT_SELECTED_SET_RELATION" if row["relation"] != "UNRESOLVED" else "MODEL_RELATION_UNRESOLVED",
                        relation=row["relation"], reason=row["reason"].strip(),
                        **{**base, "chapter_fact_ids": chapter_facts, "aha_fact_ids": aha_facts},
                    )
            compiled.append(item)
    return compiled, diagnostics


def _compile_aha_aha_rows(raw, aha_lane, ahas_by_id):
    rows = raw if isinstance(raw, list) else []
    diagnostics = [] if isinstance(raw, list) else [{"code": "AHA_AHA_RELATIONS_MISSING_OR_INVALID"}]
    id_by_observation = {item["observation_id"]: item["candidate_id"] for item in aha_lane["selections"]}
    fact_by_id = {item["candidate_id"]: item["fact_id"] for item in aha_lane["selections"]}
    bound = {}
    for index, row in enumerate(rows):
        observation_ids = row.get("observation_ids") if isinstance(row, dict) else None
        candidate_ids = ([id_by_observation.get(value) for value in observation_ids]
                         if isinstance(observation_ids, list) and len(observation_ids) == 2 else [])
        if len(candidate_ids) != 2 or None in candidate_ids or candidate_ids[0] == candidate_ids[1]:
            diagnostics.append({"code": "AHA_AHA_ROW_NOT_IN_SELECTED_SET", "source_index": index})
        else:
            bound.setdefault(frozenset(candidate_ids), []).append((index, row, candidate_ids))
    compiled = []
    selections = aha_lane["selections"]
    for left_index, left in enumerate(selections):
        for right in selections[left_index + 1:]:
            left_id, right_id = left["candidate_id"], right["candidate_id"]
            rows_for_pair = bound.get(frozenset((left_id, right_id)), [])
            base = {"left_aha_candidate_id": left_id, "right_aha_candidate_id": right_id,
                    "left_observation_id": left["observation_id"],
                    "right_observation_id": right["observation_id"],
                    "left_fact_id": left["fact_id"], "right_fact_id": right["fact_id"]}
            if len(rows_for_pair) != 1:
                code = "AHA_AHA_RELATION_MISSING" if not rows_for_pair else "DUPLICATE_AHA_AHA_RELATION_ROWS"
                item = _relation(code, **base)
            else:
                _, row, candidate_ids = rows_for_pair[0]
                facts = row.get("fact_ids") if isinstance(row, dict) else None
                aligned = ([fact_by_id[candidate_ids[0]], fact_by_id[candidate_ids[1]]]
                           if len(candidate_ids) == 2 else [])
                errors = []
                if row.get("relation") not in RELATIONS:
                    errors.append("RELATION_VALUE_INVALID")
                if facts != aligned:
                    errors.append("AHA_AHA_FACT_ALIGNMENT_INVALID")
                if not _text(row.get("reason")):
                    errors.append("RELATION_REASON_MISSING")
                if errors:
                    item = _relation(";".join(errors), **base)
                    item["reason_codes"] = errors
                else:
                    item = _relation(
                        "EXPLICIT_SELECTED_SET_RELATION" if row["relation"] != "UNRESOLVED" else "MODEL_RELATION_UNRESOLVED",
                        relation=row["relation"], reason=row["reason"].strip(), **base,
                    )
            compiled.append(item)
    return compiled, diagnostics


def compile_plan(output, chapter_ledger, chapter_candidates, aha_candidates, scope,
                 observations):
    output = output if isinstance(output, dict) else {}
    selected = output.get(OUTPUT_FIELD)
    selected = selected if isinstance(selected, dict) else {}
    chapter_rows = output.get("storyline_proposals")
    chapter_bindings = _chapter_bindings(output, chapter_ledger, chapter_rows)
    chapters = _bind_chapters(selected.get("chapter_keys"), chapter_bindings)
    ahas = _bind_ahas(
        selected.get("aha_selections"), aha_candidates,
        output.get("aha_proposals"), observations,
    )
    chapters_by_id = {item["candidate_id"]: item for item in chapter_candidates}
    ahas_by_id = {item["candidate_id"]: item for item in aha_candidates}
    chapter_aha, ca_diagnostics = _compile_chapter_aha_rows(
        selected.get("chapter_aha_relations"), chapters, ahas, chapters_by_id, ahas_by_id,
    )
    aha_aha, aa_diagnostics = _compile_aha_aha_rows(
        selected.get("aha_aha_relations"), ahas, ahas_by_id,
    )
    context = output.get(CONTEXT_FIELD)
    context = context if isinstance(context, dict) else {}
    diagnostics = [*ca_diagnostics, *aa_diagnostics]
    for field in ("summary", "uncertainty"):
        if not _text(context.get(field)):
            diagnostics.append({"code": "RECORDING_CONTEXT_FIELD_MISSING", "field": field})
    if not _text(selected.get("reason")):
        diagnostics.append({"code": "JOINT_SELECTION_REASON_MISSING"})
    diagnostics.extend(chapters["diagnostics"])
    diagnostics.extend(ahas["diagnostics"])
    return {
        "policy_version": POLICY_VERSION,
        "guidance_scope": "EDITORIAL_RELATIONS_NOT_VISUAL_FACT_EVIDENCE",
        "recording_input_context": input_context(),
        CONTEXT_FIELD: copy.deepcopy(context),
        "reason": selected.get("reason") if isinstance(selected.get("reason"), str) else None,
        "aha_consideration_scope": copy.deepcopy(scope),
        "chapters": chapters, "ahas": ahas,
        "chapter_aha_relations": chapter_aha,
        "aha_aha_relations": aha_aha,
        "diagnostics": diagnostics,
        "additional_model_calls": 0,
        "semantic_quality": "MODEL_AUTHORED_PAIR_RELATIONS_BOUND_NOT_GROUND_TRUTH",
    }


def _chapter_relation(plan, chapter_id, aha_id):
    matches = [row for row in plan["chapter_aha_relations"]
               if row["chapter_candidate_id"] == chapter_id and row["aha_candidate_id"] == aha_id]
    return matches[0] if len(matches) == 1 else _relation(
        "CHAPTER_AHA_RELATION_MISSING_OR_AMBIGUOUS", chapter_candidate_id=chapter_id,
        aha_candidate_id=aha_id, chapter_fact_ids=[], aha_fact_ids=[], aha_observation_id="",
    )


def _aha_relation(plan, left_id, right_id):
    matches = [row for row in plan["aha_aha_relations"]
               if {row["left_aha_candidate_id"], row["right_aha_candidate_id"]} == {left_id, right_id}]
    return matches[0] if len(matches) == 1 else _relation(
        "AHA_AHA_RELATION_MISSING_OR_AMBIGUOUS", left_aha_candidate_id=left_id,
        right_aha_candidate_id=right_id, left_observation_id="", right_observation_id="",
        left_fact_id="", right_fact_id="",
    )


def _mark_ledger(ledger, selected_ids, rejections, lane_status):
    for entry in ledger:
        if entry.get("validation_status") != "PASSED":
            continue
        candidate_id = entry["candidate_id"]
        selected = candidate_id in selected_ids
        entry["selection_status"] = "SELECTED" if selected else "NOT_SELECTED"
        entry["reason_codes"].append(
            "EXPLICIT_MODEL_RECOMMENDATION_WITH_CLOSED_RELATIONS"
            if selected else rejections.get(candidate_id, "MODEL_DID_NOT_RECOMMEND"
                                             if lane_status == "MODEL_SELECTION_BOUND"
                                             else "NOT_IN_VALID_RECOMMENDATION_PART"))


def execute_plan(plan, chapters, chapter_ledger, ahas, aha_ledger, observations, asset_order,
                 *, minimum, max_chapters, max_ahas, max_ahas_without_chapters=1):
    chapters_by_id = {item["candidate_id"]: item for item in chapters}
    ahas_by_id = {item["candidate_id"]: item for item in ahas}
    observation_by_id = {item["id"]: item for item in observations}
    chosen_chapters, chapter_rejections, chapter_checks = [], {}, []
    for candidate_id in plan["chapters"]["recommended_candidate_ids"]:
        candidate = chapters_by_id[candidate_id]
        if len(candidate["source_asset_ids"]) < minimum:
            chapter_rejections[candidate_id] = "CHAPTER_DISPLAY_NEEDS_THREE_MATERIALS"
            continue
        shared = next((set(candidate["source_asset_ids"]) & set(other["source_asset_ids"])
                       for other in chosen_chapters
                       if set(candidate["source_asset_ids"]) & set(other["source_asset_ids"])), None)
        chapter_checks.append({"candidate_id": candidate_id,
                               "shared_asset_ids": sorted(shared or [])})
        if shared:
            chapter_rejections[candidate_id] = "EXACT_SHARED_CHAPTER_ASSET"
        elif len(chosen_chapters) >= max_chapters:
            chapter_rejections[candidate_id] = "INHERITED_PREVIEW_CAPACITY_REACHED"
        else:
            chosen_chapters.append(copy.deepcopy(candidate))
    chosen_chapters.sort(key=lambda item: min(asset_order[value] for value in item["source_asset_ids"]))
    chosen_chapter_ids = [item["candidate_id"] for item in chosen_chapters]
    _mark_ledger(chapter_ledger, set(chosen_chapter_ids), chapter_rejections, plan["chapters"]["status"])

    chosen_ahas, aha_rejections, aha_checks = [], {}, []
    selection_by_id = {item["candidate_id"]: item for item in plan["ahas"]["selections"]}
    capacity = max_ahas if chosen_chapters else max_ahas_without_chapters
    for candidate_id in plan["ahas"]["recommended_candidate_ids"]:
        candidate = ahas_by_id[candidate_id]
        selection = selection_by_id[candidate_id]
        reason = None
        if len(candidate.get("event_fact_ids", [])) != 1:
            reason = "AHA_PROPOSAL_NOT_ATOMIC"
        chapter_rows = [_chapter_relation(plan, chapter_id, candidate_id)
                        for chapter_id in chosen_chapter_ids]
        for row in chapter_rows:
            if row["relation"] == "SAME_STORY":
                reason = reason or "SAME_MODEL_ALLOCATED_CHAPTER_STORY"
            elif row["relation"] != "DISTINCT_STORY":
                reason = reason or "CHAPTER_AHA_RELATION_UNRESOLVED"
        aha_rows = [_aha_relation(plan, other["candidate_id"], candidate_id)
                    for other in chosen_ahas]
        for row in aha_rows:
            if row["relation"] == "SAME_STORY":
                reason = reason or "SAME_MODEL_ALLOCATED_AHA_STORY"
            elif row["relation"] != "DISTINCT_STORY":
                reason = reason or "AHA_AHA_RELATION_UNRESOLVED"
        if len(chosen_ahas) >= capacity:
            reason = reason or "INHERITED_PREVIEW_CAPACITY_REACHED"
        aha_checks.append({"aha_candidate_id": candidate_id,
                           "chapter_relations": copy.deepcopy(chapter_rows),
                           "prior_aha_relations": copy.deepcopy(aha_rows),
                           "decision": "REJECT" if reason else "KEEP",
                           "reason_code": reason})
        if reason:
            aha_rejections[candidate_id] = reason
            continue
        selected = copy.deepcopy(candidate)
        selected["atomic_fact_id"] = selection["fact_id"]
        selected["focus_frame_id"] = selection["focus_frame_id"]
        selected["moment_focus"] = selection["moment_focus"]
        selected["fact_ids"] = [selection["fact_id"]]
        selected["event_fact_ids"] = [selection["fact_id"]]
        selected["moment_evidence_frame_ids"] = [selection["focus_frame_id"]]
        chosen_ahas.append(selected)
    chosen_ahas.sort(key=lambda item: (asset_order[item["source_asset_id"]], item["candidate_id"]))
    chosen_aha_ids = [item["candidate_id"] for item in chosen_ahas]
    _mark_ledger(aha_ledger, set(chosen_aha_ids), aha_rejections, plan["ahas"]["status"])

    chapter_audit = {
        "algorithm": "EXPLICIT_SELECTION_WITH_TECHNICAL_CHAPTER_CONSTRAINTS",
        "recommended_candidate_ids": list(plan["chapters"]["recommended_candidate_ids"]),
        "selected_candidate_ids": chosen_chapter_ids,
        "published_sequence_candidate_ids": chosen_chapter_ids,
        "pair_ledger": chapter_checks, "rejections": chapter_rejections,
        "selection_binding_status": plan["chapters"]["status"],
        "proxy_value_thresholds_applied": False, "automatic_fill_applied": False,
        "eligible_candidate_count": len(chapters), "capacity": max_chapters,
    }
    if chosen_ahas:
        outcome = "ATOMIC_AHAS_WITH_CLOSED_SELECTED_PAIR_RELATIONS"
    elif plan["ahas"]["status"] != "MODEL_SELECTION_BOUND":
        outcome = "AHA_RECOMMENDATION_TECHNICALLY_UNRESOLVED"
    elif plan["ahas"]["recommended_candidate_ids"]:
        outcome = "RECOMMENDED_AHAS_REJECTED_BY_ATOMIC_OR_RELATION_CONTRACT"
    else:
        outcome = "MODEL_RECOMMENDED_NO_AHA_NOT_PROOF_OF_NO_VALUE"
    aha_audit = {
        "algorithm": "ORDERED_ATOMIC_AHA_SELECTION_WITH_CLOSED_PAIR_MATRIX",
        "recommended_candidate_ids": list(plan["ahas"]["recommended_candidate_ids"]),
        "selected_candidate_ids": chosen_aha_ids,
        "published_sequence_candidate_ids": chosen_aha_ids,
        "pair_ledger": aha_checks, "rejections": aha_rejections,
        "selection_binding_status": plan["ahas"]["status"],
        "proxy_value_thresholds_applied": False, "automatic_fill_applied": False,
        "eligible_candidate_count": len(ahas), "capacity": capacity,
        "search_outcome": outcome, "search_contract": POLICY_VERSION,
        "event_category_gating_applied": False, "motif_overlap_gating_applied": False,
    }
    complete = (not plan["diagnostics"] and not chapter_rejections and not aha_rejections
                and plan["chapters"]["status"] == "MODEL_SELECTION_BOUND"
                and plan["ahas"]["status"] == "MODEL_SELECTION_BOUND")
    plan["execution_status"] = (
        "COMPLETE_CLOSED_RELATION_RECOMMENDATION_EXECUTED"
        if complete else "PARTIAL_OR_UNRESOLVED_RECOMMENDATION"
    )
    return chosen_chapters, chosen_ahas, chapter_audit, aha_audit


def allocation_plan(plan):
    """Project selected Chapter/Aha rows into the existing Writer handoff shape."""
    return {
        "policy_version": allocation.POLICY_VERSION,
        "guidance_scope": allocation.GUIDANCE_SCOPE,
        "relations": copy.deepcopy(plan.get("chapter_aha_relations", [])),
        "diagnostics": copy.deepcopy(plan.get("diagnostics", [])),
    }


def writer_response_schema(base):
    result = copy.deepcopy(base)
    result["properties"]["ahas"]["items"] = copy.deepcopy(
        result["properties"]["ahas"]["items"]
    )
    result["properties"]["ahas"]["items"]["properties"]["text"].update({
        "maxLength": AHA_VISIBLE_MAX,
        "description": (
            "One user-visible Aha sentence. Target 20 visible characters; hard delivery "
            "maximum 24. Use only the sole atomic fact."
        ),
    })
    return result


def writer_input(context):
    payload = content_handoff.writer_input(context)
    payload[WRITER_POLICY_FIELD] = POLICY_VERSION
    cautions = {item["candidate_id"]: list(item.get("evidence_cautions", []))
                for item in context["memories"]}
    focuses = {item["candidate_id"]: item.get("moment_focus")
               for item in context["memories"] if item.get("memory_type") == "AHA"}
    for item in payload["memories"]:
        item["evidence_cautions"] = cautions.get(item["candidate_id"], [])
        if item["memory_type"] == "AHA":
            item["moment_focus"] = focuses.get(item["candidate_id"])
    return payload


def writer_prompt(context, limits):
    base = content_handoff.writer_prompt(context, retry=False, limits=limits)
    prefix, _ = base.rsplit("Input:\n", 1)
    instruction = (
        "V1.72.1：每条 Aha 只有一个事实和一个焦点帧，text 以 20 字为目标并且绝对不超过 24 字；"
        "这是一次输出，不会再调用模型改写。输出前自行计数。若 evidence_cautions 表示可见文字不确定，"
        "不要恢复精确店名、地名或文字；只写事实中有把握的通用对象。动作使用事实支持的最低强度，"
        "不把静止写成移动、不把普通移动升级为快速动作、不把可能写成确定。Aha 围绕 moment_focus，"
        "通常只保留一个主体和一个中心动作、状态或发现；除非理解这一刻必需，否则省略背景、颜色、"
        "装饰、物品清单、拍摄过程和其他修饰。moment_focus 不是新事实，任何用词仍须由 facts 支持。"
        "目标语言有自然常用表达时，不混入未解释的外语词。以上适用于所有场景，"
        "不得添加基于示例对象的特例。\n"
    )
    return prefix + instruction + "Input:\n" + json.dumps(writer_input(context), ensure_ascii=False)


def writer_enabled(context):
    return context.get(WRITER_POLICY_FIELD) == POLICY_VERSION

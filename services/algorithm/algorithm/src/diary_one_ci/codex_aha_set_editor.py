"""V1.73 two-stage Aha shortlist and set editor.

S07 remains responsible for grounded Chapter proposals and atomic Aha
nominations.  This module binds that output, prepares one text-only S09
editor request with request-local references, and deterministically executes
the returned set.  It never ranks by scene tags and never retries or fills a
rejected set.
"""

import copy
from itertools import combinations

from . import codex_grounded_recording_editor as grounded


POLICY_VERSION = "CODEX_D4_AHA_SET_EDITOR_V01"
POLICY_FIELD = grounded.POLICY_FIELD
OUTPUT_FIELD = grounded.OUTPUT_FIELD
CONTEXT_FIELD = grounded.CONTEXT_FIELD
WRITER_POLICY_FIELD = grounded.WRITER_POLICY_FIELD
EDITOR_STAGE = "S09_AHA_SET_EDITOR"
SHORTLIST_MAX = 8
MAX_AHAS = 3
REVIEW_STATUSES = ("STANDALONE", "CHAPTER_SUPPORT", "UNRESOLVED")
RELATIONS = grounded.RELATIONS


def consideration_scope(observations, roles):
    return grounded.consideration_scope(observations, roles)


def input_context():
    return grounded.input_context()


def structure_observations(observations, roles):
    return grounded.structure_observations(observations, roles)


def structure_moments(moments):
    return grounded.structure_moments(moments)


def perception_instruction():
    return grounded.perception_instruction()


def response_schema(base):
    """Make S07 a discovery stage, not the final Aha set decision."""
    result = grounded.response_schema(base)
    result["properties"]["aha_proposals"]["maxItems"] = SHORTLIST_MAX
    result["properties"][OUTPUT_FIELD] = {
        "type": "object",
        "additionalProperties": False,
        "required": ["chapter_keys", "reason"],
        "properties": {
            "chapter_keys": {
                "type": "array", "items": {"type": "string"},
                "maxItems": 4, "uniqueItems": True,
            },
            "reason": {"type": "string"},
        },
    }
    return result


def prompt_instruction():
    return (
        "V1.73 separates discovery from final Aha set editing. In this S07 call, select the "
        "recommended Chapter keys and nominate at most eight grounded atomic Aha candidates; do "
        "not select the final Aha set and do not return Chapter/Aha or Aha/Aha relation matrices. "
        "The eight-candidate limit is a shortlist ceiling, not a target. Each Aha nomination must "
        "still contain exactly one supported fact, one evidence frame belonging to that fact, and "
        "one concise moment_focus. Search across all usable supported facts, including small ordinary "
        "discoveries, without using tags, scene categories, object names, asset count, import order, "
        "quality scores, rarity proxies or a fixed output quota as proof of memory value. A shared "
        "setting does not make two stories the same; a different object or name does not make them "
        "different. Return empty legacy storyline_proposals[*].aha_relations arrays. A separate "
        "text-only editor will compare the validated shortlist once after S07. "
    )


def compile_discovery(output, chapter_ledger, chapter_candidates, aha_candidates, scope,
                      observations):
    """Bind S07 Chapters and every valid atomic nomination into a shortlist."""
    output = output if isinstance(output, dict) else {}
    selected = output.get(OUTPUT_FIELD)
    selected = selected if isinstance(selected, dict) else {}
    proposals = output.get("aha_proposals")
    proposals = proposals if isinstance(proposals, list) else []
    diagnostics = []
    if len(proposals) > SHORTLIST_MAX:
        diagnostics.append({
            "code": "AHA_SHORTLIST_EXCEEDS_MAXIMUM",
            "reported_count": len(proposals),
            "maximum": SHORTLIST_MAX,
        })
        proposals = proposals[:SHORTLIST_MAX]

    chapter_bindings = grounded._chapter_bindings(
        output, chapter_ledger, output.get("storyline_proposals")
    )
    chapters = grounded._bind_chapters(selected.get("chapter_keys"), chapter_bindings)
    raw_ahas = []
    for proposal in proposals:
        if not isinstance(proposal, dict):
            raw_ahas.append(proposal)
            continue
        fact_ids = proposal.get("event_fact_ids")
        fact_id = fact_ids[0] if isinstance(fact_ids, list) and len(fact_ids) == 1 else None
        raw_ahas.append({
            "observation_id": proposal.get("observation_id"),
            "fact_id": fact_id,
            "focus_frame_id": proposal.get("focus_frame_id"),
            "moment_focus": proposal.get("moment_focus"),
        })
    shortlist = grounded._bind_ahas(
        raw_ahas, aha_candidates, proposals, observations,
    )

    context = output.get(CONTEXT_FIELD)
    context = context if isinstance(context, dict) else {}
    for field in ("summary", "uncertainty"):
        if not grounded._text(context.get(field)):
            diagnostics.append({"code": "RECORDING_CONTEXT_FIELD_MISSING", "field": field})
    if not grounded._text(selected.get("reason")):
        diagnostics.append({"code": "CHAPTER_SELECTION_REASON_MISSING"})
    diagnostics.extend(chapters["diagnostics"])
    diagnostics.extend(shortlist["diagnostics"])
    return {
        "policy_version": POLICY_VERSION,
        "guidance_scope": "TWO_STAGE_EDITORIAL_JUDGMENT_NOT_VISUAL_FACT_EVIDENCE",
        "recording_input_context": input_context(),
        CONTEXT_FIELD: copy.deepcopy(context),
        "reason": selected.get("reason") if isinstance(selected.get("reason"), str) else None,
        "aha_consideration_scope": copy.deepcopy(scope),
        "chapters": chapters,
        "aha_shortlist": shortlist,
        "diagnostics": diagnostics,
        "additional_model_calls": 1,
        "semantic_quality": "S07_DISCOVERY_BOUND_NOT_FINAL_AHA_SET",
    }


def preview_selected_chapters(plan, chapter_candidates, asset_order, *, minimum,
                              max_chapters):
    """Mirror the final technical Chapter constraints without touching ledgers."""
    by_id = {item["candidate_id"]: item for item in chapter_candidates}
    chosen = []
    for candidate_id in plan["chapters"]["recommended_candidate_ids"]:
        candidate = by_id.get(candidate_id)
        if candidate is None or len(candidate.get("source_asset_ids", [])) < minimum:
            continue
        sources = set(candidate["source_asset_ids"])
        if any(sources & set(other["source_asset_ids"]) for other in chosen):
            continue
        if len(chosen) >= max_chapters:
            continue
        chosen.append(copy.deepcopy(candidate))
    chosen.sort(key=lambda item: min(asset_order[value] for value in item["source_asset_ids"]))
    return chosen


def _fact_lookup(observations):
    facts = {}
    limitations = {}
    for observation in observations:
        for fact in observation.get("facts", []):
            fact_id = fact.get("fact_id")
            if grounded._text(fact_id):
                facts[fact_id] = fact
                limitations[fact_id] = [
                    value for value in observation.get("limitations", [])
                    if grounded._text(value)
                ]
    return facts, limitations


def editor_input(discovery_plan, selected_chapters, chapter_candidates, aha_candidates,
                 observations):
    """Return a text-only request payload and a private reversible ID map."""
    facts, limitations = _fact_lookup(observations)
    chapter_by_id = {item["candidate_id"]: item for item in chapter_candidates}
    aha_by_id = {item["candidate_id"]: item for item in aha_candidates}
    fact_to_short = {}

    def short_fact(fact_id):
        if fact_id not in fact_to_short:
            fact_to_short[fact_id] = "F%03d" % (len(fact_to_short) + 1)
        return fact_to_short[fact_id]

    chapter_map = {}
    chapter_fact_map = {}
    chapter_rows = []
    selected_keys = discovery_plan["chapters"].get("selected_keys", [])
    key_by_id = dict(zip(
        discovery_plan["chapters"].get("recommended_candidate_ids", []), selected_keys,
    ))
    for index, selected in enumerate(selected_chapters, 1):
        short_id = "C%02d" % index
        candidate_id = selected["candidate_id"]
        candidate = chapter_by_id[candidate_id]
        chapter_map[short_id] = candidate_id
        chapter_fact_map[short_id] = []
        fact_rows = []
        for fact_id in candidate.get("fact_ids", []):
            fact = facts.get(fact_id)
            if fact is None:
                continue
            fact_short = short_fact(fact_id)
            chapter_fact_map[short_id].append(fact_short)
            row = {
                "fact_id": fact_short,
                "text": fact.get("text", ""),
                "support_grade": fact.get("support_grade", "UNKNOWN"),
            }
            if limitations.get(fact_id):
                row["evidence_cautions"] = limitations[fact_id]
            fact_rows.append(row)
        chapter_rows.append({
            "candidate_id": short_id,
            "thesis": candidate.get("storyline_identity", {}).get("thesis", ""),
            "facts": fact_rows,
        })

    aha_map = {}
    aha_selection_map = {}
    aha_fact_map = {}
    aha_rows = []
    for index, selection in enumerate(
        discovery_plan["aha_shortlist"].get("selections", [])[:SHORTLIST_MAX], 1
    ):
        short_id = "A%02d" % index
        candidate_id = selection["candidate_id"]
        candidate = aha_by_id.get(candidate_id)
        fact_id = selection["fact_id"]
        fact = facts.get(fact_id)
        if candidate is None or fact is None:
            continue
        fact_short = short_fact(fact_id)
        aha_map[short_id] = candidate_id
        aha_selection_map[short_id] = copy.deepcopy(selection)
        aha_fact_map[short_id] = fact_short
        aha_rows.append({
            "candidate_id": short_id,
            "fact": {
                "fact_id": fact_short,
                "text": fact.get("text", ""),
                "support_grade": fact.get("support_grade", "UNKNOWN"),
            },
            "moment_focus": selection["moment_focus"],
            "narrative_duty": candidate.get("narrative_duty", ""),
            "evidence_cautions": limitations.get(fact_id, []),
        })

    context = {
        "policy_version": POLICY_VERSION,
        "recording_context": copy.deepcopy(discovery_plan.get(CONTEXT_FIELD, {})),
        "quantity_contract": {
            "allowed_aha_count": {"minimum": 0, "maximum": MAX_AHAS},
            "active_quality_target_when_supported": "2_TO_3",
            "one_is_valid": True,
            "zero_requires_no_grounded_standalone_choice": True,
            "quota_or_automatic_fill": False,
        },
        "chapters": chapter_rows,
        "aha_candidates": aha_rows,
    }
    maps = {
        "chapters": chapter_map,
        "chapter_keys": {short: key_by_id.get(long) for short, long in chapter_map.items()},
        "chapter_facts": chapter_fact_map,
        "ahas": aha_map,
        "aha_selections": aha_selection_map,
        "aha_facts": aha_fact_map,
        "facts": {short: long for long, short in fact_to_short.items()},
    }
    return context, maps


def editor_response_schema():
    relation_enum = {"type": "string", "enum": list(RELATIONS)}
    return {
        "type": "object", "additionalProperties": False,
        "required": ["candidate_reviews", "selected_aha_ids", "chapter_aha_relations",
                     "aha_aha_relations", "set_reason"],
        "properties": {
            "candidate_reviews": {
                "type": "array", "maxItems": SHORTLIST_MAX,
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["candidate_id", "status", "reason"],
                    "properties": {
                        "candidate_id": {"type": "string"},
                        "status": {"type": "string", "enum": list(REVIEW_STATUSES)},
                        "reason": {"type": "string"},
                    },
                },
            },
            "selected_aha_ids": {
                "type": "array", "items": {"type": "string"},
                "maxItems": MAX_AHAS, "uniqueItems": True,
            },
            "chapter_aha_relations": {
                "type": "array",
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["chapter_candidate_id", "aha_candidate_id", "relation",
                                 "chapter_fact_ids", "aha_fact_id", "reason"],
                    "properties": {
                        "chapter_candidate_id": {"type": "string"},
                        "aha_candidate_id": {"type": "string"},
                        "relation": relation_enum,
                        "chapter_fact_ids": {
                            "type": "array", "items": {"type": "string"},
                            "minItems": 1, "uniqueItems": True,
                        },
                        "aha_fact_id": {"type": "string"},
                        "reason": {"type": "string"},
                    },
                },
            },
            "aha_aha_relations": {
                "type": "array",
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["aha_candidate_ids", "relation", "fact_ids", "reason"],
                    "properties": {
                        "aha_candidate_ids": {
                            "type": "array", "items": {"type": "string"},
                            "minItems": 2, "maxItems": 2, "uniqueItems": True,
                        },
                        "relation": relation_enum,
                        "fact_ids": {
                            "type": "array", "items": {"type": "string"},
                            "minItems": 2, "maxItems": 2,
                        },
                        "reason": {"type": "string"},
                    },
                },
            },
            "set_reason": {"type": "string"},
        },
    }


def editor_prompt(context):
    import json

    return (
        "You are the one-pass S09 Aha Set Editor. The supplied Chapters and Aha candidates have "
        "already passed fact/reference checks; judge editorial story duties only from their text. "
        "Review every Aha candidate exactly once as STANDALONE, CHAPTER_SUPPORT, or UNRESOLVED. "
        "STANDALONE means independently worth revisiting and not the same story as any selected "
        "Chapter. CHAPTER_SUPPORT means its central recall experience is already carried by a "
        "Chapter. UNRESOLVED means the supplied facts do not support a confident decision. Select "
        "only STANDALONE candidates. Zero to three Ahas are allowed; when evidence supports them, "
        "actively seek two or three, while one remains valid and no quota may force weak content. "
        "Two Ahas in a shared theme may coexist only when they provide concretely different recall "
        "experiences; different names, objects, wording, crops, or place labels alone are not enough. "
        "For every selected Chapter/Aha pair and every unordered selected Aha/Aha pair, return exactly "
        "one relation row with cited supplied fact IDs. SAME_STORY suppresses the later Aha; "
        "DISTINCT_STORY permits coexistence; UNRESOLVED does not prove independence. Do not invent "
        "facts, reinterpret the focus, rank by metadata, rewrite candidates, request images, fill after "
        "a rejection, or ask for another model call. Give concise decision reasons, not hidden reasoning. "
        "Return only the schema object. Input:\n" + json.dumps(context, ensure_ascii=False)
    )


def _unresolved_relation(code, **fields):
    return {
        **fields,
        "relation": "UNRESOLVED",
        "reason": "",
        "reason_codes": [code],
    }


def _compile_chapter_aha(output, selected_ids, selected_chapters, context, maps):
    rows = output.get("chapter_aha_relations")
    rows = rows if isinstance(rows, list) else []
    diagnostics = [] if isinstance(output.get("chapter_aha_relations"), list) else [
        {"code": "CHAPTER_AHA_RELATIONS_MISSING_OR_INVALID"}
    ]
    selected_set = set(selected_ids)
    chapter_set = {
        short for short, long in maps["chapters"].items()
        if any(item["candidate_id"] == long for item in selected_chapters)
    }
    bound = {}
    for index, row in enumerate(rows):
        chapter_id = row.get("chapter_candidate_id") if isinstance(row, dict) else None
        aha_id = row.get("aha_candidate_id") if isinstance(row, dict) else None
        if chapter_id not in chapter_set or aha_id not in selected_set:
            diagnostics.append({"code": "CHAPTER_AHA_ROW_NOT_IN_SELECTED_SET", "source_index": index})
            continue
        bound.setdefault((chapter_id, aha_id), []).append(row)

    compiled = []
    reverse_facts = maps["facts"]
    for chapter_id in sorted(chapter_set):
        for aha_id in selected_ids:
            base = {
                "chapter_candidate_id": maps["chapters"][chapter_id],
                "aha_candidate_id": maps["ahas"][aha_id],
                "aha_observation_id": maps["aha_selections"][aha_id]["observation_id"],
                "chapter_fact_ids": [], "aha_fact_ids": [],
            }
            matches = bound.get((chapter_id, aha_id), [])
            if len(matches) != 1:
                code = "CHAPTER_AHA_RELATION_MISSING" if not matches else "DUPLICATE_CHAPTER_AHA_RELATION_ROWS"
                compiled.append(_unresolved_relation(code, **base))
                continue
            row = matches[0]
            fact_ids = row.get("chapter_fact_ids")
            errors = []
            if row.get("relation") not in RELATIONS:
                errors.append("RELATION_VALUE_INVALID")
            if (not isinstance(fact_ids, list) or not fact_ids
                    or len(set(fact_ids)) != len(fact_ids)
                    or not set(fact_ids) <= set(maps["chapter_facts"].get(chapter_id, []))):
                errors.append("CHAPTER_FACT_REFERENCE_INVALID")
            if row.get("aha_fact_id") != maps["aha_facts"].get(aha_id):
                errors.append("AHA_ATOMIC_FACT_REFERENCE_INVALID")
            if not grounded._text(row.get("reason")):
                errors.append("RELATION_REASON_MISSING")
            if errors:
                item = _unresolved_relation(errors[0], **base)
                item["reason_codes"] = errors
            else:
                item = {
                    **base,
                    "chapter_fact_ids": [reverse_facts[value] for value in fact_ids],
                    "aha_fact_ids": [reverse_facts[row["aha_fact_id"]]],
                    "relation": row["relation"],
                    "reason": row["reason"].strip(),
                    "reason_codes": [
                        "EXPLICIT_SELECTED_SET_RELATION"
                        if row["relation"] != "UNRESOLVED" else "MODEL_RELATION_UNRESOLVED"
                    ],
                }
            compiled.append(item)
    return compiled, diagnostics


def _compile_aha_aha(output, selected_ids, maps):
    rows = output.get("aha_aha_relations")
    rows = rows if isinstance(rows, list) else []
    diagnostics = [] if isinstance(output.get("aha_aha_relations"), list) else [
        {"code": "AHA_AHA_RELATIONS_MISSING_OR_INVALID"}
    ]
    selected_set = set(selected_ids)
    bound = {}
    for index, row in enumerate(rows):
        ids = row.get("aha_candidate_ids") if isinstance(row, dict) else None
        if (not isinstance(ids, list) or len(ids) != 2 or len(set(ids)) != 2
                or not set(ids) <= selected_set):
            diagnostics.append({"code": "AHA_AHA_ROW_NOT_IN_SELECTED_SET", "source_index": index})
            continue
        bound.setdefault(frozenset(ids), []).append(row)

    compiled = []
    for left, right in combinations(selected_ids, 2):
        left_selection = maps["aha_selections"][left]
        right_selection = maps["aha_selections"][right]
        base = {
            "left_aha_candidate_id": maps["ahas"][left],
            "right_aha_candidate_id": maps["ahas"][right],
            "left_observation_id": left_selection["observation_id"],
            "right_observation_id": right_selection["observation_id"],
            "left_fact_id": left_selection["fact_id"],
            "right_fact_id": right_selection["fact_id"],
        }
        matches = bound.get(frozenset((left, right)), [])
        if len(matches) != 1:
            code = "AHA_AHA_RELATION_MISSING" if not matches else "DUPLICATE_AHA_AHA_RELATION_ROWS"
            compiled.append(_unresolved_relation(code, **base))
            continue
        row = matches[0]
        row_ids = row.get("aha_candidate_ids")
        aligned = [maps["aha_facts"].get(value) for value in row_ids]
        errors = []
        if row.get("relation") not in RELATIONS:
            errors.append("RELATION_VALUE_INVALID")
        if row.get("fact_ids") != aligned:
            errors.append("AHA_AHA_FACT_ALIGNMENT_INVALID")
        if not grounded._text(row.get("reason")):
            errors.append("RELATION_REASON_MISSING")
        if errors:
            item = _unresolved_relation(errors[0], **base)
            item["reason_codes"] = errors
        else:
            item = {
                **base,
                "relation": row["relation"],
                "reason": row["reason"].strip(),
                "reason_codes": [
                    "EXPLICIT_SELECTED_SET_RELATION"
                    if row["relation"] != "UNRESOLVED" else "MODEL_RELATION_UNRESOLVED"
                ],
            }
        compiled.append(item)
    return compiled, diagnostics


def compile_editor(output, context, maps, discovery_plan, selected_chapters,
                   chapter_candidates, aha_candidates):
    """Bind one editor response; preserve valid siblings on local row failures."""
    del chapter_candidates, aha_candidates  # The private map owns exact request bindings.
    output = output if isinstance(output, dict) else {}
    diagnostics = copy.deepcopy(discovery_plan.get("diagnostics", []))
    reviews = output.get("candidate_reviews")
    reviews = reviews if isinstance(reviews, list) else []
    if not isinstance(output.get("candidate_reviews"), list):
        diagnostics.append({"code": "AHA_CANDIDATE_REVIEWS_MISSING_OR_INVALID"})
    review_by_id = {}
    review_rows = []
    for index, row in enumerate(reviews):
        candidate_id = row.get("candidate_id") if isinstance(row, dict) else None
        if candidate_id not in maps["ahas"]:
            diagnostics.append({"code": "UNKNOWN_AHA_REVIEW_REFERENCE", "source_index": index})
            continue
        if candidate_id in review_by_id:
            diagnostics.append({"code": "DUPLICATE_AHA_REVIEW_REFERENCE", "source_index": index})
            continue
        if row.get("status") not in REVIEW_STATUSES or not grounded._text(row.get("reason")):
            diagnostics.append({"code": "AHA_REVIEW_INVALID", "source_index": index})
            continue
        normalized = {
            "candidate_id": maps["ahas"][candidate_id],
            "request_candidate_id": candidate_id,
            "status": row["status"],
            "reason": row["reason"].strip(),
        }
        review_by_id[candidate_id] = normalized
        review_rows.append(normalized)
    for candidate_id in maps["ahas"]:
        if candidate_id not in review_by_id:
            diagnostics.append({"code": "AHA_REVIEW_MISSING", "candidate_id": candidate_id})

    selected_raw = output.get("selected_aha_ids")
    selected_raw = selected_raw if isinstance(selected_raw, list) else []
    if not isinstance(output.get("selected_aha_ids"), list):
        diagnostics.append({"code": "AHA_SELECTION_LIST_MISSING_OR_INVALID"})
    selected_ids = []
    seen = set()
    for index, candidate_id in enumerate(selected_raw):
        if candidate_id in seen:
            diagnostics.append({"code": "DUPLICATE_AHA_SELECTION_REFERENCE", "source_index": index})
        elif candidate_id not in maps["ahas"]:
            diagnostics.append({"code": "UNKNOWN_AHA_SELECTION_REFERENCE", "source_index": index})
        elif candidate_id not in review_by_id:
            diagnostics.append({"code": "AHA_SELECTION_HAS_NO_VALID_REVIEW", "source_index": index})
        elif review_by_id[candidate_id]["status"] != "STANDALONE":
            diagnostics.append({"code": "AHA_SELECTION_NOT_STANDALONE", "source_index": index})
        elif len(selected_ids) >= MAX_AHAS:
            diagnostics.append({"code": "AHA_SELECTION_EXCEEDS_MAXIMUM", "source_index": index})
        else:
            selected_ids.append(candidate_id)
        seen.add(candidate_id)

    selections = [copy.deepcopy(maps["aha_selections"][value]) for value in selected_ids]
    aha_lane = {
        "status": "PARTIAL_SELECTION_BOUND" if diagnostics else "MODEL_SELECTION_BOUND",
        "recommended_candidate_ids": [maps["ahas"][value] for value in selected_ids],
        "selections": selections,
        "diagnostics": [item for item in diagnostics if str(item.get("code", "")).startswith("AHA_")],
    }
    chapter_aha, ca_diagnostics = _compile_chapter_aha(
        output, selected_ids, selected_chapters, context, maps,
    )
    aha_aha, aa_diagnostics = _compile_aha_aha(output, selected_ids, maps)
    diagnostics.extend(ca_diagnostics)
    diagnostics.extend(aa_diagnostics)
    if not grounded._text(output.get("set_reason")):
        diagnostics.append({"code": "AHA_SET_REASON_MISSING"})
    if diagnostics:
        aha_lane["status"] = "PARTIAL_SELECTION_BOUND"

    plan = {
        "policy_version": POLICY_VERSION,
        "guidance_scope": "TWO_STAGE_EDITORIAL_JUDGMENT_NOT_VISUAL_FACT_EVIDENCE",
        "recording_input_context": discovery_plan.get("recording_input_context"),
        CONTEXT_FIELD: copy.deepcopy(discovery_plan.get(CONTEXT_FIELD, {})),
        "reason": output.get("set_reason") if isinstance(output.get("set_reason"), str) else None,
        "aha_consideration_scope": copy.deepcopy(discovery_plan.get("aha_consideration_scope", [])),
        "chapters": copy.deepcopy(discovery_plan["chapters"]),
        "ahas": aha_lane,
        "aha_candidate_reviews": review_rows,
        "chapter_aha_relations": chapter_aha,
        "aha_aha_relations": aha_aha,
        "diagnostics": diagnostics,
        "additional_model_calls": 1,
        "semantic_quality": "ONE_PASS_TEXT_EDITOR_RELATIONS_BOUND_NOT_GROUND_TRUTH",
        "editor_input": copy.deepcopy(context),
    }
    return plan


def unavailable_plan(discovery_plan, error_code):
    diagnostics = [
        *copy.deepcopy(discovery_plan.get("diagnostics", [])),
        {"code": "AHA_SET_EDITOR_UNAVAILABLE", "detail": str(error_code)[:200]},
    ]
    return {
        "policy_version": POLICY_VERSION,
        "guidance_scope": "TWO_STAGE_EDITORIAL_JUDGMENT_NOT_VISUAL_FACT_EVIDENCE",
        "recording_input_context": discovery_plan.get("recording_input_context"),
        CONTEXT_FIELD: copy.deepcopy(discovery_plan.get(CONTEXT_FIELD, {})),
        "reason": None,
        "aha_consideration_scope": copy.deepcopy(discovery_plan.get("aha_consideration_scope", [])),
        "chapters": copy.deepcopy(discovery_plan["chapters"]),
        "ahas": {
            "status": "AHA_SET_EDITOR_UNAVAILABLE",
            "recommended_candidate_ids": [], "selections": [], "diagnostics": diagnostics[-1:],
        },
        "aha_candidate_reviews": [],
        "chapter_aha_relations": [], "aha_aha_relations": [],
        "diagnostics": diagnostics,
        "additional_model_calls": 1,
        "semantic_quality": "AHA_EDITOR_UNAVAILABLE_CHAPTERS_PRESERVED",
    }


def execute_plan(plan, chapters, chapter_ledger, ahas, aha_ledger, observations, asset_order,
                 *, minimum, max_chapters, max_ahas):
    return grounded.execute_plan(
        plan, chapters, chapter_ledger, ahas, aha_ledger, observations, asset_order,
        minimum=minimum, max_chapters=max_chapters, max_ahas=max_ahas,
        max_ahas_without_chapters=max_ahas,
    )


def allocation_plan(plan):
    return grounded.allocation_plan(plan)


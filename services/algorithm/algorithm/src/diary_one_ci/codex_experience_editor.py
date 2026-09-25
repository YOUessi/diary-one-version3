"""V1.75 full-fact Aha experience editor with Chapter-coverage audit.

S07 owns Chapters only. S09 receives every usable supported fact, records a
bounded finalist ledger, explicitly reviews every fact outside the selected
Chapters, selects a final coexistable set of atomic Ahas, and returns the
single authoritative pair-relation matrix. Deterministic code binds references
and executes the returned subset; it does not rank facts or fill rejected slots.
"""

import copy
import json
import uuid
from itertools import combinations

from . import codex_grounded_recording_editor as grounded


POLICY_VERSION = "CODEX_D5_FULL_FACT_AHA_EDITOR_V02"
POLICY_FIELD = grounded.POLICY_FIELD
OUTPUT_FIELD = grounded.OUTPUT_FIELD
CONTEXT_FIELD = grounded.CONTEXT_FIELD
WRITER_POLICY_FIELD = grounded.WRITER_POLICY_FIELD
EDITOR_STAGE = "S09_AHA_EXPERIENCE_EDITOR"
SEARCH_CONTRACT = "FULL_FACT_CHAPTER_COVERAGE_AUDIT_SINGLE_RELATION_AUTHORITY_V02"
REPRESENTATIVE_FRAME_FIELD = "representative_frame_id"
MAX_FINALISTS = 8
MAX_AHAS = 3
INTRINSIC_VALUES = ("WORTH_REVISITING", "WEAK", "UNRESOLVED")
RELATIONS = grounded.RELATIONS


def input_context():
    return grounded.input_context()


def structure_observations(observations, roles):
    return grounded.structure_observations(observations, roles)


def structure_moments(moments):
    return grounded.structure_moments(moments)


def perception_schema(base):
    """Require a visually selected representative frame for each fact."""
    result = copy.deepcopy(base)
    fact = result["properties"]["observations"]["items"]["properties"]["facts"]["items"]
    fact["properties"][REPRESENTATIVE_FRAME_FIELD] = {
        "type": "string",
        "minLength": 1,
        "description": (
            "One frame from evidence_frame_ids that most clearly represents this fact. "
            "This is evidence provenance, not an Aha decision."
        ),
    }
    if REPRESENTATIVE_FRAME_FIELD not in fact["required"]:
        fact["required"].append(REPRESENTATIVE_FRAME_FIELD)
    return result


def perception_instruction():
    return (
        "V1.74 representative-frame contract: for every fact, return exactly one "
        "representative_frame_id from that fact's evidence_frame_ids. Choose the frame that most "
        "clearly and completely shows the stated fact. This does not decide whether the fact is an "
        "Aha and must not change the fact text. "
    )


def consideration_scope(observations, roles):
    """All usable facts with grounded support and valid visual provenance."""
    keep = {item["observation_id"] for item in roles if item["role"] == "KEEP"}
    scope = []
    for observation in observations:
        fact_ids = []
        for fact in observation.get("facts", []):
            frame = fact.get(REPRESENTATIVE_FRAME_FIELD)
            if (
                observation.get("id") in keep
                and fact.get("support_grade") in ("STRONG", "MODERATE")
                and isinstance(fact.get("fact_id"), str)
                and fact["fact_id"]
                and isinstance(frame, str)
                and frame in fact.get("evidence_frame_ids", [])
            ):
                fact_ids.append(fact["fact_id"])
        if fact_ids:
            scope.append({
                "observation_id": observation["id"],
                "event_fact_ids": fact_ids,
            })
    return scope


def response_schema(base):
    """Make S07 Chapter-only while retaining the shared wire shape."""
    result = grounded.response_schema(base)
    result["properties"]["aha_proposals"]["maxItems"] = 0
    result["properties"][OUTPUT_FIELD] = {
        "type": "object",
        "additionalProperties": False,
        "required": ["chapter_keys", "reason"],
        "properties": {
            "chapter_keys": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 4,
                "uniqueItems": True,
            },
            "reason": {"type": "string"},
        },
    }
    return result


def prompt_instruction():
    return (
        "V1.74 makes this S07 call Chapter-only. Return an empty aha_proposals array and empty "
        "legacy storyline_proposals[*].aha_relations arrays. Do not nominate, rank, focus, or "
        "relate Ahas here. A separate one-pass S09 editor will receive every usable supported fact "
        "after the technically executable Chapters are known. "
    )


def compile_discovery(output, chapter_ledger, scope):
    output = output if isinstance(output, dict) else {}
    selected = output.get(OUTPUT_FIELD)
    selected = selected if isinstance(selected, dict) else {}
    diagnostics = []
    proposals = output.get("aha_proposals")
    if not isinstance(proposals, list):
        diagnostics.append({"code": "S07_AHA_PROPOSALS_MISSING_OR_INVALID"})
    elif proposals:
        diagnostics.append({"code": "S07_CHAPTER_ONLY_AHA_PROPOSALS_NOT_EMPTY"})
    chapter_bindings = grounded._chapter_bindings(
        output, chapter_ledger, output.get("storyline_proposals")
    )
    chapters = grounded._bind_chapters(selected.get("chapter_keys"), chapter_bindings)
    context = output.get(CONTEXT_FIELD)
    context = context if isinstance(context, dict) else {}
    for field in ("summary", "uncertainty"):
        if not grounded._text(context.get(field)):
            diagnostics.append({"code": "RECORDING_CONTEXT_FIELD_MISSING", "field": field})
    if not grounded._text(selected.get("reason")):
        diagnostics.append({"code": "CHAPTER_SELECTION_REASON_MISSING"})
    diagnostics.extend(chapters["diagnostics"])
    return {
        "policy_version": POLICY_VERSION,
        "guidance_scope": "CHAPTER_ONLY_S07_FULL_FACT_S09_NOT_VISUAL_FACT_EVIDENCE",
        "recording_input_context": input_context(),
        CONTEXT_FIELD: copy.deepcopy(context),
        "reason": selected.get("reason") if isinstance(selected.get("reason"), str) else None,
        "aha_consideration_scope": copy.deepcopy(scope),
        "chapters": chapters,
        "diagnostics": diagnostics,
        "additional_model_calls": 1,
        "semantic_quality": "CHAPTER_SELECTION_BOUND_AHA_NOT_YET_EDITED",
    }


def preview_selected_chapters(plan, chapter_candidates, asset_order, *, minimum, max_chapters):
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


def build_fact_candidates(namespace, observations, roles, moments, asset_order):
    """Build one technical candidate per eligible fact; make no value judgment."""
    role_by_id = {item["observation_id"]: item["role"] for item in roles}
    moment_by_observation = {
        observation_id: moment["id"]
        for moment in moments
        for observation_id in moment["observation_ids"]
    }
    ordered = sorted(observations, key=lambda item: asset_order[item["source_asset_id"]])
    candidates = []
    ledger = []
    for observation in ordered:
        for fact in observation.get("facts", []):
            frame = fact.get(REPRESENTATIVE_FRAME_FIELD)
            entry = {
                "observation_id": observation["id"],
                "source_asset_id": observation["source_asset_id"],
                "fact_id": fact.get("fact_id"),
                "validation_status": "REJECTED",
                "selection_status": "NOT_ELIGIBLE",
                "reason_codes": [],
            }
            if role_by_id.get(observation["id"]) != "KEEP":
                entry["reason_codes"].append("NON_KEEP_MEMBER")
            elif fact.get("support_grade") not in ("STRONG", "MODERATE"):
                entry["reason_codes"].append("FACT_SUPPORT_TOO_WEAK")
            elif not isinstance(frame, str) or frame not in fact.get("evidence_frame_ids", []):
                entry["reason_codes"].append("FACT_REPRESENTATIVE_FRAME_INVALID")
            else:
                candidate_id = str(uuid.uuid5(
                    namespace,
                    "aha-fact-candidate:%s:%s" % (
                        observation["source_asset_id"], fact["fact_id"],
                    ),
                ))
                candidate = {
                    "candidate_id": candidate_id,
                    "candidate_type": "AHA",
                    "observation_id": observation["id"],
                    "moment_id": moment_by_observation[observation["id"]],
                    "source_asset_id": observation["source_asset_id"],
                    "fact_ids": [fact["fact_id"]],
                    "event_fact_ids": [fact["fact_id"]],
                    "representative_frame_id": frame,
                    "event_kind": observation.get("event_kind", "NONE"),
                    "event_salience": observation.get("event_salience", "NONE"),
                    "episode_code": observation.get("episode_code", "UNKNOWN"),
                    "narrative_duty": "",
                    "proposal_source": "FULL_SUPPORTED_FACT_PALETTE",
                    "subject_codes": list(observation.get("subject_codes", [])),
                    "motifs": list(observation.get("motifs", [])),
                    "quality_score": float(observation.get("quality_score", 0.0)),
                    "fact_support_grades": [fact["support_grade"]],
                }
                candidates.append(candidate)
                entry.update({
                    "candidate_id": candidate_id,
                    "validation_status": "PASSED",
                    "selection_status": "ELIGIBLE",
                    "reason_codes": ["SUPPORTED_FACT_WITH_VISUAL_REPRESENTATIVE"],
                })
            ledger.append(entry)
    return candidates, ledger


def _fact_lookup(observations):
    facts = {}
    observation_by_fact = {}
    limitations = {}
    for observation in observations:
        cautions = [
            value for value in observation.get("limitations", [])
            if grounded._text(value)
        ]
        for fact in observation.get("facts", []):
            fact_id = fact.get("fact_id")
            if grounded._text(fact_id):
                facts[fact_id] = fact
                observation_by_fact[fact_id] = observation["id"]
                limitations[fact_id] = cautions
    return facts, observation_by_fact, limitations


def editor_input(discovery_plan, selected_chapters, chapter_candidates, aha_candidates,
                 observations):
    """Return the full usable fact palette plus selected-Chapter membership."""
    facts, observation_by_fact, limitations = _fact_lookup(observations)
    chapter_by_id = {item["candidate_id"]: item for item in chapter_candidates}
    candidate_by_fact = {
        item["fact_ids"][0]: item["candidate_id"]
        for item in aha_candidates if len(item.get("fact_ids", [])) == 1
    }
    observation_to_short = {
        observation["id"]: "O%03d" % index
        for index, observation in enumerate(observations, 1)
    }
    fact_to_short = {
        fact["fact_id"]: "F%03d" % index
        for index, fact in enumerate(
            [fact for observation in observations for fact in observation.get("facts", [])], 1
        )
    }

    selected_keys = discovery_plan["chapters"].get("selected_keys", [])
    key_by_id = dict(zip(
        discovery_plan["chapters"].get("recommended_candidate_ids", []), selected_keys,
    ))
    chapter_map = {}
    chapter_fact_map = {}
    chapter_membership_by_fact = {}
    chapter_rows = []
    for index, selected in enumerate(selected_chapters, 1):
        short_id = "C%02d" % index
        candidate_id = selected["candidate_id"]
        candidate = chapter_by_id[candidate_id]
        chapter_map[short_id] = candidate_id
        fact_rows = []
        chapter_fact_map[short_id] = []
        for fact_id in candidate.get("fact_ids", []):
            fact = facts.get(fact_id)
            fact_short = fact_to_short.get(fact_id)
            if fact is None or fact_short is None:
                continue
            chapter_fact_map[short_id].append(fact_short)
            chapter_membership_by_fact.setdefault(fact_short, []).append(short_id)
            fact_rows.append({
                "fact_id": fact_short,
                "text": fact.get("text", ""),
                "support_grade": fact.get("support_grade", "UNKNOWN"),
            })
        chapter_rows.append({
            "chapter_id": short_id,
            "thesis": candidate.get("storyline_identity", {}).get("thesis", ""),
            "facts": fact_rows,
        })

    eligible_fact_ids = [
        fact_id
        for scope in discovery_plan.get("aha_consideration_scope", [])
        for fact_id in scope.get("event_fact_ids", [])
        if fact_id in candidate_by_fact
    ]
    palette = []
    for fact_id in eligible_fact_ids:
        fact = facts[fact_id]
        row = {
            "fact_id": fact_to_short[fact_id],
            "observation_id": observation_to_short[observation_by_fact[fact_id]],
            "text": fact.get("text", ""),
            "support_grade": fact.get("support_grade", "UNKNOWN"),
            "chapter_membership": list(chapter_membership_by_fact.get(
                fact_to_short[fact_id], [],
            )),
            "coverage_status": (
                "INSIDE_SELECTED_CHAPTER"
                if chapter_membership_by_fact.get(fact_to_short[fact_id])
                else "OUTSIDE_SELECTED_CHAPTERS"
            ),
        }
        if limitations.get(fact_id):
            row["evidence_cautions"] = limitations[fact_id]
        palette.append(row)

    uncovered_fact_ids = [
        row["fact_id"] for row in palette
        if row["coverage_status"] == "OUTSIDE_SELECTED_CHAPTERS"
    ]

    context = {
        "policy_version": POLICY_VERSION,
        "recording_context": copy.deepcopy(discovery_plan.get(CONTEXT_FIELD, {})),
        "quantity_contract": {
            "allowed_aha_count": {"minimum": 0, "maximum": MAX_AHAS},
            "active_quality_target_when_supported": "2_TO_3",
            "one_is_valid": True,
            "zero_requires_no_grounded_distinct_choice": True,
            "quota_or_automatic_fill": False,
        },
        "chapters": chapter_rows,
        "fact_palette": palette,
        "coverage_audit": {
            "uncovered_fact_ids": uncovered_fact_ids,
            "required_review": "EXACTLY_ONCE_EACH_IN_PALETTE_ORDER",
            "membership_is_value_score": False,
            "selection_is_required": False,
        },
    }
    maps = {
        "chapters": chapter_map,
        "chapter_keys": {short: key_by_id.get(long) for short, long in chapter_map.items()},
        "chapter_facts": chapter_fact_map,
        "facts": {short: long for long, short in fact_to_short.items()},
        "fact_short_by_long": fact_to_short,
        "candidate_by_fact": candidate_by_fact,
        "observations": {short: long for long, short in observation_to_short.items()},
        "observation_by_fact": observation_by_fact,
        "representative_frames": {
            fact_to_short[fact_id]: facts[fact_id][REPRESENTATIVE_FRAME_FIELD]
            for fact_id in eligible_fact_ids
        },
        "eligible_fact_ids": [fact_to_short[value] for value in eligible_fact_ids],
        "uncovered_fact_ids": uncovered_fact_ids,
    }
    return context, maps


def editor_response_schema():
    relation = {"type": "string", "enum": list(RELATIONS)}
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "uncovered_fact_reviews", "finalists", "selected_ahas", "chapter_aha_relations",
            "aha_aha_relations", "set_reason",
        ],
        "properties": {
            "uncovered_fact_reviews": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["fact_id", "intrinsic_value", "revisit_hook", "reason"],
                    "properties": {
                        "fact_id": {"type": "string"},
                        "intrinsic_value": {
                            "type": "string", "enum": list(INTRINSIC_VALUES),
                        },
                        "revisit_hook": {"type": "string", "minLength": 1, "maxLength": 120},
                        "reason": {"type": "string"},
                    },
                },
            },
            "finalists": {
                "type": "array",
                "maxItems": MAX_FINALISTS,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["fact_id", "intrinsic_value", "revisit_hook", "reason"],
                    "properties": {
                        "fact_id": {"type": "string"},
                        "intrinsic_value": {
                            "type": "string", "enum": list(INTRINSIC_VALUES),
                        },
                        "revisit_hook": {"type": "string", "minLength": 1, "maxLength": 120},
                        "reason": {"type": "string"},
                    },
                },
            },
            "selected_ahas": {
                "type": "array",
                "maxItems": MAX_AHAS,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["fact_id", "moment_focus", "selection_reason"],
                    "properties": {
                        "fact_id": {"type": "string"},
                        "moment_focus": {"type": "string", "minLength": 1, "maxLength": 80},
                        "selection_reason": {"type": "string"},
                    },
                },
            },
            "chapter_aha_relations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "chapter_id", "aha_fact_id", "relation",
                        "chapter_fact_ids", "reason",
                    ],
                    "properties": {
                        "chapter_id": {"type": "string"},
                        "aha_fact_id": {"type": "string"},
                        "relation": relation,
                        "chapter_fact_ids": {
                            "type": "array", "items": {"type": "string"},
                            "minItems": 1, "uniqueItems": True,
                        },
                        "reason": {"type": "string"},
                    },
                },
            },
            "aha_aha_relations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["aha_fact_ids", "relation", "reason"],
                    "properties": {
                        "aha_fact_ids": {
                            "type": "array", "items": {"type": "string"},
                            "minItems": 2, "maxItems": 2, "uniqueItems": True,
                        },
                        "relation": relation,
                        "reason": {"type": "string"},
                    },
                },
            },
            "set_reason": {"type": "string"},
        },
    }


def editor_prompt(context):
    return (
        "You are the one-pass S09 Aha Experience Editor. Read the entire supplied fact_palette; "
        "it is not an upstream shortlist. Chapter membership is structural context, never a value "
        "score: facts inside a Chapter may still be Ahas when they carry a genuinely additional "
        "recall story, while facts outside Chapters are not automatically valuable. First return "
        "uncovered_fact_reviews with exactly one review for every coverage_audit.uncovered_fact_ids "
        "entry, in the same order. Do not omit any uncovered fact and do not review covered facts in "
        "that array. For every review, revisit_hook must name the concrete action, interaction, change, "
        "state, composition, or discovery supported by the complete fact; a strong anchor, name, "
        "object, crop, wording, or place label alone is not a revisit hook. Then list at most eight "
        "strongest finalists from the full palette for an auditable comparison. intrinsic_value judges "
        "only whether the fact contains a concrete moment worth revisiting by itself; it does not judge "
        "Chapter overlap. Select zero to three Ahas only from WORTH_REVISITING finalists. selected_ahas "
        "is the FINAL set that must already be able to coexist with every selected Chapter and with "
        "each other; it is not a provisional list for deterministic cleanup. When grounded facts "
        "support them, actively seek two or three; one remains valid and no quota may force weak "
        "content. For each selection, compress the existing fact into one atomic moment_focus without "
        "adding facts. Static discoveries are allowed only when the supplied fact supports a concrete "
        "revisit experience, not mere classification. Return exactly chapters multiplied by selected "
        "Ahas Chapter/Aha relation rows, and exactly n*(n-1)/2 unordered Aha/Aha rows for n selected "
        "Ahas. Relations are the only authority on cross-card story overlap: a selected item with any "
        "SAME_STORY or UNRESOLVED relation must be removed before output; consider another independent "
        "WORTH_REVISITING finalist when supported, but never fill a quota. An Aha inside a Chapter is "
        "allowed only if its recall story is genuinely additional to that Chapter's main story. Do not "
        "invent facts, use metadata as value proof, request images, or ask for another call. Reasons are "
        "concise editorial decisions, not hidden reasoning or new evidence. Return only the schema "
        "object. Input:\n"
        + json.dumps(context, ensure_ascii=False)
    )


def _unresolved(code, **fields):
    return {
        **fields,
        "relation": "UNRESOLVED",
        "reason": "",
        "reason_codes": [code],
    }


def _compile_chapter_aha(output, selected_facts, selected_chapters, maps):
    rows = output.get("chapter_aha_relations")
    rows = rows if isinstance(rows, list) else []
    diagnostics = [] if isinstance(output.get("chapter_aha_relations"), list) else [
        {"code": "CHAPTER_AHA_RELATIONS_MISSING_OR_INVALID"}
    ]
    chapter_set = {
        short for short, long in maps["chapters"].items()
        if any(item["candidate_id"] == long for item in selected_chapters)
    }
    selected_set = set(selected_facts)
    bound = {}
    for index, row in enumerate(rows):
        chapter_id = row.get("chapter_id") if isinstance(row, dict) else None
        fact_id = row.get("aha_fact_id") if isinstance(row, dict) else None
        if chapter_id not in chapter_set or fact_id not in selected_set:
            diagnostics.append({"code": "CHAPTER_AHA_ROW_NOT_IN_SELECTED_SET", "source_index": index})
            continue
        bound.setdefault((chapter_id, fact_id), []).append(row)

    compiled = []
    for chapter_id in sorted(chapter_set):
        for fact_short in selected_facts:
            fact_long = maps["facts"][fact_short]
            candidate_id = maps["candidate_by_fact"][fact_long]
            base = {
                "chapter_candidate_id": maps["chapters"][chapter_id],
                "aha_candidate_id": candidate_id,
                "aha_observation_id": maps["observation_by_fact"][fact_long],
                "chapter_fact_ids": [],
                "aha_fact_ids": [fact_long],
            }
            matches = bound.get((chapter_id, fact_short), [])
            if len(matches) != 1:
                code = (
                    "CHAPTER_AHA_RELATION_MISSING"
                    if not matches else "DUPLICATE_CHAPTER_AHA_RELATION_ROWS"
                )
                compiled.append(_unresolved(code, **base))
                continue
            row = matches[0]
            chapter_facts = row.get("chapter_fact_ids")
            errors = []
            if row.get("relation") not in RELATIONS:
                errors.append("RELATION_VALUE_INVALID")
            if (
                not isinstance(chapter_facts, list)
                or not chapter_facts
                or len(set(chapter_facts)) != len(chapter_facts)
                or not set(chapter_facts) <= set(maps["chapter_facts"].get(chapter_id, []))
            ):
                errors.append("CHAPTER_FACT_REFERENCE_INVALID")
            if not grounded._text(row.get("reason")):
                errors.append("RELATION_REASON_MISSING")
            if errors:
                item = _unresolved(errors[0], **base)
                item["reason_codes"] = errors
            else:
                item = {
                    **base,
                    "chapter_fact_ids": [maps["facts"][value] for value in chapter_facts],
                    "relation": row["relation"],
                    "reason": row["reason"].strip(),
                    "reason_codes": [
                        "EXPLICIT_SELECTED_SET_RELATION"
                        if row["relation"] != "UNRESOLVED" else "MODEL_RELATION_UNRESOLVED"
                    ],
                }
            compiled.append(item)
    return compiled, diagnostics


def _compile_aha_aha(output, selected_facts, maps):
    rows = output.get("aha_aha_relations")
    rows = rows if isinstance(rows, list) else []
    diagnostics = [] if isinstance(output.get("aha_aha_relations"), list) else [
        {"code": "AHA_AHA_RELATIONS_MISSING_OR_INVALID"}
    ]
    selected_set = set(selected_facts)
    bound = {}
    for index, row in enumerate(rows):
        fact_ids = row.get("aha_fact_ids") if isinstance(row, dict) else None
        if (
            not isinstance(fact_ids, list)
            or len(fact_ids) != 2
            or len(set(fact_ids)) != 2
            or not set(fact_ids) <= selected_set
        ):
            diagnostics.append({"code": "AHA_AHA_ROW_NOT_IN_SELECTED_SET", "source_index": index})
            continue
        bound.setdefault(frozenset(fact_ids), []).append(row)

    compiled = []
    for left, right in combinations(selected_facts, 2):
        left_long = maps["facts"][left]
        right_long = maps["facts"][right]
        base = {
            "left_aha_candidate_id": maps["candidate_by_fact"][left_long],
            "right_aha_candidate_id": maps["candidate_by_fact"][right_long],
            "left_observation_id": maps["observation_by_fact"][left_long],
            "right_observation_id": maps["observation_by_fact"][right_long],
            "left_fact_id": left_long,
            "right_fact_id": right_long,
        }
        matches = bound.get(frozenset((left, right)), [])
        if len(matches) != 1:
            code = "AHA_AHA_RELATION_MISSING" if not matches else "DUPLICATE_AHA_AHA_RELATION_ROWS"
            compiled.append(_unresolved(code, **base))
            continue
        row = matches[0]
        errors = []
        if row.get("relation") not in RELATIONS:
            errors.append("RELATION_VALUE_INVALID")
        if not grounded._text(row.get("reason")):
            errors.append("RELATION_REASON_MISSING")
        if errors:
            item = _unresolved(errors[0], **base)
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


def compile_editor(output, context, maps, discovery_plan, selected_chapters):
    """Bind the one-pass full-fact selection without semantic auto-repair."""
    output = output if isinstance(output, dict) else {}
    diagnostics = copy.deepcopy(discovery_plan.get("diagnostics", []))
    eligible = set(maps["eligible_fact_ids"])
    uncovered = list(maps.get("uncovered_fact_ids", []))
    uncovered_set = set(uncovered)

    reviews_raw = output.get("uncovered_fact_reviews")
    reviews_raw = reviews_raw if isinstance(reviews_raw, list) else []
    if not isinstance(output.get("uncovered_fact_reviews"), list):
        diagnostics.append({"code": "UNCOVERED_FACT_REVIEWS_MISSING_OR_INVALID"})
    review_by_fact = {}
    review_rows = []
    for index, row in enumerate(reviews_raw):
        fact_id = row.get("fact_id") if isinstance(row, dict) else None
        if fact_id not in uncovered_set:
            diagnostics.append({
                "code": "UNCOVERED_FACT_REVIEW_OUTSIDE_REQUIRED_SET", "source_index": index,
            })
            continue
        if fact_id in review_by_fact:
            diagnostics.append({
                "code": "DUPLICATE_UNCOVERED_FACT_REVIEW", "source_index": index,
            })
            continue
        if (
            row.get("intrinsic_value") not in INTRINSIC_VALUES
            or not grounded._text(row.get("revisit_hook"))
            or not grounded._text(row.get("reason"))
        ):
            diagnostics.append({
                "code": "UNCOVERED_FACT_REVIEW_INVALID", "source_index": index,
            })
            continue
        normalized = {
            "fact_id": maps["facts"][fact_id],
            "request_fact_id": fact_id,
            "intrinsic_value": row["intrinsic_value"],
            "revisit_hook": row["revisit_hook"].strip(),
            "reason": row["reason"].strip(),
        }
        review_by_fact[fact_id] = normalized
        review_rows.append(normalized)
    for fact_id in uncovered:
        if fact_id not in review_by_fact:
            diagnostics.append({
                "code": "UNCOVERED_FACT_REVIEW_MISSING", "fact_id": maps["facts"][fact_id],
            })

    finalists_raw = output.get("finalists")
    finalists_raw = finalists_raw if isinstance(finalists_raw, list) else []
    if not isinstance(output.get("finalists"), list):
        diagnostics.append({"code": "AHA_FINALISTS_MISSING_OR_INVALID"})
    finalist_by_fact = {}
    finalist_rows = []
    for index, row in enumerate(finalists_raw[:MAX_FINALISTS]):
        fact_id = row.get("fact_id") if isinstance(row, dict) else None
        if fact_id not in eligible:
            diagnostics.append({"code": "UNKNOWN_AHA_FINALIST_FACT", "source_index": index})
            continue
        if fact_id in finalist_by_fact:
            diagnostics.append({"code": "DUPLICATE_AHA_FINALIST_FACT", "source_index": index})
            continue
        if (
            row.get("intrinsic_value") not in INTRINSIC_VALUES
            or not grounded._text(row.get("revisit_hook"))
            or not grounded._text(row.get("reason"))
        ):
            diagnostics.append({"code": "AHA_FINALIST_REVIEW_INVALID", "source_index": index})
            continue
        normalized = {
            "fact_id": maps["facts"][fact_id],
            "request_fact_id": fact_id,
            "intrinsic_value": row["intrinsic_value"],
            "revisit_hook": row["revisit_hook"].strip(),
            "reason": row["reason"].strip(),
        }
        finalist_by_fact[fact_id] = normalized
        finalist_rows.append(normalized)
    if len(finalists_raw) > MAX_FINALISTS:
        diagnostics.append({"code": "AHA_FINALISTS_EXCEED_MAXIMUM"})

    selected_raw = output.get("selected_ahas")
    selected_raw = selected_raw if isinstance(selected_raw, list) else []
    if not isinstance(output.get("selected_ahas"), list):
        diagnostics.append({"code": "AHA_SELECTION_LIST_MISSING_OR_INVALID"})
    selected_facts = []
    selections = []
    seen_facts = set()
    seen_observations = set()
    for index, row in enumerate(selected_raw):
        fact_short = row.get("fact_id") if isinstance(row, dict) else None
        fact_long = maps["facts"].get(fact_short)
        observation_id = maps["observation_by_fact"].get(fact_long)
        reason = None
        if fact_short in seen_facts:
            reason = "DUPLICATE_AHA_SELECTION_FACT"
        elif fact_short not in eligible:
            reason = "UNKNOWN_AHA_SELECTION_FACT"
        elif fact_short not in finalist_by_fact:
            reason = "AHA_SELECTION_NOT_IN_FINALISTS"
        elif finalist_by_fact[fact_short]["intrinsic_value"] != "WORTH_REVISITING":
            reason = "AHA_SELECTION_NOT_WORTH_REVISITING"
        elif (
            fact_short in uncovered_set
            and (
                fact_short not in review_by_fact
                or review_by_fact[fact_short]["intrinsic_value"] != "WORTH_REVISITING"
            )
        ):
            reason = "AHA_SELECTION_UNCOVERED_REVIEW_NOT_WORTH_REVISITING"
        elif observation_id in seen_observations:
            reason = "MULTIPLE_AHAS_FROM_ONE_OBSERVATION_NOT_SUPPORTED"
        elif not grounded._text(row.get("moment_focus")):
            reason = "AHA_SELECTION_FOCUS_MISSING"
        elif not grounded._text(row.get("selection_reason")):
            reason = "AHA_SELECTION_REASON_MISSING"
        elif len(selected_facts) >= MAX_AHAS:
            reason = "AHA_SELECTION_EXCEEDS_MAXIMUM"
        if fact_short in eligible:
            seen_facts.add(fact_short)
        if observation_id is not None:
            seen_observations.add(observation_id)
        if reason:
            diagnostics.append({"code": reason, "source_index": index})
            continue
        selected_facts.append(fact_short)
        selections.append({
            "candidate_id": maps["candidate_by_fact"][fact_long],
            "observation_id": observation_id,
            "fact_id": fact_long,
            "focus_frame_id": maps["representative_frames"][fact_short],
            "revisit_hook": finalist_by_fact[fact_short]["revisit_hook"],
            "moment_focus": row["moment_focus"].strip(),
            "selection_reason": row["selection_reason"].strip(),
        })

    chapter_aha, ca_diagnostics = _compile_chapter_aha(
        output, selected_facts, selected_chapters, maps,
    )
    aha_aha, aa_diagnostics = _compile_aha_aha(output, selected_facts, maps)
    diagnostics.extend(ca_diagnostics)
    diagnostics.extend(aa_diagnostics)
    if not grounded._text(output.get("set_reason")):
        diagnostics.append({"code": "AHA_SET_REASON_MISSING"})

    lane_status = "MODEL_SELECTION_BOUND" if not diagnostics else "PARTIAL_SELECTION_BOUND"
    plan = {
        "policy_version": POLICY_VERSION,
        "guidance_scope": "FULL_FACT_EDITORIAL_JUDGMENT_NOT_VISUAL_FACT_EVIDENCE",
        "recording_input_context": discovery_plan.get("recording_input_context"),
        CONTEXT_FIELD: copy.deepcopy(discovery_plan.get(CONTEXT_FIELD, {})),
        "reason": output.get("set_reason") if isinstance(output.get("set_reason"), str) else None,
        "aha_consideration_scope": copy.deepcopy(discovery_plan.get("aha_consideration_scope", [])),
        "chapters": copy.deepcopy(discovery_plan["chapters"]),
        "ahas": {
            "status": lane_status,
            "recommended_candidate_ids": [item["candidate_id"] for item in selections],
            "selections": selections,
            "diagnostics": [
                item for item in diagnostics
                if str(item.get("code", "")).startswith("AHA_")
                or str(item.get("code", "")).startswith("MULTIPLE_AHAS")
            ],
        },
        "uncovered_fact_reviews": review_rows,
        "aha_finalists": finalist_rows,
        "chapter_aha_relations": chapter_aha,
        "aha_aha_relations": aha_aha,
        "diagnostics": diagnostics,
        "additional_model_calls": 1,
        "semantic_quality": "ONE_PASS_FULL_FACT_EDITOR_RELATIONS_BOUND_NOT_GROUND_TRUTH",
        "editor_input": copy.deepcopy(context),
    }
    return plan


def unavailable_plan(discovery_plan, error_code):
    diagnostics = [
        *copy.deepcopy(discovery_plan.get("diagnostics", [])),
        {"code": "AHA_EXPERIENCE_EDITOR_UNAVAILABLE", "detail": str(error_code)[:200]},
    ]
    return {
        "policy_version": POLICY_VERSION,
        "guidance_scope": "FULL_FACT_EDITORIAL_JUDGMENT_NOT_VISUAL_FACT_EVIDENCE",
        "recording_input_context": discovery_plan.get("recording_input_context"),
        CONTEXT_FIELD: copy.deepcopy(discovery_plan.get(CONTEXT_FIELD, {})),
        "reason": None,
        "aha_consideration_scope": copy.deepcopy(discovery_plan.get("aha_consideration_scope", [])),
        "chapters": copy.deepcopy(discovery_plan["chapters"]),
        "ahas": {
            "status": "AHA_EXPERIENCE_EDITOR_UNAVAILABLE",
            "recommended_candidate_ids": [],
            "selections": [],
            "diagnostics": diagnostics[-1:],
        },
        "aha_finalists": [],
        "chapter_aha_relations": [],
        "aha_aha_relations": [],
        "diagnostics": diagnostics,
        "additional_model_calls": 1,
        "semantic_quality": "AHA_EDITOR_UNAVAILABLE_CHAPTERS_PRESERVED",
    }


def execute_plan(plan, chapters, chapter_ledger, ahas, aha_ledger, observations, asset_order,
                 *, minimum, max_chapters, max_ahas):
    result = grounded.execute_plan(
        plan, chapters, chapter_ledger, ahas, aha_ledger, observations, asset_order,
        minimum=minimum, max_chapters=max_chapters, max_ahas=max_ahas,
        max_ahas_without_chapters=max_ahas,
    )
    result[3]["algorithm"] = "FULL_FACT_MODEL_SELECTION_WITH_SINGLE_RELATION_AUTHORITY"
    result[3]["search_contract"] = SEARCH_CONTRACT
    result[3]["event_category_gating_applied"] = False
    result[3]["motif_overlap_gating_applied"] = False
    return result


def allocation_plan(plan):
    return grounded.allocation_plan(plan)

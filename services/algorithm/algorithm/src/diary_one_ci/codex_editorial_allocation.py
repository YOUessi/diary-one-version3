"""Bind existing editorial relations; never infer stories or create evidence.

This module has no model calls, scene vocabulary, scoring or candidate gates.
An unresolved relation neither suppresses a candidate nor proves independence.
"""

import copy


POLICY_VERSION = "DIARY_ONE_X02_EDITORIAL_ALLOCATION_V01"
POLICY_FIELD = "editorial_allocation_policy_version"
GUIDANCE_SCOPE = "EDITORIAL_HINTS_NOT_FACT_EVIDENCE"
RELATIONS_FIELD = "chapter_aha_relations"
RELATIONS = ("SAME_STORY", "DISTINCT_STORY", "UNRESOLVED")


def structure_schema(base):
    """Extend a copy of the current response, without changing its old fields."""
    result = copy.deepcopy(base)
    result.setdefault("properties", {})[RELATIONS_FIELD] = {
        "type": "array",
        "description": (
            "Editorial relations between proposed Chapters and existing eligible Aha facts. "
            "These are organizational hints, not new fact evidence. Missing relations remain unresolved."
        ),
        "items": {
            "type": "object",
            "additionalProperties": False,
            "required": ["chapter_key", "aha_observation_id", "relation",
                         "chapter_fact_ids", "aha_fact_ids", "reason"],
            "properties": {
                "chapter_key": {"type": "string"},
                "aha_observation_id": {"type": "string"},
                "relation": {"type": "string", "enum": list(RELATIONS)},
                "chapter_fact_ids": {"type": "array", "items": {"type": "string"},
                                     "minItems": 1, "uniqueItems": True},
                "aha_fact_ids": {"type": "array", "items": {"type": "string"},
                                 "minItems": 1, "uniqueItems": True},
                "reason": {"type": "string"},
            },
        },
    }
    required = result.setdefault("required", [])
    if RELATIONS_FIELD not in required:
        required.append(RELATIONS_FIELD)
    return result


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _fact_ids(value):
    if (not isinstance(value, list) or not value
            or any(not _text(item) for item in value)
            or len(set(value)) != len(value)):
        return None
    return list(value)


def _candidate_facts(candidate):
    return set(item for item in candidate.get("fact_ids", []) if _text(item))


def _empty_plan():
    return {"policy_version": POLICY_VERSION, "guidance_scope": GUIDANCE_SCOPE,
            "relations": [], "diagnostics": []}


def _unresolved(chapter_id, aha_id, code, observation_id=""):
    return {
        "chapter_candidate_id": chapter_id,
        "aha_candidate_id": aha_id,
        "aha_observation_id": observation_id,
        "relation": "UNRESOLVED",
        "chapter_fact_ids": [],
        "aha_fact_ids": [],
        "reason": "",
        "reason_codes": [code],
    }


def compile_relations(output, chapters, chapter_ledger, ahas):
    """Bind model annotations to actual candidates, preserving all candidate pairs.

    Proposal keys bind through the passed ledger only. Ambiguous keys, duplicate
    pair rows and invalid references produce unresolved annotations, never a
    guessed binding or candidate deletion. Input objects are not mutated.
    """
    plan = _empty_plan()
    chapter_by_id = {item["candidate_id"]: item for item in chapters}
    aha_by_id = {item["candidate_id"]: item for item in ahas}
    ledger_by_key = {}
    for entry in chapter_ledger:
        key = entry.get("candidate_key")
        if _text(key):
            ledger_by_key.setdefault(key, []).append(entry)
    key_bindings = {}
    for key, entries in ledger_by_key.items():
        # Even a passed/rejected key collision cannot be disambiguated from the
        # model's key alone; do not redirect the rejected row to another Chapter.
        if len(entries) != 1:
            plan["diagnostics"].append({"code": "AMBIGUOUS_CHAPTER_KEY", "chapter_key": key})
            continue
        entry = entries[0]
        if (entry.get("validation_status") == "PASSED"
                and entry.get("candidate_id") in chapter_by_id):
            key_bindings[key] = entry["candidate_id"]
    ahas_by_observation = {}
    for candidate in ahas:
        observation_id = candidate.get("observation_id")
        if _text(observation_id):
            ahas_by_observation.setdefault(observation_id, []).append(candidate["candidate_id"])

    supplied = output.get(RELATIONS_FIELD) if isinstance(output, dict) else None
    if not isinstance(supplied, list):
        plan["diagnostics"].append({"code": "RELATION_ARRAY_MISSING_OR_INVALID"})
        supplied = []
    rows_by_pair = {}
    for index, row in enumerate(supplied):
        if not isinstance(row, dict):
            plan["diagnostics"].append({"code": "RELATION_ROW_INVALID", "source_index": index})
            continue
        key = row.get("chapter_key")
        observation_id = row.get("aha_observation_id")
        chapter_id = key_bindings.get(key) if isinstance(key, str) else None
        aha_ids = ahas_by_observation.get(observation_id, []) if isinstance(observation_id, str) else []
        if chapter_id is None or len(aha_ids) != 1:
            plan["diagnostics"].append({
                "code": ("CHAPTER_KEY_NOT_UNIQUELY_PASSED" if chapter_id is None
                         else "AHA_OBSERVATION_NOT_UNIQUELY_BOUND"),
                "source_index": index,
                "chapter_key": key if isinstance(key, str) else None,
                "aha_observation_id": observation_id if isinstance(observation_id, str) else None,
            })
            continue
        rows_by_pair.setdefault((chapter_id, aha_ids[0]), []).append((index, row))

    for chapter_id, chapter in chapter_by_id.items():
        for aha_id, aha in aha_by_id.items():
            pair = (chapter_id, aha_id)
            rows = rows_by_pair.get(pair, [])
            relation = _unresolved(chapter_id, aha_id, "RELATION_MISSING", aha.get("observation_id", ""))
            if len(rows) > 1:
                relation["reason_codes"] = ["DUPLICATE_OR_CONFLICTING_RELATION_ROWS"]
            elif rows:
                index, row = rows[0]
                chapter_facts = _fact_ids(row.get("chapter_fact_ids"))
                aha_facts = _fact_ids(row.get("aha_fact_ids"))
                errors = []
                if row.get("relation") not in RELATIONS:
                    errors.append("RELATION_VALUE_INVALID")
                if chapter_facts is None or not set(chapter_facts) <= _candidate_facts(chapter):
                    errors.append("CHAPTER_FACT_REFERENCE_INVALID")
                if aha_facts is None or not set(aha_facts) <= _candidate_facts(aha):
                    errors.append("AHA_FACT_REFERENCE_INVALID")
                if not _text(row.get("reason")):
                    errors.append("RELATION_REASON_MISSING_OR_INVALID")
                if errors:
                    relation["reason_codes"] = errors
                else:
                    relation.update({
                        "relation": row["relation"],
                        "chapter_fact_ids": chapter_facts,
                        "aha_fact_ids": aha_facts,
                        "reason": row["reason"].strip(),
                        "reason_codes": ["EXPLICIT_EDITORIAL_RELATION" if row["relation"] != "UNRESOLVED"
                                         else "MODEL_RELATION_UNRESOLVED"],
                    })
            if relation["relation"] == "UNRESOLVED":
                plan["diagnostics"].append({
                    "code": "PAIR_UNRESOLVED", "chapter_candidate_id": chapter_id,
                    "aha_candidate_id": aha_id, "reason_codes": list(relation["reason_codes"]),
                    "source_indices": [index for index, _ in rows],
                })
            plan["relations"].append(relation)
    return plan


def for_selection(plan, chapter_id, aha_id):
    """Return a copied pair annotation; absence never proves independence."""
    if not isinstance(plan, dict) or plan.get("policy_version") != POLICY_VERSION:
        return _unresolved(chapter_id, aha_id, "ALLOCATION_POLICY_MISSING_OR_UNSUPPORTED")
    matches = [row for row in plan.get("relations", [])
               if row.get("chapter_candidate_id") == chapter_id
               and row.get("aha_candidate_id") == aha_id]
    if len(matches) != 1:
        return _unresolved(chapter_id, aha_id, "RELATION_MISSING_OR_AMBIGUOUS")
    return copy.deepcopy(matches[0])


def project(plan, memories):
    """Project intact distinct-story hints onto actual final-memory facts only.

    No intersection repairs an incomplete relation. Missing final memories,
    missing facts and unresolved relations stay diagnostics, not Writer guidance.
    """
    projected = _empty_plan()
    if not isinstance(plan, dict) or plan.get("policy_version") != POLICY_VERSION:
        projected["diagnostics"].append({"code": "ALLOCATION_POLICY_MISSING_OR_UNSUPPORTED"})
        return projected
    projected["diagnostics"] = copy.deepcopy(plan.get("diagnostics", []))
    memories_by_id = {}
    for memory in memories:
        memories_by_id.setdefault(memory.get("candidate_id"), []).append(memory)
    rows_by_pair = {}
    for row in plan.get("relations", []):
        pair = (row.get("chapter_candidate_id"), row.get("aha_candidate_id"))
        rows_by_pair.setdefault(pair, []).append(row)
    for pair, rows in rows_by_pair.items():
        chapter_id, aha_id = pair
        diagnostic = {"chapter_candidate_id": chapter_id, "aha_candidate_id": aha_id}
        if len(rows) != 1:
            projected["diagnostics"].append({**diagnostic, "code": "RELATION_MISSING_OR_AMBIGUOUS"})
            continue
        row = rows[0]
        if row.get("relation") != "DISTINCT_STORY":
            projected["diagnostics"].append({**diagnostic, "code": "NON_DISTINCT_RELATION_NOT_PROJECTED",
                                             "relation": row.get("relation")})
            continue
        chapter_matches = memories_by_id.get(chapter_id, [])
        aha_matches = memories_by_id.get(aha_id, [])
        if len(chapter_matches) != 1 or len(aha_matches) != 1:
            projected["diagnostics"].append({**diagnostic, "code": "FINAL_MEMORY_MISSING_OR_AMBIGUOUS"})
            continue
        chapter, aha = chapter_matches[0], aha_matches[0]
        if chapter.get("memory_type") != "CHAPTER" or aha.get("memory_type") != "AHA":
            projected["diagnostics"].append({**diagnostic, "code": "FINAL_MEMORY_TYPE_MISMATCH"})
            continue
        chapter_facts = _fact_ids(row.get("chapter_fact_ids"))
        aha_facts = _fact_ids(row.get("aha_fact_ids"))
        actual_chapter_facts = {fact.get("fact_id") for fact in chapter.get("facts", [])}
        actual_aha_facts = {fact.get("fact_id") for fact in aha.get("facts", [])}
        if (chapter_facts is None or aha_facts is None
                or not set(chapter_facts) <= actual_chapter_facts
                or not set(aha_facts) <= actual_aha_facts
                or not _text(row.get("reason"))):
            projected["diagnostics"].append({**diagnostic, "code": "FINAL_RELATION_REFERENCES_OR_REASON_UNAVAILABLE"})
            continue
        projected["relations"].append(copy.deepcopy({key: row[key] for key in (
            "chapter_candidate_id", "aha_candidate_id", "relation",
            "chapter_fact_ids", "aha_fact_ids", "reason",
        )}))
    return projected

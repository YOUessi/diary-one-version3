"""Research-only S07 priority -> S09 membership handoff.

Ordinal editorial judgment is not a score or fact evidence. This module binds
IDs, never infers scenes. Invalid ordering falls back per lane, without retries
or rejecting otherwise valid candidates. Existing eligibility remains upstream.
"""

import copy


POLICY_VERSION = "CODEX_D1_EDITORIAL_ORDER_V01"
POLICY_FIELD = "codex_editorial_order_policy_version"
OUTPUT_FIELD = "editorial_order"


def response_schema(base):
    result = copy.deepcopy(base)
    result["properties"][OUTPUT_FIELD] = {
        "type": "object", "additionalProperties": False,
        "required": ["chapter_keys", "observation_ids", "reason"],
        "properties": {
            "chapter_keys": {"type": "array", "items": {"type": "string"},
                             "uniqueItems": True,
                             "description": "Every proposed Chapter key once, best priority first."},
            "observation_ids": {"type": "array", "items": {"type": "string"},
                                "uniqueItems": True,
                                "description": "Every aha_relation_scope observation_id once, best Aha priority first."},
            "reason": {"type": "string", "description": "Brief relative tradeoff, not new facts or per-asset checklist."},
        },
    }
    result["required"].append(OUTPUT_FIELD)
    return result


def prompt_instruction():
    return (
        "S09 will consume editorial_order, not rank meaningfulness by category, rarity or image-quality scores. "
        "In chapter_keys rank every proposed Chapter once by what is worth retaining from this day's supplied "
        "experiences. Propose worthwhile groups and supported alternatives, not filler for a count. "
        "Before finalizing, consider meaningful unrepresented groups or discoveries; no per-asset omission checklist. "
        "In observation_ids rank every observation in aha_relation_scope once, including those without a native "
        "aha_proposal. This is a compact priority list, not a request for a long proposal for every observation. "
        "Compare the concrete experience or discovery, why it is memorable here, and what it adds to the other "
        "cards. Ordinary moments and quiet distinctive views are allowed; do not require novelty, people or action. "
        "Do not infer the user's private interests. Use reason for a brief relative tradeoff, not another story. "
        "Consider Chapter/Aha duties together using the existing aha_relations. Rank Ahas as backup discoveries "
        "too: a SAME_STORY Aha is suppressed only if its owning Chapter is selected. An unresolved relation is "
        "not a new hard exclusion or proof of independence. S09 retains reference/eligibility checks, the "
        "three-material Chapter floor, no shared Chapter assets and existing capacities; it takes higher priority "
        "feasible candidates first. Import sequence is not capture time. Lists may be empty only when their "
        "corresponding proposal/scope is empty. "
    )


def _bind(order, expected, bindings):
    """Full permutation, then bind only candidates that passed upstream checks."""
    audit = {"status": "FALLBACK_LEGACY_ORDER", "supplied_order": copy.deepcopy(order),
             "ranked_candidate_ids": [], "diagnostics": []}
    if not isinstance(expected, list) or any(not isinstance(v, str) or not v for v in expected):
        audit["diagnostics"].append("INVALID_ORDER_SCOPE")
        return audit
    if len(set(expected)) != len(expected):
        audit["diagnostics"].append("AMBIGUOUS_ORDER_SCOPE")
        return audit
    if not isinstance(order, list) or any(not isinstance(v, str) or not v for v in order):
        audit["diagnostics"].append("ORDER_MISSING_OR_INVALID")
        return audit
    audit["unknown_references"] = [v for v in order if v not in set(expected)]
    audit["missing_references"] = [v for v in expected if v not in set(order)]
    if len(set(order)) != len(order):
        audit["diagnostics"].append("DUPLICATE_ORDER_REFERENCE")
    if audit["unknown_references"]:
        audit["diagnostics"].append("UNKNOWN_ORDER_REFERENCE")
    if audit["missing_references"]:
        audit["diagnostics"].append("INCOMPLETE_ORDER")
    if set(bindings) - set(expected) or len(set(bindings.values())) != len(bindings):
        audit["diagnostics"].append("CANDIDATE_BINDING_MISMATCH")
    if audit["diagnostics"]:
        return audit
    audit.update(status="MODEL_ORDER_BOUND",
                 ranked_candidate_ids=[bindings[v] for v in order if v in bindings],
                 upstream_ineligible_references=[v for v in order if v not in bindings])
    return audit


def compile_order(output, chapter_ledger, aha_candidates, aha_scope):
    """Preserve raw ordering as audit; prose never becomes candidate facts."""
    raw = output.get(OUTPUT_FIELD) if isinstance(output, dict) else None
    raw = raw if isinstance(raw, dict) else {}
    proposals = output.get("storyline_proposals") if isinstance(output, dict) else None
    if not isinstance(proposals, list) or any(not isinstance(p, dict) for p in proposals):
        chapter_keys, bindings = None, {}
    else:
        chapter_keys = [p.get("key") for p in proposals]
        bindings = {proposals[e["source_index"]].get("key"): e["candidate_id"]
                    for e in chapter_ledger if e["validation_status"] == "PASSED"
                    and isinstance(proposals[e["source_index"]].get("key"), str)}
    return {
        "policy_version": POLICY_VERSION, "guidance_scope": "EDITORIAL_JUDGMENT_NOT_FACT_OR_PERSONAL_INTEREST_SCORE",
        "reason": raw.get("reason") if isinstance(raw.get("reason"), str) else None,
        "chapters": _bind(raw.get("chapter_keys"), chapter_keys, bindings),
        "ahas": _bind(raw.get("observation_ids"), [a["observation_id"] for a in aha_scope],
                      {a["observation_id"]: a["candidate_id"] for a in aha_candidates}),
        "additional_model_calls": 0,
    }


def applied(lane):
    return isinstance(lane, dict) and lane.get("status") == "MODEL_ORDER_BOUND"


def select_chapters(candidates, ledger, asset_order, lane, *, minimum, maximum, pair_conflict):
    """Priority-first feasible selection; no proxy value/position thresholds.

    This intentionally prefers the first feasible candidate over a combination
    of lower priorities. It is not a claimed optimal or personalized set score.
    """
    by_id = {c["candidate_id"]: c for c in candidates}
    ranked = [by_id[cid] for cid in lane["ranked_candidate_ids"]]
    selected, rejections, pairs = [], {}, []
    for candidate in ranked:
        cid = candidate["candidate_id"]
        if len(candidate["source_asset_ids"]) < minimum:
            rejections[cid] = "CHAPTER_DISPLAY_NEEDS_THREE_MATERIALS"
            continue
        conflicts = []
        for chosen in selected:
            conflict = pair_conflict(candidate, chosen, asset_order)
            pairs.append({"candidate_a_id": cid, "candidate_b_id": chosen["candidate_id"],
                          "reason_codes": [conflict or "NO_SHARED_ASSET_NOT_PROOF_OF_STORY_INDEPENDENCE"],
                          "same_memory_evidence": [], "distinct_memory_evidence": [],
                          "selection_effect": "FORBID_COSELECT" if conflict else "ALLOW_COSELECT"})
            if conflict:
                conflicts.append(conflict)
        if conflicts:
            rejections[cid] = conflicts[0]
        elif len(selected) >= maximum:
            rejections[cid] = "CHAPTER_PREVIEW_CAPACITY_REACHED"
        else:
            selected.append(dict(candidate))
    membership = [c["candidate_id"] for c in selected]
    ranks = {cid: index + 1 for index, cid in enumerate(lane["ranked_candidate_ids"])}
    for entry in ledger:
        if entry["validation_status"] != "PASSED":
            continue
        cid = entry["candidate_id"]
        entry["editorial_priority"] = ranks[cid]
        entry["selection_status"] = "SELECTED" if cid in membership else "NOT_SELECTED"
        entry["reason_codes"].append("MODEL_EDITORIAL_PRIORITY_SELECTED_NOT_QUALITY_VERIFIED"
                                     if cid in membership else rejections[cid])
    selected.sort(key=lambda c: min(asset_order[a] for a in c["source_asset_ids"]))
    return selected, {
        "algorithm": "MODEL_EDITORIAL_PRIORITY_THEN_EXISTING_FEASIBILITY",
        "editorial_order": copy.deepcopy(lane), "ranked_candidate_ids": lane["ranked_candidate_ids"],
        "selected_candidate_ids": membership, "published_sequence_candidate_ids": [c["candidate_id"] for c in selected],
        "publication_order_basis": "IMPORT_SEQUENCE_NOT_CHRONOLOGY", "pair_ledger": pairs,
        "rejections": rejections, "proxy_value_thresholds_applied": False,
        "eligible_candidate_count": sum(len(c["source_asset_ids"]) >= minimum for c in candidates),
        "target_note": "Capacity is a ceiling, not a quota. Model proposals still determine available experiences.",
    }

"""Opt-in recording-context and explicit joint recommendation, not a day score.

No model calls, scene vocabulary, interest scoring or automatic slot filling.
The model owns semantic recommendations; this module binds and executes them.
Partial execution is observable and never certifies semantic independence.
"""

import copy
from collections import Counter

from . import codex_editorial_allocation as allocation


POLICY_VERSION = "CODEX_D2_RECORDING_EDITOR_V01"
POLICY_FIELD = "codex_recording_editor_policy_version"
OUTPUT_FIELD = "day_selection"
CONTEXT_FIELD = "recording_context"


def consideration_scope(observations, roles):
    """Project existing usable facts, without event-kind/salience eligibility."""
    keep = {r["observation_id"] for r in roles if r["role"] == "KEEP"}
    scope = []
    for observation in observations:
        facts = [f["fact_id"] for f in observation.get("facts", [])
                 if f.get("support_grade") in ("STRONG", "MODERATE")
                 and isinstance(f.get("fact_id"), str) and f["fact_id"]]
        if observation["id"] in keep and facts:
            scope.append({"observation_id": observation["id"], "event_fact_ids": facts})
    return scope


def input_context():
    """Current research bundle has no verified wear/chronology/GPS provenance."""
    return {
        "scope": "SUPPLIED_RECORDING_COLLECTION_NOT_VERIFIED_COMPLETE_DAY",
        "capture_time_reliable": False,
        "gps_available": False,
        "wear_duration_minutes": None,
        "capture_coverage": "UNKNOWN",
        "personal_routine_baseline": "UNAVAILABLE",
        "constraints": [
            "ASSET_COUNT_AND_VIDEO_DURATION_ARE_NOT_WEAR_DURATION",
            "IMPORT_ORDER_DOES_NOT_ESTABLISH_TIME_OR_ACTIVITY_BOUNDARIES",
            "SPARSE_MATERIAL_IS_NOT_PROOF_OF_LOW_VALUE_OR_AN_ORDINARY_DAY",
            "CONTEXT_IS_REVISABLE_EDITORIAL_GUIDANCE_NOT_FACT_OR_USER_PROFILE",
        ],
    }


def response_schema(base):
    result = copy.deepcopy(base)
    result["properties"][CONTEXT_FIELD] = {
        "type": "object", "additionalProperties": False,
        "required": ["summary", "uncertainty"],
        "properties": {
            "summary": {"type": "string", "description": "Brief evidence-led overview of the supplied recording, not the user's whole day or personal value."},
            "uncertainty": {"type": "string", "description": "Briefly state what the supplied material cannot establish; no invented history, time or GPS."},
        },
    }
    result["properties"][OUTPUT_FIELD] = {
        "type": "object", "additionalProperties": False,
        "required": ["chapter_keys", "observation_ids", "reason"],
        "properties": {
            "chapter_keys": {"type": "array", "items": {"type": "string"},
                             "uniqueItems": True,
                             "description": "Only recommended Chapter proposal keys, not all alternatives. Empty is allowed."},
            "observation_ids": {"type": "array", "items": {"type": "string"},
                                "uniqueItems": True,
                                "description": "Only recommended native aha_proposals observation_ids. Empty is allowed."},
            "reason": {"type": "string", "description": "Brief joint tradeoff and incremental contribution across the recommended cards; explain an empty selection without claiming absence of value."},
        },
    }
    result["required"].extend([CONTEXT_FIELD, OUTPUT_FIELD])
    result["properties"]["storyline_proposals"]["items"]["properties"]["aha_relations"]["description"] = (
        "Relations from this Chapter to nominated Ahas with potentially overlapping stories. "
        "Do not enumerate all consideration-scope observations. Missing is unresolved."
    )
    return result


def prompt_instruction():
    return (
        "This opt-in recording editor uses day_selection as one explicit joint recommendation, not two "
        "complete rankings. First summarize the supplied collection in recording_context: what experiences "
        "are supported and what remains unknown. The collection may cover selected activity segments, not "
        "a complete day. Its organization may be focused, varied, mixed or unclear; do not impose a day-type "
        "taxonomy, value score, personal-interest profile or ordinary/special quota. Do not infer wear time, "
        "routine, weekday, novelty to this user or missing experiences from asset count, import order or video "
        "duration. A short recording can contain worthwhile memories. Use the overview to guide grouping "
        "and focus, never as additional facts. The current contract has no reliable capture times or GPS. "
        "aha_relation_scope contains ALL usable supported observations for consideration. Event kind, "
        "salience and other labels do not grant or deny Aha eligibility. Actively look for grounded small "
        "discoveries and meaningful moments across this scope; do not require people, action, rarity or a "
        "major event. Nominate worthwhile Ahas in aha_proposals with their existing event_fact_ids and a "
        "concrete narrative_duty. Do not make an Aha for every observation. Each recommended Aha MUST have "
        "one unambiguous native proposal. No program-generated event candidate will fill an empty slot. "
        "Compare Chapters and Ahas together: each recommended card should contribute something worth "
        "keeping beyond the other recommended cards. Also compare Ahas with each other. An unselected "
        "Chapter does not entitle all its fragments to become Ahas. Shared place, motif or category alone "
        "does not establish a shared story. Keep concrete planned focus in thesis/narrative_duty rather "
        "than an object inventory; this does not guarantee that later media selection will preserve it. "
        "Return ONLY the recommended subset in day_selection.chapter_keys and observation_ids. Supported "
        "alternatives may remain in proposals without being recommended. Explain the joint tradeoff briefly "
        "in reason, including when no Aha is recommended. The program executes valid recommended entries "
        "in listed order, does not rerank by proxy scores and does not replace rejected entries with other "
        "candidates. Existing limits remain: at most 4 Chapters, at least 3 KEEP materials per Chapter, "
        "at most 3 Ahas with Chapters and at most 1 Aha without Chapters. These are ceilings, not quotas; "
        "the no-Chapter limit is inherited, not evidence that sparse recordings lack value. "
    )


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _bind_subset(raw, proposals, identity_field, bindings):
    lane = {"status": "MISSING_OR_INVALID_SELECTION", "supplied_references": copy.deepcopy(raw),
            "recommended_candidate_ids": [], "diagnostics": []}
    if not isinstance(raw, list):
        lane["diagnostics"].append({"code": "SELECTION_LIST_MISSING_OR_INVALID"})
        return lane
    counts = Counter(p.get(identity_field) for p in proposals
                     if isinstance(p, dict) and _text(p.get(identity_field))) if isinstance(proposals, list) else Counter()
    if not isinstance(proposals, list):
        lane["diagnostics"].append({"code": "PROPOSAL_LIST_MISSING_OR_INVALID"})
    seen = set()
    for index, reference in enumerate(raw):
        error = None
        if not _text(reference):
            error = "SELECTION_REFERENCE_INVALID"
        elif reference in seen:
            error = "DUPLICATE_SELECTION_REFERENCE"
        elif counts[reference] == 0:
            error = "UNKNOWN_PROPOSAL_REFERENCE"
        elif counts[reference] > 1:
            error = "AMBIGUOUS_PROPOSAL_REFERENCE"
        elif reference not in bindings:
            error = "RECOMMENDED_PROPOSAL_NOT_ELIGIBLE"
        if _text(reference):
            seen.add(reference)
        if error:
            lane["diagnostics"].append({"code": error, "index": index, "reference": copy.deepcopy(reference)})
        else:
            lane["recommended_candidate_ids"].append(bindings[reference])
    lane["status"] = "PARTIAL_SELECTION_BOUND" if lane["diagnostics"] else "MODEL_SELECTION_BOUND"
    return lane


def compile_plan(output, chapter_ledger, aha_candidates, scope):
    output = output if isinstance(output, dict) else {}
    raw = output.get(OUTPUT_FIELD)
    raw = raw if isinstance(raw, dict) else {}
    chapters = output.get("storyline_proposals")
    chapter_bindings = {}
    for entry in chapter_ledger:
        index = entry.get("source_index")
        if (entry.get("validation_status") == "PASSED" and isinstance(chapters, list)
                and isinstance(index, int) and 0 <= index < len(chapters)
                and isinstance(chapters[index], dict) and _text(chapters[index].get("key"))):
            chapter_bindings[chapters[index]["key"]] = entry["candidate_id"]
    context = output.get(CONTEXT_FIELD)
    context = context if isinstance(context, dict) else {}
    diagnostics = []
    for field in ("summary", "uncertainty"):
        if not _text(context.get(field)):
            diagnostics.append({"code": "RECORDING_CONTEXT_FIELD_MISSING", "field": field})
    if not _text(raw.get("reason")):
        diagnostics.append({"code": "JOINT_SELECTION_REASON_MISSING"})
    return {
        "policy_version": POLICY_VERSION,
        "guidance_scope": "EDITORIAL_JUDGMENT_NOT_FACT_OR_PERSONAL_INTEREST_SCORE",
        "recording_input_context": input_context(),
        CONTEXT_FIELD: copy.deepcopy(context),
        "reason": raw.get("reason") if isinstance(raw.get("reason"), str) else None,
        "aha_consideration_scope": copy.deepcopy(scope),
        "chapters": _bind_subset(raw.get("chapter_keys"), chapters, "key", chapter_bindings),
        "ahas": _bind_subset(raw.get("observation_ids"), output.get("aha_proposals"), "observation_id",
                             {a["observation_id"]: a["candidate_id"] for a in aha_candidates}),
        "diagnostics": diagnostics, "additional_model_calls": 0,
        "semantic_quality": "NOT_VERIFIED_BY_REFERENCE_BINDING_OR_MODEL_REASON",
    }


def _execute_lane(candidates, ledger, lane, maximum, conflict_for, order_key):
    by_id = {c["candidate_id"]: c for c in candidates}
    selected, rejections, checks = [], {}, []
    for cid in lane["recommended_candidate_ids"]:
        candidate = by_id[cid]
        conflict = conflict_for(candidate, selected, checks)
        if conflict:
            rejections[cid] = conflict
        elif len(selected) >= maximum:
            rejections[cid] = "INHERITED_PREVIEW_CAPACITY_REACHED"
        else:
            selected.append(copy.deepcopy(candidate))
    selected_ids = [c["candidate_id"] for c in selected]
    for entry in ledger:
        if entry.get("validation_status") != "PASSED":
            continue
        cid = entry["candidate_id"]
        entry["selection_status"] = "SELECTED" if cid in selected_ids else "NOT_SELECTED"
        entry["reason_codes"].append(
            "EXPLICIT_MODEL_RECOMMENDATION_EXECUTED_NOT_QUALITY_VERIFIED" if cid in selected_ids
            else rejections.get(cid, "MODEL_DID_NOT_RECOMMEND" if lane["status"] == "MODEL_SELECTION_BOUND"
                                else "NOT_IN_VALID_RECOMMENDATION_PART_OF_PARTIAL_PLAN"))
    selected.sort(key=order_key)
    return selected, {
        "algorithm": "EXPLICIT_JOINT_RECOMMENDATION_WITH_TECHNICAL_CONSTRAINTS",
        "recommended_candidate_ids": list(lane["recommended_candidate_ids"]),
        "selected_candidate_ids": selected_ids,
        "published_sequence_candidate_ids": [c["candidate_id"] for c in selected],
        "publication_order_basis": "IMPORT_SEQUENCE_NOT_CHRONOLOGY",
        "pair_ledger": checks, "rejections": rejections,
        "selection_binding_status": lane["status"],
        "proxy_value_thresholds_applied": False, "automatic_fill_applied": False,
        "eligible_candidate_count": len(candidates), "capacity": maximum,
    }


def execute_plan(plan, chapters, chapter_ledger, ahas, aha_ledger, asset_order,
                 allocation_plan, *, minimum, max_chapters, max_ahas):
    """Execute one model-authored set. Conflicts cause explicit partial execution.

    C/A source sharing is allowed for a distinct story; C/C and A/A exact source
    duplicates are not. Motif overlap does not infer semantic duplication here.
    """
    def chapter_conflict(candidate, selected, checks):
        if len(candidate["source_asset_ids"]) < minimum:
            return "CHAPTER_DISPLAY_NEEDS_THREE_MATERIALS"
        conflict = None
        for other in selected:
            shared = set(candidate["source_asset_ids"]) & set(other["source_asset_ids"])
            checks.append({"candidate_a_id": candidate["candidate_id"], "candidate_b_id": other["candidate_id"],
                           "shared_asset_ids": sorted(shared),
                           "reason_codes": ["EXACT_SHARED_CHAPTER_ASSET" if shared else "NO_EXACT_DUPLICATE_NOT_PROOF_OF_STORY_INDEPENDENCE"]})
            if shared:
                conflict = "EXACT_SHARED_CHAPTER_ASSET"
        return conflict

    chosen_chapters, chapter_audit = _execute_lane(
        chapters, chapter_ledger, plan["chapters"], max_chapters, chapter_conflict,
        lambda c: min(asset_order[a] for a in c["source_asset_ids"]))

    chapter_relations, chapter_conflicts = [], []

    def aha_conflict(candidate, selected, checks):
        conflict = None
        for chapter in chosen_chapters:
            relation = allocation.for_selection(allocation_plan, chapter["candidate_id"], candidate["candidate_id"])
            chapter_relations.append(relation)
            if relation["relation"] == "SAME_STORY":
                conflict = "SAME_MODEL_ALLOCATED_CHAPTER_STORY"
                chapter_conflicts.append({"aha_candidate_id": candidate["candidate_id"],
                                          "chapter_candidate_id": chapter["candidate_id"], "reason_code": conflict})
        for other in selected:
            duplicate = (candidate["observation_id"] == other["observation_id"]
                         or candidate["source_asset_id"] == other["source_asset_id"])
            checks.append({"candidate_a_id": candidate["candidate_id"], "candidate_b_id": other["candidate_id"],
                           "reason_codes": ["EXACT_AHA_DUPLICATE" if duplicate else "NO_EXACT_DUPLICATE_NOT_PROOF_OF_STORY_INDEPENDENCE"],
                           "semantic_comparison_owner": "S07_JOINT_RECOMMENDATION_NOT_VERIFIED"})
            if duplicate:
                conflict = "EXACT_AHA_DUPLICATE"
        return conflict

    chosen_ahas, aha_audit = _execute_lane(
        ahas, aha_ledger, plan["ahas"], max_ahas if chosen_chapters else 1, aha_conflict,
        lambda c: (asset_order[c["source_asset_id"]], c["candidate_id"]))
    if chosen_ahas:
        outcome = "GROUNDED_MODEL_RECOMMENDED_AHA_SELECTED"
    elif plan["ahas"]["status"] != "MODEL_SELECTION_BOUND":
        outcome = "AHA_RECOMMENDATION_TECHNICALLY_UNRESOLVED"
    elif plan["ahas"]["recommended_candidate_ids"]:
        outcome = "RECOMMENDED_AHAS_NOT_EXECUTABLE_WITH_EXISTING_CONSTRAINTS"
    else:
        outcome = "MODEL_RECOMMENDED_NO_AHA_NOT_PROOF_OF_NO_VALUE"
    aha_audit.update(search_outcome=outcome, search_contract=POLICY_VERSION,
                     chapter_relations=chapter_relations, chapter_conflicts=chapter_conflicts,
                     event_category_gating_applied=False, motif_overlap_gating_applied=False)
    complete = (not plan["diagnostics"] and all(
        plan[lane]["status"] == "MODEL_SELECTION_BOUND" and not audit["rejections"]
        for lane, audit in (("chapters", chapter_audit), ("ahas", aha_audit))))
    plan["execution_status"] = "COMPLETE_RECOMMENDATION_EXECUTED" if complete else "PARTIAL_OR_MISSING_RECOMMENDATION"
    return chosen_chapters, chosen_ahas, chapter_audit, aha_audit

"""Display-only selection. No scene vocabulary, similarity threshold or regrouping."""

import json

from . import codex_editorial_allocation as allocation

POLICY_VERSION = "DIARY_ONE_X02_CHAPTER_MEDIA_V01"
RESPONSE_ACCEPTANCE_VERSION = "DIARY_ONE_X02_CHAPTER_SELECTION_RESPONSE_V02"
MIN_MEDIA = 3
MAX_MEDIA = 5
MAX_COMPARISON_FRAMES = 12

SELECTION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["ranked_observation_ids", "display_count", "reason"],
    "properties": {
        "ranked_observation_ids": {
            "type": "array", "items": {"type": "string"},
            "minItems": MIN_MEDIA, "maxItems": MAX_COMPARISON_FRAMES,
            "uniqueItems": True,
            "description": (
                "Chosen observation IDs in priority order; the first display_count IDs are selected. "
                "Only the chosen subset is needed. A longer or complete ranking is also accepted."
            ),
        },
        "display_count": {"type": "integer", "minimum": MIN_MEDIA, "maximum": MAX_MEDIA},
        "reason": {"type": "string"},
    },
}


def selection_prompt(context):
    allocation_note = (
        "chapter_aha_relations contains the existing cross-card editorial allocation, not new facts. "
        "Keep the Chapter's theme represented while respecting the stated separate Aha focus. "
        "Do not remove a material merely because an Aha shares it, invent a difference, borrow facts "
        "from another card, regroup, or reduce the three-material floor. "
        if context.get(allocation.POLICY_FIELD) == allocation.POLICY_VERSION else ""
    )
    return (
        "Select display material for ONE already-established Diary One Chapter. "
        "Compare the supplied preview images directly; do not infer visual repetition from tags, "
        "similar wording, or shared subject categories. Do not regroup material or reject this Chapter. "
        "Return chosen observation IDs in ranked_observation_ids, best first, each ID at most once. "
        "Returning only the chosen three to five is sufficient; omitted materials need not be ranked. "
        "A longer ranking is also accepted: its first display_count IDs are selected. "
        "The first three should form the strongest "
        "representative set, balancing image quality and useful visual differences. "
        "Use content_brief to consider how each material contributes to this Chapter's theme, "
        "specific character and additional meaning, not just visual differences. Its theme and contribution "
        "hints are editorial context, not new evidence or required wording; rely on the supplied images "
        "and facts. Empty hints do not block selection. The fact IDs preserve each material's scope, "
        "not proof that different images share one scene or temporal sequence. "
        "Keep at least three usable materials even when some are similar. This does not require "
        "three unrelated subjects. Prefer three over four or five when the extras largely repeat "
        "what is already visible. Add a fourth or fifth only for worthwhile additional visual content "
        "or a meaningful different view. Choose display_count from 3 to 5, no more than the number "
        "of IDs you return. "
        "The first ranked item is the cover. Explain the selection briefly in Chinese, referring to "
        "the actual images; do not invent times, events or new facts. Import order is not capture time. "
        "Each video has only its existing preview frame here: unseen motion is unknown, not redundant. "
        "Omitted display items still belong to this Chapter and are not deleted. "
        + allocation_note + "Input:\n"
        + json.dumps(context, ensure_ascii=False)
    )


def choose_display(members, model_output=None, fallback_reason="MODEL_NOT_AVAILABLE"):
    """Normalize references/count only; a model failure cannot remove the Chapter."""
    member_ids = [str(item["id"]) for item in members]
    ranked = sorted(members, key=lambda item: (-float(item["quality_score"]), str(item["id"])))
    ranked_ids = [str(item["id"]) for item in ranked]
    source = "QUALITY_ONLY_FALLBACK_NOT_DEDUP_VERIFIED"
    reason = ""
    count = MIN_MEDIA
    count_adjusted = False
    if len(members) == MIN_MEDIA:
        source = "THREE_MEMBER_FLOOR_NO_COMPARISON_NEEDED"
        fallback_reason = ""
    elif isinstance(model_output, dict):
        proposed = model_output.get("ranked_observation_ids")
        requested = model_output.get("display_count")
        if (
            isinstance(proposed, list)
            and all(isinstance(value, str) for value in proposed)
            and len(proposed) >= MIN_MEDIA
            and len(proposed) == len(set(proposed))
            and set(proposed).issubset(member_ids)
            and isinstance(requested, int) and not isinstance(requested, bool)
        ):
            # Preserve the actual model order; never invent a ranking for omitted members.
            ranked_ids = list(proposed)
            count = max(MIN_MEDIA, min(MAX_MEDIA, len(proposed), requested))
            count_adjusted = count != requested
            source = "MODEL_VISUAL_SELECTION"
            raw_reason = model_output.get("reason", "")
            reason = raw_reason.strip() if isinstance(raw_reason, str) else ""
            fallback_reason = ""
        else:
            fallback_reason = "MODEL_SELECTION_REFERENCES_OR_COUNT_INVALID"
    selected = ranked_ids[:count]
    return {
        "policy_version": POLICY_VERSION,
        "response_acceptance_version": RESPONSE_ACCEPTANCE_VERSION,
        "selected_observation_ids": selected,
        "ranked_observation_ids": ranked_ids,
        "ranking_scope": "ALL_MEMBERS" if len(ranked_ids) == len(member_ids) else "RETURNED_SUBSET",
        "omitted_observation_ids": [value for value in member_ids if value not in selected],
        "selection_source": source,
        "model_reason": reason,
        "fallback_reason": fallback_reason,
        "count_adjusted_to_display_contract": count_adjusted,
        "candidate_membership_changed": False,
    }

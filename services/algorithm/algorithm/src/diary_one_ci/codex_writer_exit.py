"""Writer delivery rules, not a semantic judge or another generation step."""

import copy


POLICY_FIELD = "writer_exit_policy_version"
LEGACY_POLICY_VERSION = "DIARY_ONE_X02_WRITER_EXIT_V01"
POLICY_VERSION = "DIARY_ONE_X02_WRITER_EXIT_V02"
AHA_TARGET = 20
AHA_TOLERANCE = 24


def enabled(context):
    return context.get(POLICY_FIELD) in (LEGACY_POLICY_VERSION, POLICY_VERSION)


def soft_length_enabled(context):
    return context.get(POLICY_FIELD) == POLICY_VERSION and context.get("locale") == "zh-Hans"


def length_audit(visible_length):
    over = visible_length > AHA_TOLERANCE
    result = {
        "writing_target_visible_max": AHA_TARGET,
        "tolerance_visible_max": AHA_TOLERANCE,
        "length_status": ("OVER_TOLERANCE_REVIEW" if over else
                          "WITHIN_TOLERANCE" if visible_length > AHA_TARGET else "WITHIN_TARGET"),
        "length_review_required": over,
        "quality_flags": ["AHA_LENGTH_OVER_TOLERANCE_REVIEW"] if over else [],
    }
    if over:
        result["length_review_label"] = "偏长，待评价"
    return result


def response_schema(schema, context):
    """Align advisory schema text with the active policy; not constrained decoding."""
    if not soft_length_enabled(context):
        return schema
    result = copy.deepcopy(schema)
    # The legacy schema shares its item object across both buckets. Break that alias.
    result["properties"]["ahas"]["items"] = copy.deepcopy(result["properties"]["ahas"]["items"])
    result["properties"]["chapters"]["items"]["properties"]["text"]["description"] = (
        "Chapter: one concise sentence by default, at most two when the second adds "
        "materially distinct approved information."
    )
    result["properties"]["ahas"]["items"]["properties"]["text"]["description"] = (
        f"Aha: exactly one user-visible sentence. Aim for {AHA_TARGET} visible Chinese "
        f"characters; {AHA_TARGET + 1}-{AHA_TOLERANCE} are acceptable. Longer text is "
        "retained for length review, not automatically rejected or truncated. Stay focused."
    )
    return result


def normalize_buckets(output, context):
    """Ignore wrong-type copies only when the correct bucket has one item.

    Expected types come from the selected candidates, never from prose. Multiple
    entries in the correct bucket remain ambiguous and are not auto-resolved.
    """
    if not enabled(context) or not isinstance(output, dict):
        return output, {}
    normalized = copy.deepcopy(output)
    notes = {}
    for memory in context["memories"]:
        candidate_id = memory["candidate_id"]
        correct = "chapters" if memory["memory_type"] == "CHAPTER" else "ahas"
        wrong = "ahas" if correct == "chapters" else "chapters"
        correct_items = normalized.get(correct, [])
        wrong_items = normalized.get(wrong, [])
        if not isinstance(correct_items, list) or not isinstance(wrong_items, list):
            continue

        def matches(item):
            return isinstance(item, dict) and item.get("candidate_id") == candidate_id

        if sum(matches(item) for item in correct_items) != 1:
            continue
        misplaced = sum(matches(item) for item in wrong_items)
        if misplaced:
            normalized[wrong] = [item for item in wrong_items if not matches(item)]
            notes[candidate_id] = {
                "normalization_codes": ["WRITER_WRONG_BUCKET_COPY_IGNORED"],
                "ignored_wrong_bucket_copy_count": misplaced,
            }
    return normalized, notes

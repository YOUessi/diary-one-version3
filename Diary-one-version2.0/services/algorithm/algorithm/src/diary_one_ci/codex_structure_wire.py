"""Single-source model output -> existing internal structure, without inference.

The model supplies each Chapter member/fact binding once in beat_map. This
adapter only derives redundant lists and qualifies nested relation references.
It preserves invalid rows for the existing validators, not partial repair.
"""

import copy


POLICY_VERSION = "DIARY_ONE_X02_STRUCTURE_WIRE_V01"
POLICY_FIELD = "structure_wire_policy_version"


def response_schema(base):
    """Transform a copy of the V1.66 schema; public/legacy schemas stay intact."""
    result = copy.deepcopy(base)
    properties = result["properties"]
    relation_array = properties.pop("chapter_aha_relations")
    result["required"].remove("chapter_aha_relations")
    relation = relation_array["items"]
    relation["properties"].pop("chapter_key")
    observation = relation["properties"].pop("aha_observation_id")
    observation["description"] = "Copy the exact input observation_id, as in beat_map and aha_proposals."
    relation["properties"]["observation_id"] = observation
    relation["required"] = ["observation_id" if field == "aha_observation_id" else field
                            for field in relation["required"] if field != "chapter_key"]
    relation_array["description"] = (
        "Relations to this Chapter: include eligible Aha observations among its beat_map members "
        "even without native aha_proposals, plus other potentially overlapping Aha stories. "
        "Do not enumerate unrelated pairs. Missing remains unresolved."
    )
    chapter = properties["storyline_proposals"]["items"]
    members = chapter["properties"].pop("observation_ids")
    chapter["properties"].pop("fact_ids")
    chapter["required"] = [field for field in chapter["required"]
                           if field not in ("observation_ids", "fact_ids")]
    chapter["properties"]["beat_map"]["maxItems"] = members["maxItems"]
    chapter["properties"]["beat_map"]["description"] = (
        "The sole Chapter membership and fact-reference list. One complete entry per chosen member; "
        "do not repeat observation_ids or fact_ids in a separate Chapter-level summary."
    )
    chapter["properties"]["aha_relations"] = relation_array
    chapter["required"].append("aha_relations")
    aha = properties["aha_proposals"]["items"]
    aha["properties"].pop("key")
    aha["required"].remove("key")
    aha["properties"]["observation_id"]["description"] = (
        "Copy the exact input observation_id; do not invent an Aha name or a second identity."
    )
    return result


def normalize_output(raw):
    """Return a copied legacy-shaped value and a separate derivation receipt.

No ID lookup, alias repair, role inference, text rewriting, scoring or model call.
Invalid beat entries are not dropped: the unchanged beat_map and invalid derived
values reach the old candidate validator together. Retired extra fields are
recorded but cannot become a second authority in this explicit new wire path.
"""
    audit = {"policy_version": POLICY_VERSION, "chapters": [], "ahas": [],
             "diagnostics": [], "facts_created": 0, "model_calls_added": 0}
    if not isinstance(raw, dict):
        audit["diagnostics"].append({"code": "STRUCTURE_OUTPUT_NOT_OBJECT"})
        return copy.deepcopy(raw), audit
    output = copy.deepcopy(raw)
    if "chapter_aha_relations" in raw:
        audit["diagnostics"].append({"code": "RETIRED_TOP_LEVEL_RELATIONS_IGNORED"})
    output["chapter_aha_relations"] = []
    chapters = output.get("storyline_proposals")
    for index, chapter in enumerate(chapters if isinstance(chapters, list) else []):
        if not isinstance(chapter, dict):
            audit["diagnostics"].append({"code": "CHAPTER_ROW_NOT_OBJECT", "source_index": index})
            continue
        entry = {"source_index": index, "chapter_key": chapter.get("key"),
                 "source": "UNCHANGED_BEAT_MAP", "ignored_legacy_summary_fields": {}}
        for field in ("observation_ids", "fact_ids"):
            if field in chapter:
                entry["ignored_legacy_summary_fields"][field] = copy.deepcopy(chapter[field])
        beats = chapter.get("beat_map")
        if isinstance(beats, list):
            # None is an invalid structural value, not a generated fact/ID.
            members = [beat.get("observation_id") if isinstance(beat, dict) else None
                       for beat in beats]
            fact_lists = [beat.get("fact_ids") if isinstance(beat, dict) else None
                          for beat in beats]
            facts = ([fact for values in fact_lists for fact in values]
                     if all(isinstance(values, list) for values in fact_lists) else None)
        else:
            members, facts = None, None
        chapter["observation_ids"] = members
        chapter["fact_ids"] = facts
        entry["derived_observation_ids"] = copy.deepcopy(members)
        entry["derived_fact_ids"] = copy.deepcopy(facts)
        relations = chapter.pop("aha_relations", None)
        entry["nested_relation_count"] = len(relations) if isinstance(relations, list) else None
        if not isinstance(relations, list):
            audit["diagnostics"].append({"code": "NESTED_RELATIONS_MISSING_OR_INVALID",
                                         "source_index": index, "chapter_key": chapter.get("key")})
        else:
            for row in relations:
                if not isinstance(row, dict):
                    output["chapter_aha_relations"].append(row)
                    continue
                qualified = {field: copy.deepcopy(row.get(field)) for field in
                             ("relation", "chapter_fact_ids", "aha_fact_ids", "reason")}
                qualified["chapter_key"] = chapter.get("key")
                qualified["aha_observation_id"] = row.get("observation_id")
                output["chapter_aha_relations"].append(qualified)
        audit["chapters"].append(entry)
    ahas = output.get("aha_proposals")
    for index, aha in enumerate(ahas if isinstance(ahas, list) else []):
        if not isinstance(aha, dict):
            continue
        entry = {"source_index": index, "observation_id": aha.get("observation_id")}
        if "key" in aha:
            entry["ignored_legacy_key"] = aha["key"]
        # Only an internal ledger label; actual identity still passes the same
        # observation and fact checks. No second model-authored key exists.
        aha["key"] = aha.get("observation_id", "")
        audit["ahas"].append(entry)
    audit["flattened_relation_count"] = len(output["chapter_aha_relations"])
    return output, audit

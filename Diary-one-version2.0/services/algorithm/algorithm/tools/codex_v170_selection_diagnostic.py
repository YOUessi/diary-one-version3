"""Read-only S09 comparison on one actual fresh S07 response; no model call.

Tests attribution and factual ownership paths, not semantic gold labels. Does
not change the run or restore suppressed Ahas. Output remains private/local.
"""
import hashlib
import json
import sys
import uuid
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "var/codex_v1_70_editorial_order"
AREA = ROOT / "var/codex_v1_70_full_chain_execution"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def run(pack):
    candidate = load(FROZEN / "codex_candidate.json")
    for name, digest in candidate["source_sha256"].items():
        assert hashlib.sha256((FROZEN / "codex_candidate_runtime" / name).read_bytes()).hexdigest() == digest
    sys.path.insert(0, str(FROZEN / "codex_candidate_runtime/src"))
    from diary_one_ci import x02, codex_structure_wire as wire, codex_editorial_allocation as allocation
    directory = AREA / ("pack_%s/round_1" % pack)
    path = directory / "codex_full_run.json"
    result = load(path)["result"]
    trace = result["decision_trace"]
    manifest = load(directory / "codex_manifest.json")
    order = {a["asset_id"]: a["sequence_index"] for a in manifest["assets"]}
    requests = [load(p) for p in sorted((directory / "codex_stage_calls").glob("codex_[0-9][0-9][0-9]_request.json"))]
    request = next(q for q in requests if q["stage"] == "S05_S07_STRUCTURE_PROPOSAL")
    raw = load(directory / ("codex_stage_calls/codex_%03d_response.json" % request["index"]))["output"]
    normalized, _ = wire.normalize_output(raw)
    args = (uuid.UUID(result["session_id"]), result["observations"], trace["observation_roles"],
            result["moments"], normalized, order)
    chapters, cl = x02._build_storyline_candidates(*args)
    ahas, al = x02._build_aha_candidates(*args, value_first=True)
    relations = allocation.compile_relations(normalized, chapters, cl, ahas)
    cs, ca = x02._select_storyline_set(chapters, cl, result["observations"], order)
    aas, aa = x02._select_aha_set(ahas, al, cs, result["observations"], order,
                                 value_first=True, allocation_plan=relations)
    actual_chapters = trace["chapter_set_selection"]["selected_candidate_ids"]
    actual_ahas = trace["aha_set_selection"]["selected_candidate_ids"]
    chapter_lookup = {c["candidate_id"]: c for c in chapters}
    aha_lookup = {a["candidate_id"]: a for a in ahas}
    final_owners = {c["candidate_id"]: c for c in result["chapters"]}
    losses = []
    for conflict in trace["aha_set_selection"]["chapter_conflicts"]:
        aha = aha_lookup[conflict["aha_candidate_id"]]
        owner = final_owners.get(conflict["chapter_candidate_id"])
        if owner is None:
            continue
        retained = {m["source_asset_id"] for m in owner["selected_media"]}
        if aha["source_asset_id"] not in retained:
            losses.append({**conflict, "asset_index": order[aha["source_asset_id"]] + 1,
                           "owner_title": owner["title"], "owner_selected_assets": [order[a] + 1 for a in retained],
                           "event_facts_still_in_final_owner_claims": bool(set(aha["event_fact_ids"]) & {c["fact_id"] for c in owner["claims"]}),
                           "interpretation": "MATERIAL_OMISSION_PATH_NOT_AUTOMATIC_PROOF_OF_LOST_DISTINCT_STORY"})
    summary = {
        "pack": pack, "source_result_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "scope": "SAME_FRESH_FACTS_AND_S07_OUTPUT_LOCAL_S09_ONLY_NOT_NEW_FULL_MODEL_TEST",
        "external_calls": 0, "same_chapter_membership": set(actual_chapters) == {c["candidate_id"] for c in cs},
        "same_aha_membership": set(actual_ahas) == {a["candidate_id"] for a in aas},
        "current_chapter_assets": [[order[a] + 1 for a in chapter_lookup[cid]["source_asset_ids"]] for cid in actual_chapters],
        "legacy_chapter_assets": [[order[a] + 1 for a in c["source_asset_ids"]] for c in cs],
        "current_aha_assets": [order[aha_lookup[cid]["source_asset_id"]] + 1 for cid in actual_ahas],
        "legacy_aha_assets": [order[a["source_asset_id"]] + 1 for a in aas],
        "same_story_suppressed_then_owner_media_omitted": losses,
        "caution": "No semantic decisions or runtime rules created by this diagnostic; empty loss list does not prove perfect coverage.",
    }
    with (directory / "codex_selection_diagnostic.json").open("x", encoding="utf-8") as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    assert len(sys.argv) == 2 and sys.argv[1] in ("1", "2", "3")
    run(sys.argv[1])

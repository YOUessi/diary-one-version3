"""Mechanical private run summary. No model calls or semantic quality scoring."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / "var/codex_v1_70_full_chain_execution"


def read(p):
    return json.loads(p.read_text(encoding="utf-8"))


def summarize(pack):
    path = AREA / ("pack_%s/round_1" % pack)
    raw = read(path / "codex_full_run.json")
    manifest = read(path / "codex_manifest.json")
    result = raw.get("result", {})
    trace = result.get("decision_trace", {})
    indices = {a["asset_id"]: a["sequence_index"] + 1 for a in manifest["assets"]}
    observations = {o["id"]: o for o in result.get("observations", [])}
    chapters = {c["candidate_id"]: c for c in trace.get("chapter_candidates", []) if c.get("candidate_id")}
    cards = []
    for kind, field in (("CHAPTER", "chapters"), ("AHA", "ahas")):
        for i, c in enumerate(result.get(field, []), 1):
            candidate = chapters.get(c["candidate_id"], {})
            cards.append({"key": ("C" if kind == "CHAPTER" else "A") + str(i),
                "candidate_id": c["candidate_id"], "kind": kind, "title": c["title"], "story": c["story"],
                "story_character_count": len(c["story"]), "tags": c.get("tags"),
                "selected_assets": [indices[m["source_asset_id"]] for m in c["selected_media"]],
                "candidate_assets": [indices[a] for a in candidate.get("source_asset_ids", [])],
                "candidate_thesis": candidate.get("thesis"),
                "candidate_reason": candidate.get("model_grouping_reason"),
                "claims": c.get("claims"), "storyline_identity": c.get("storyline_identity")})
    calls = {}
    for t in raw.get("transport_attempts", []):
        stage = t["stage"]
        group = calls.setdefault(stage, {"calls": 0, "seconds": 0, "input_tokens": 0,
                                        "output_tokens": 0, "cost_cny_known": 0, "usage_unknown": 0})
        group["calls"] += 1
        group["seconds"] += t.get("duration_seconds", 0)
        usage = t.get("usage")
        if usage is None:
            group["usage_unknown"] += 1
        else:
            for key in ("input_tokens", "output_tokens"):
                group[key] += usage[key]
            group["cost_cny_known"] += usage["estimated_cost_cny"]
    obs = [{"asset": indices[o["source_asset_id"]], "id": o["id"],
            "status": o.get("status"), "event_kind": o.get("event_kind"), "salience": o.get("event_salience"),
            "facts": o.get("facts"), "field_degradation": o.get("field_degradation")} for o in observations.values()]
    brief = {"pack": pack, "status": raw.get("status"), "source_result_sha256": hashlib.sha256((path / "codex_full_run.json").read_bytes()).hexdigest(),
             "candidate_sha256": raw["candidate_sha256"], "asset_count": len(indices),
             "frame_count": sum(len(a["frames"]) for a in manifest["assets"]),
             "chapter_count": len(result.get("chapters", [])), "aha_count": len(result.get("ahas", [])),
             "seconds": raw.get("end_to_end_seconds"), "normalization_seconds": raw.get("normalization_seconds"),
             "cost_cny_known": raw.get("estimated_cost_cny_known"), "stages": calls,
             "editorial_order": trace.get("editorial_order"), "cards": cards, "observations": obs,
             "chapter_candidates": trace.get("chapter_candidates"), "aha_candidates": trace.get("aha_candidates"),
             "aha_selection": trace.get("aha_set_selection"), "chapter_selection": trace.get("chapter_set_selection"),
             "writer_items": trace.get("writer_items"), "blocked_memories": trace.get("blocked_memories"),
             "models": dict(Counter(t.get("provider_model") for t in raw.get("transport_attempts", []))),
             "semantic_quality_status": "REQUIRES_IMAGE_REVIEW_NOT_MECHANICALLY_SCORED"}
    target = path / "codex_mechanical_review.json"
    with target.open("x", encoding="utf-8") as stream:
        json.dump(brief, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return brief


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pack", choices=("1", "2", "3"))
    report = summarize(parser.parse_args().pack)
    print(json.dumps({k: report[k] for k in ("pack", "status", "asset_count", "frame_count", "chapter_count", "aha_count", "seconds", "cost_cny_known", "stages", "editorial_order")}, ensure_ascii=False))

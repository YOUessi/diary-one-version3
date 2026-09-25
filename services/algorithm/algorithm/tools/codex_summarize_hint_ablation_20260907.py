"""Summarize fixed real S07 outputs with existing reference checks, no model calls.

Grouping quality is deliberately not auto-scored. All raw groups remain visible,
including rejected proposals. No scenario-specific code is used for validation.
"""
import json
import sys
import uuid
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from diary_one_ci import x02
from diary_one_ci import codex_editorial_allocation as allocation
from diary_one_ci import codex_structure_wire as wire

AREA = ROOT / "var/codex_structure_hint_ablation_20260907"
OLD = ROOT / "var/codex_v1_68_2_experience_first_chapter_execution"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def summarize(slot):
    directory = AREA / ("slot_%02d" % slot["slot"])
    result = load(directory / "codex_result.json")
    old_dir = OLD / ("pack_%d/round_1" % slot["pack"])
    old = load(old_dir / "codex_full_run.json")["result"]
    manifest = load(old_dir / "codex_manifest.json")
    assets = {a["asset_id"]: a for a in manifest["assets"]}
    observation_by_id = {o["id"]: o for o in old["observations"]}
    order = {a["asset_id"]: a["sequence_index"] for a in manifest["assets"]}

    def material(observation_id):
        obs = observation_by_id.get(observation_id)
        if obs is None:
            return {"observation_id": observation_id, "reference_status": "UNKNOWN"}
        asset = assets[obs["source_asset_id"]]
        return {"observation_id": observation_id, "source_asset_id": obs["source_asset_id"],
                "import_index_one_based": asset["sequence_index"] + 1,
                "source_file": asset["source_display_name"],
                "facts": obs["facts"], "all_frames": asset["frames"]}

    summary = {k: v for k, v in result.items() if k != "output"}
    if not isinstance(result.get("output"), dict):
        return summary
    normalized, wire_audit = wire.normalize_output(result["output"])
    namespace = uuid.UUID(old["session_id"])
    roles = old["decision_trace"]["observation_roles"]
    chapters, chapter_ledger = x02._build_storyline_candidates(
        namespace, old["observations"], roles, old["moments"], normalized, order)
    ahas, aha_ledger = x02._build_aha_candidates(
        namespace, old["observations"], roles, old["moments"], normalized, order, value_first=True)
    plan = allocation.compile_relations(normalized, chapters, chapter_ledger, ahas)
    eligible_aha_ids = {c["observation_id"] for c in ahas}
    raw_chapters = result["output"].get("storyline_proposals", [])
    summary.update(
        groups=[{**c, "members": [{**b, "material": material(b.get("observation_id"))}
                                  for b in c.get("beat_map", [])]}
                for c in raw_chapters],
        native_ahas=[{**a, "material": material(a.get("observation_id"))}
                     for a in result["output"].get("aha_proposals", [])],
        chapter_reference_ledger=chapter_ledger,
        aha_reference_ledger=aha_ledger,
        relation_plan=plan,
        wire_audit=wire_audit,
        valid_chapter_candidates=len(chapters),
        valid_aha_candidates=len(ahas),
        membership_relation_coverage=[{
            "chapter_key": c.get("key"),
            "eligible_member_observation_ids": [b.get("observation_id") for b in c.get("beat_map", [])
                                                  if b.get("observation_id") in eligible_aha_ids],
            "missing_member_relation_ids": [b.get("observation_id") for b in c.get("beat_map", [])
                                            if b.get("observation_id") in eligible_aha_ids
                                            and b.get("observation_id") not in {r.get("observation_id") for r in c.get("aha_relations", [])}],
        } for c in raw_chapters],
        qualification="Existing reference checks only; no Chapter set, S10, Writer or publication rerun; candidate counts are not output card counts.",
    )
    return summary


def main():
    execution = load(AREA / "codex_execution_summary.json")
    summaries = [summarize(slot) for slot in execution["results"]]
    path = AREA / "codex_structure_review.json"
    with path.open("x", encoding="utf-8") as stream:
        json.dump({"scope": "S07_REAL_DIAGNOSTIC_NOT_USER_LABELS", "slots": summaries}, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    for slot in summaries:
        print(json.dumps({k: slot.get(k) for k in ("slot", "pack", "condition", "repeat", "status", "valid_chapter_candidates", "valid_aha_candidates")}, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""Freeze the opt-in D2 implementation after local checks. No API or extraction."""

import ast
import io
import shutil
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from codex_freeze_s07_research_v1_69 import inventory, load, require, save, sha

AREA = ROOT / "var/codex_v1_71_recording_editor"
PRIOR = ROOT / "var/codex_v1_70_editorial_order"
PRIOR_SHA = "282299e31ccd59abd3a3e208dc1be1d6f9cefdebd616b46d1df68c6d085e3ef9"
CHANGED = "src/diary_one_ci/x02.py"
ADDITIONS = {"src/diary_one_ci/codex_recording_editor.py", "src/diary_one_ci/codex_d2_research.py"}
FUNCTIONS = {"run_x02_v041", "_run_x02_with_policy", "_run_x02_impl",
             "_storyline_structure_prompt", "_build_aha_candidates"}


def freeze():
    require(not AREA.exists(), "Never overwrite a candidate checkpoint")
    require(sha(PRIOR / "codex_candidate.json") == PRIOR_SHA, "V1.70 candidate drift")
    baseline = load(PRIOR / "codex_candidate.json")
    require(inventory(PRIOR / "codex_candidate_runtime") == baseline["source_sha256"], "Frozen V1.70 drift")
    current = inventory(ROOT)
    require(set(current) - set(baseline["source_sha256"]) == ADDITIONS, "Unexpected new runtime source")
    require({k: v for k, v in current.items() if k not in ADDITIONS and k != CHANGED} ==
            {k: v for k, v in baseline["source_sha256"].items() if k != CHANGED}, "Out-of-scope source changes")
    trees = [ast.parse(p.read_text()) for p in (PRIOR / "codex_candidate_runtime" / CHANGED, ROOT / CHANGED)]
    funcs = [{n.name: ast.dump(n) for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))} for tree in trees]
    require(set(funcs[0]) == set(funcs[1]), "Unexpected x02 function addition/removal")
    require({k for k in funcs[0] if funcs[0][k] != funcs[1][k]} == FUNCTIONS, "Unexpected x02 behavior change")
    other = [[ast.dump(n) for n in tree.body if not isinstance(n, (ast.FunctionDef, ast.ClassDef))
              and not (isinstance(n, ast.ImportFrom) and any(a.name == "codex_recording_editor" for a in n.names))]
             for tree in trees]
    require(other[0] == other[1], "Unexpected constants or imports changed")
    d2 = load(ROOT / "var/codex_d2_whole_day_editorial_design_v01/codex_design_checkpoint.json")
    design = "docs/codex_D2_WHOLE_DAY_EDITORIAL_DESIGN_V01.md"
    require(sha(ROOT / design) == d2["artifacts_sha256"][design], "Accepted D2 design changed")
    tests = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / "tests").rglob("*"))
             if p.suffix in (".py", ".json")}
    archives = {p.relative_to(ROOT).as_posix(): sha(p)
                for p in sorted((ROOT / "var/codex_v1_70_full_chain_execution").glob("pack_*/round_1/**/*.json"))}
    require(archives, "Real replay inputs unavailable")
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=1).run(
        unittest.defaultTestLoader.discover(str(ROOT / "tests")))
    print(output.getvalue(), end="")
    require(result.wasSuccessful(), "Local regression failed")
    require(not any("RecordingEditorTests" in t.id() for t, _ in result.skipped), "D2 real replay checks skipped")
    require(inventory(ROOT) == current, "Runtime changed during checks")
    for name, digest in {**tests, **archives}.items():
        require(sha(ROOT / name) == digest, "Tests or archived records changed during checks")
    AREA.mkdir()
    destination = AREA / "codex_candidate_runtime"
    for name in current:
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, path)
    require(inventory(destination) == current, "Frozen copy mismatch")
    sys.path.insert(0, str(ROOT / "tests"))
    from test_codex_recording_editor import record
    scope_counts = {}
    for pack in (1, 2, 3):
        r = record(pack)
        scope_counts[str(pack)] = {"old_consideration_scope": len(r["request"]["context"]["aha_relation_scope"]),
                                   "new_consideration_scope": len(r["scope"]),
                                   "meaning": "ELIGIBILITY_ONLY_NOT_NEW_QUALITY_OR_RECOMMENDED_COUNT"}
    save(AREA / "codex_local_checks.json", {
        "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "skipped": [{"test": t.id(), "reason": reason} for t, reason in result.skipped],
        "d2_test_methods": 13, "d2_real_pack_function_replays": 3, "d2_mock_transport_calls": 50,
        "single_real_asset_component_check": "NOT_A_REAL_SHORT_WEAR_DAY_OR_NEW_MODEL_RUN",
        "aha_consideration_scope_counts": scope_counts,
        "actual_external_calls": 0, "new_quality_status": "NOT_TESTED",
        "test_files_sha256": tests, "archived_replay_inputs_sha256": archives,
        "protocol_mutations": "CONTROLLED_SELECTION_IDS_AND_FIELD_SHAPES_NOT_SYNTHETIC_SEMANTIC_ERRORS",
    })
    from diary_one_ci import codex_d2_research as research
    save(AREA / "codex_candidate.json", {
        "algorithm_candidate": "V1.71", "created_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": current, "baseline_candidate_sha256": PRIOR_SHA,
        "baseline_differences": [CHANGED, *sorted(ADDITIONS)], "baseline_existing_files_unchanged": 45,
        "changed_x02_functions": sorted(FUNCTIONS), "research_profile": research.profile(),
        "full_function_entry": "diary_one_ci.codex_d2_research.run_research",
        "gateway_factory": "diary_one_ci.codex_d2_research.make_gateway",
        "freeze_tool_sha256": sha(Path(__file__)), "local_checks_sha256": sha(AREA / "codex_local_checks.json"),
        "accepted_design_sha256": sha(ROOT / design),
        "implementation_checkpoint_sha256": sha(ROOT / "docs/codex_CHECKPOINT_V1_71_RECORDING_EDITOR.md"),
        "read_first_sha256": sha(ROOT / "docs/00_READ_FIRST.md"),
        "quality_status": "LOCAL_IMPLEMENTATION_ONLY_FRESH_REAL_CHAIN_NOT_RUN",
        "future_run": {"packs": [1, 2, 3], "rounds_each": 1, "fresh_decode_and_extraction": True,
                       "fresh_perception": True, "cross_run_semantic_cache": False,
                       "same_candidate_all_packs": True, "feedback_after_each_pack": True,
                       "pipeline_scope": "NORMALIZATION_AND_S04_S12_NOT_S13",
                       "next_stage_not_launched_by_freeze": True},
        "unchanged": ["S04_MODEL_AND_INPUT", "CHAPTER_THREE_MEDIA_FLOOR", "INHERITED_COUNTS",
                      "UNRESOLVED_RELATIONS_NOT_A_NEW_HARD_GATE", "S10", "WRITER",
                      "WEB_APP_DEFAULTS", "V1_70_RESEARCH_ENTRY", "GPS_AND_INCREMENTAL_TRIGGER"],
        "exclusions": ["WEB_SWITCH", "APP_R2", "FIRMWARE_SDK", "SHARED_STATE", "PUBLIC_SYNC", "LONG_TERM_MEMORY"],
    })
    print("V1.71 local candidate frozen; API 0; SHA-256 " + sha(AREA / "codex_candidate.json"))


if __name__ == "__main__":
    freeze()

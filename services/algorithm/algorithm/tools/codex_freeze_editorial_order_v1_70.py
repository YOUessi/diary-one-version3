"""Freeze D1 after local regression. No API, extraction or deployment."""
import ast
import io
import json
import shutil
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from codex_freeze_s07_research_v1_69 import inventory, load, require, save, sha

PRIOR = ROOT / "var/codex_v1_69_s07_plus_short_refs"
PRIOR_SHA = "a92f528b8ccc50e3d39db380d2e93bc5d187aebb3f9e78e069c331b782d261e8"
AREA = ROOT / "var/codex_v1_70_editorial_order"
CHANGED = "src/diary_one_ci/x02.py"
ADDITIONS = {"src/diary_one_ci/codex_editorial_order.py", "src/diary_one_ci/codex_d1_research.py"}
ALLOWED_FUNCTIONS = {"run_x02_v041", "_run_x02_with_policy", "_run_x02_impl",
                     "_storyline_structure_prompt", "_select_storyline_set", "_select_aha_set"}


def freeze():
    require(not AREA.exists(), "Never overwrite a frozen checkpoint")
    require(sha(PRIOR / "codex_candidate.json") == PRIOR_SHA, "Prior candidate drift")
    baseline = load(PRIOR / "codex_candidate.json")
    require(inventory(PRIOR / "codex_candidate_runtime") == baseline["source_sha256"], "Archived source drift")
    current = inventory(ROOT)
    require(set(current) - set(baseline["source_sha256"]) == ADDITIONS, "Unexpected added source")
    require({k: v for k, v in current.items() if k not in ADDITIONS and k != CHANGED} ==
            {k: v for k, v in baseline["source_sha256"].items() if k != CHANGED}, "Out-of-scope source change")
    trees = [ast.parse(p.read_text()) for p in (PRIOR / "codex_candidate_runtime" / CHANGED, ROOT / CHANGED)]
    funcs = [{n.name: ast.dump(n) for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
             for tree in trees]
    require(set(funcs[0]) == set(funcs[1]), "Unexpected x02 function addition/removal")
    changed_functions = {k for k in funcs[0] if funcs[0][k] != funcs[1][k]}
    require(changed_functions == ALLOWED_FUNCTIONS, "Unexpected x02 function change")
    tests = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / "tests").rglob("*"))
             if p.suffix in (".py", ".json")}
    replay_pins = {p.relative_to(ROOT).as_posix(): sha(p)
                   for p in sorted((ROOT / "var/codex_v1_69_full_chain_execution").glob("pack_*/round_1/**/*.json"))}
    output = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(stream=output, verbosity=1).run(suite)
    print(output.getvalue(), end="")
    require(result.wasSuccessful(), "Local tests failed")
    require(not any("EditorialOrderTests" in t.id() for t, _ in result.skipped), "D1 real replay checks skipped")
    require(inventory(ROOT) == current, "Source changed during verification")
    for name, digest in {**tests, **replay_pins}.items():
        require(sha(ROOT / name) == digest, "Tests or archived real inputs drifted")
    AREA.mkdir()
    destination = AREA / "codex_candidate_runtime"
    for name in current:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    require(inventory(destination) == current, "Frozen snapshot differs")
    save(AREA / "codex_local_checks.json", {
        "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "skipped": [{"test": t.id(), "reason": reason} for t, reason in result.skipped],
        "new_test_methods": 7, "three_pack_offline_chains": 3, "replayed_transport_calls": 53,
        "actual_external_calls": 0, "new_model_quality": "NOT_TESTED",
        "protocol_test_order": "ARCHIVED_ORDER_AND_REVERSAL_FOR_WIRING_ONLY_NOT_SEMANTIC_LABELS",
        "test_files_sha256": tests, "real_replay_files_sha256": replay_pins,
    })
    from diary_one_ci import codex_d1_research as research
    save(AREA / "codex_candidate.json", {
        "algorithm_candidate": "V1.70", "created_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": current, "baseline_candidate_sha256": PRIOR_SHA,
        "baseline_differences": [CHANGED, *sorted(ADDITIONS)], "baseline_existing_files_unchanged": 43,
        "changed_x02_functions": sorted(changed_functions), "research_profile": research.profile(),
        "full_function_entry": "diary_one_ci.codex_d1_research.run_research",
        "gateway_factory": "diary_one_ci.codex_d1_research.make_gateway",
        "freeze_tool_sha256": sha(Path(__file__)), "local_checks_sha256": sha(AREA / "codex_local_checks.json"),
        "approved_design_sha256": sha(ROOT / "docs/codex_D1_EXPERIENCE_SELECTION_AND_AHA_DRAFT.md"),
        "quality_status": "LOCAL_IMPLEMENTATION_ONLY_FRESH_REAL_CHAIN_NOT_RUN",
        "future_run": {"packs": [1, 2, 3], "rounds_each": 1, "fresh_decode_and_extraction": True,
                       "fresh_perception": True, "cross_run_semantic_cache": False,
                       "feedback_after_each_pack": True, "same_candidate_all_packs": True,
                       "pipeline_scope": "NORMALIZATION_AND_EXISTING_S04_S12_NOT_S13",
                       "start_requires_next_stage": True},
        "unchanged": ["S04_MODEL_AND_INPUT", "AHA_ELIGIBILITY", "CHAPTER_THREE_MEDIA_FLOOR",
                      "SAME_STORY_AND_UNRESOLVED_POLICY", "S10_INPUT_AND_SELECTION", "WRITER"],
        "exclusions": ["WEB_DEFAULT_SWITCH", "APP_R2", "FIRMWARE_SDK", "SHARED_STATE", "PUBLIC_DEPLOYMENT"],
    })
    print(json.dumps({"event": "V1_70_FROZEN_LOCAL_ONLY", "source_files": len(current),
                      "tests": result.testsRun, "skipped": len(result.skipped), "external_calls": 0,
                      "candidate_sha256": sha(AREA / "codex_candidate.json")}))


if __name__ == "__main__":
    freeze()

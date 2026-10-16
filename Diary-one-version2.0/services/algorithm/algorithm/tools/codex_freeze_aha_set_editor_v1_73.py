"""Freeze V1.73 after local checks. No API, extraction, Web, or deployment."""

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
sys.path.insert(0, str(ROOT / "tools"))
from codex_freeze_s07_research_v1_69 import inventory, load, require, save, sha


AREA = ROOT / "var/codex_v1_73_aha_set_editor"
PRIOR = ROOT / "var/codex_v1_72_1_focus_frame_writer_exit"
PRIOR_SHA = "97d5b36efbc0b9e59369fe14b3904f7008f925bf3f5b2cec421137208dd8715c"
PRIOR_REAL_RUN = ROOT / "var/codex_v1_72_1_full_chain_execution/pack_1/round_1/codex_full_run.json"
PRIOR_REAL_RUN_SHA = "bb84ea3be572ccffb1d47bda8283895fd2e30263c7eda3a43bcdee4f17a8bf70"
ADDED = {
    "src/diary_one_ci/codex_aha_set_editor.py",
    "src/diary_one_ci/codex_d4_research.py",
}
CHANGED = {
    "src/diary_one_ci/codex_grounded_recording_editor.py",
    "src/diary_one_ci/x02.py",
}
EXPECTED_FUNCTION_CHANGES = {
    "src/diary_one_ci/x02.py": {"_run_x02_impl", "_storyline_structure_prompt"},
    "src/diary_one_ci/codex_grounded_recording_editor.py": {"execute_plan"},
}
CHECKPOINT = "docs/codex_CHECKPOINT_V1_73_AHA_SET_EDITOR.md"
DESIGN = "docs/codex_D4_AHA_SET_EDITOR_DESIGN_V01.md"


def top_level_functions(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name: ast.dump(node)
        for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))
    }


def top_level_non_import_behavior(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [
        ast.dump(node) for node in tree.body
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom))
    ]


def freeze():
    require(not AREA.exists(), "Never overwrite a candidate checkpoint")
    require(sha(PRIOR / "codex_candidate.json") == PRIOR_SHA, "V1.72.1 candidate drift")
    require(sha(PRIOR_REAL_RUN) == PRIOR_REAL_RUN_SHA, "V1.72.1 real result drift")
    baseline = load(PRIOR / "codex_candidate.json")
    require(
        inventory(PRIOR / "codex_candidate_runtime") == baseline["source_sha256"],
        "Frozen V1.72.1 runtime drift",
    )
    current = inventory(ROOT)
    require(set(current) == set(baseline["source_sha256"]) | ADDED,
            "V1.73 runtime file scope drift")
    require({
        name for name in baseline["source_sha256"]
        if current[name] != baseline["source_sha256"][name]
    } == CHANGED, "Out-of-scope existing runtime source change")

    changed_functions = {}
    for name, expected in EXPECTED_FUNCTION_CHANGES.items():
        old_path = PRIOR / "codex_candidate_runtime" / name
        new_path = ROOT / name
        old, new = top_level_functions(old_path), top_level_functions(new_path)
        require(set(old) == set(new), "Unexpected function/class addition or removal in " + name)
        actual = {key for key in old if old[key] != new[key]}
        require(actual == expected, "Unexpected behavior change in " + name)
        require(
            top_level_non_import_behavior(old_path) == top_level_non_import_behavior(new_path),
            "Unexpected constants or executable top-level behavior changed in " + name,
        )
        changed_functions[name] = sorted(actual)

    tests = {
        path.relative_to(ROOT).as_posix(): sha(path)
        for path in sorted((ROOT / "tests").rglob("*"))
        if path.suffix in (".py", ".json")
    }
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=1).run(
        unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    )
    print(output.getvalue(), end="")
    require(result.wasSuccessful(), "Local regression failed")
    require(not any("AhaSetEditorTests" in test.id() for test, _ in result.skipped),
            "V1.73 protocol tests skipped")
    require(inventory(ROOT) == current, "Runtime changed during checks")
    for name, digest in tests.items():
        require(sha(ROOT / name) == digest, "Test input changed during checks")

    AREA.mkdir()
    destination = AREA / "codex_candidate_runtime"
    for name in current:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    require(inventory(destination) == current, "Frozen copy mismatch")

    from diary_one_ci import codex_aha_set_editor as editor
    from diary_one_ci import codex_d4_research as research
    save(AREA / "codex_local_checks.json", {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": [{"test": test.id(), "reason": reason}
                    for test, reason in result.skipped],
        "v1_73_protocol_test_methods": 11,
        "v1_73_full_x02_integration_tests": 1,
        "actual_external_calls": 0,
        "new_real_quality_status": "NOT_TESTED",
        "synthetic_image_semantic_errors": 0,
        "protocol_fixtures_meaning": "REFERENCE_AND_EXECUTION_CHECKS_ONLY_NOT_SEMANTIC_GOLD",
        "s09_model_calls_per_nonempty_shortlist": 1,
        "s09_retries": 0,
        "automatic_aha_fill": False,
        "aha_count_minimum": 0,
        "aha_count_maximum": editor.MAX_AHAS,
        "test_files_sha256": tests,
    })
    save(AREA / "codex_candidate.json", {
        "algorithm_candidate": "V1.73",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": current,
        "baseline_candidate_sha256": PRIOR_SHA,
        "baseline_real_run_sha256": PRIOR_REAL_RUN_SHA,
        "baseline_added_files": sorted(ADDED),
        "baseline_modified_files": sorted(CHANGED),
        "baseline_existing_files_unchanged": len(baseline["source_sha256"]) - len(CHANGED),
        "changed_functions": changed_functions,
        "research_profile": research.profile(),
        "full_function_entry": "diary_one_ci.codex_d4_research.run_research",
        "gateway_factory": "diary_one_ci.codex_d4_research.make_gateway",
        "freeze_tool_sha256": sha(Path(__file__)),
        "local_checks_sha256": sha(AREA / "codex_local_checks.json"),
        "implementation_checkpoint_sha256": sha(ROOT / CHECKPOINT),
        "confirmed_design_sha256": sha(ROOT / DESIGN),
        "quality_status": "LOCAL_IMPLEMENTATION_ONLY_FRESH_REAL_CHAIN_NOT_RUN",
        "contracts": {
            "s07_aha_shortlist_maximum": editor.SHORTLIST_MAX,
            "s09_editor": "ONE_TEXT_ONLY_PLUS_CALL_WHEN_SHORTLIST_NONEMPTY",
            "candidate_review_states": list(editor.REVIEW_STATUSES),
            "aha_count_range": [0, editor.MAX_AHAS],
            "active_quality_target": "TWO_TO_THREE_WHEN_SUPPORTED",
            "no_chapter_aha_capacity": editor.MAX_AHAS,
            "selected_chapter_aha_pairs": "EXACTLY_ONE_RELATION_EACH",
            "selected_aha_aha_pairs": "EXACTLY_ONE_RELATION_EACH",
            "same_theme_coexistence": "ONLY_WITH_DIFFERENT_RECALL_EXPERIENCE_DUTIES",
            "editor_retries": 0,
            "automatic_fill": False,
            "aha_moment": "ONE_FACT_ONE_VALIDATED_FOCUS_FRAME",
            "writer_policy": "UNCHANGED_V1_72_1_SINGLE_PASS_20_TARGET_24_HARD_MAX",
        },
        "future_run": {
            "packs": [1, 2, 3], "rounds_each": 1,
            "fresh_decode_and_extraction": True, "fresh_perception": True,
            "cross_run_semantic_cache": False, "same_candidate_all_packs": True,
            "feedback_after_each_pack": True,
            "pipeline_scope": "NORMALIZATION_AND_S04_S12_NOT_S13",
            "next_stage_not_launched_by_freeze": True,
        },
        "unchanged": [
            "CHAPTER_GROUPING_CONTRACT", "CHAPTER_THREE_TO_FIVE_MEDIA",
            "S04_FACT_CONTRACT", "S10_MEDIA_CONTRACT", "V1_72_1_WRITER_CONTRACT",
            "S13_NOT_EXECUTED", "WEB_APP_DEFAULTS", "V1_72_1_FROZEN_EVIDENCE",
            "GPS_AND_INCREMENTAL_TRIGGER",
        ],
        "exclusions": [
            "WEB_SWITCH", "APP_R2", "FIRMWARE_SDK", "SHARED_STATE",
            "PUBLIC_SYNC", "LONG_TERM_MEMORY", "SCENE_SPECIFIC_RULES",
            "SYNTHETIC_IMAGE_ERROR_GATES", "API_REDRAW_OR_RETRY",
        ],
    })
    print("V1.73 local candidate frozen; API 0; SHA-256 "
          + sha(AREA / "codex_candidate.json"))


if __name__ == "__main__":
    freeze()


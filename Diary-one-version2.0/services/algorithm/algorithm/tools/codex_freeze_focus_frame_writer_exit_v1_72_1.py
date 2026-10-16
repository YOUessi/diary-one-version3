"""Freeze V1.72.1 after local checks. No API, extraction, Web, or deployment."""

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


AREA = ROOT / "var/codex_v1_72_1_focus_frame_writer_exit"
PRIOR = ROOT / "var/codex_v1_72_relation_atomic_writer"
PRIOR_SHA = "3331f744fac44653bf75da7360714d296e0f771ac96253256380d5337b3c9be2"
PRIOR_REAL_RUN = ROOT / "var/codex_v1_72_full_chain_execution/pack_1/round_1/codex_full_run.json"
PRIOR_REAL_RUN_SHA = "5e16e8822ae62585bb63c4c45b55816683fb7c3c5f7aab7be9ca70937236ef3b"
CHANGED = {
    "src/diary_one_ci/codex_grounded_recording_editor.py",
    "src/diary_one_ci/codex_d3_research.py",
    "src/diary_one_ci/x02.py",
}
X02_CHANGED = {
    "_run_x02_impl", "_storyline_structure_prompt", "_validate_writer_output",
    "_writer_context", "_writer_retry_context",
}
X02_ADDED = {"_writer_fallback_ids"}
CHECKPOINT = "docs/codex_CHECKPOINT_V1_72_1_FOCUS_FRAME_WRITER_EXIT.md"
REAL_REVIEW = "docs/codex_V1_72_PACK_1_REAL_REVIEW.md"


def freeze():
    require(not AREA.exists(), "Never overwrite a candidate checkpoint")
    require(sha(PRIOR / "codex_candidate.json") == PRIOR_SHA, "V1.72 candidate drift")
    require(sha(PRIOR_REAL_RUN) == PRIOR_REAL_RUN_SHA, "V1.72 real result drift")
    baseline = load(PRIOR / "codex_candidate.json")
    require(inventory(PRIOR / "codex_candidate_runtime") == baseline["source_sha256"],
            "Frozen V1.72 runtime drift")
    current = inventory(ROOT)
    require(set(current) == set(baseline["source_sha256"]),
            "V1.72.1 may not add or remove runtime source files")
    require({name for name in current if current[name] != baseline["source_sha256"][name]}
            == CHANGED, "Out-of-scope runtime source change")

    old_path = PRIOR / "codex_candidate_runtime/src/diary_one_ci/x02.py"
    trees = [ast.parse(path.read_text(encoding="utf-8"))
             for path in (old_path, ROOT / "src/diary_one_ci/x02.py")]
    functions = [{node.name: ast.dump(node) for node in tree.body
                  if isinstance(node, (ast.FunctionDef, ast.ClassDef))} for tree in trees]
    require(set(functions[1]) - set(functions[0]) == X02_ADDED,
            "Unexpected x02 function addition")
    require(set(functions[0]) - set(functions[1]) == set(),
            "Unexpected x02 function removal")
    changed_functions = {
        name for name in set(functions[0]) & set(functions[1])
        if functions[0][name] != functions[1][name]
    }
    require(changed_functions == X02_CHANGED, "Unexpected x02 behavior change")
    other = [[ast.dump(node) for node in tree.body
              if not isinstance(node, (ast.FunctionDef, ast.ClassDef))]
             for tree in trees]
    require(other[0] == other[1], "Unexpected x02 constants or imports changed")

    tests = {path.relative_to(ROOT).as_posix(): sha(path)
             for path in sorted((ROOT / "tests").rglob("*"))
             if path.suffix in (".py", ".json")}
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=1).run(
        unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    )
    print(output.getvalue(), end="")
    require(result.wasSuccessful(), "Local regression failed")
    require(not any("GroundedRecordingEditorTests" in test.id()
                    for test, _ in result.skipped), "V1.72.1 protocol tests skipped")
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

    from diary_one_ci import codex_d3_research as research
    from diary_one_ci import codex_grounded_recording_editor as editor
    save(AREA / "codex_local_checks.json", {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": [{"test": test.id(), "reason": reason}
                    for test, reason in result.skipped],
        "v1_72_1_protocol_test_methods": 11,
        "actual_external_calls": 0,
        "new_real_quality_status": "NOT_TESTED",
        "synthetic_image_semantic_errors": 0,
        "protocol_fixtures_meaning": "REFERENCE_AND_EXIT_CHECKS_ONLY_NOT_SEMANTIC_GOLD",
        "writer_model_calls_per_full_run": 1,
        "writer_model_rewrite_calls": 0,
        "grounded_aha_deterministic_fallback": "FORBIDDEN",
        "aha_writer_schema_max_length": editor.AHA_VISIBLE_MAX,
        "test_files_sha256": tests,
    })
    save(AREA / "codex_candidate.json", {
        "algorithm_candidate": "V1.72.1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": current,
        "baseline_candidate_sha256": PRIOR_SHA,
        "baseline_real_run_sha256": PRIOR_REAL_RUN_SHA,
        "baseline_differences": sorted(CHANGED),
        "baseline_existing_files_unchanged": len(current) - len(CHANGED),
        "changed_x02_functions": sorted(changed_functions),
        "added_x02_functions": sorted(X02_ADDED),
        "research_profile": research.profile(),
        "full_function_entry": "diary_one_ci.codex_d3_research.run_research",
        "gateway_factory": "diary_one_ci.codex_d3_research.make_gateway",
        "freeze_tool_sha256": sha(Path(__file__)),
        "local_checks_sha256": sha(AREA / "codex_local_checks.json"),
        "implementation_checkpoint_sha256": sha(ROOT / CHECKPOINT),
        "superseding_real_review_sha256": sha(ROOT / REAL_REVIEW),
        "quality_status": "LOCAL_IMPLEMENTATION_ONLY_FRESH_REAL_CHAIN_NOT_RUN",
        "contracts": {
            "selected_chapter_aha_pairs": "EXACTLY_ONE_RELATION_EACH",
            "selected_aha_aha_pairs": "EXACTLY_ONE_RELATION_EACH",
            "aha_moment": "ONE_FACT_ONE_VALIDATED_FOCUS_FRAME",
            "aha_focus_source": "MODEL_AUTHORED_AND_REFERENCE_VALIDATED_NOT_PROGRAM_INFERRED",
            "aha_writer_target_visible_characters": editor.AHA_WRITING_TARGET,
            "aha_writer_hard_max_visible_characters": editor.AHA_VISIBLE_MAX,
            "writer_model": research.prior.PLUS,
            "writer_model_retries": 0,
            "grounded_aha_fallback": "NO_DETERMINISTIC_PUBLISH_PATH",
            "provider_constrained_decoding": "NOT_CLAIMED_JSON_OBJECT_MODE_PLUS_LOCAL_RELEASE_GATE",
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
            "CHAPTER_THREE_TO_FIVE_MEDIA", "INHERITED_DAILY_COUNT_CEILINGS",
            "S13_NOT_EXECUTED", "WEB_APP_DEFAULTS", "V1_72_FROZEN_EVIDENCE",
            "GPS_AND_INCREMENTAL_TRIGGER",
        ],
        "exclusions": [
            "WEB_SWITCH", "APP_R2", "FIRMWARE_SDK", "SHARED_STATE",
            "PUBLIC_SYNC", "LONG_TERM_MEMORY", "SCENE_SPECIFIC_RULES",
            "SYNTHETIC_IMAGE_ERROR_GATES", "API_WRITER_REDRAW",
        ],
    })
    print("V1.72.1 local candidate frozen; API 0; SHA-256 "
          + sha(AREA / "codex_candidate.json"))


if __name__ == "__main__":
    freeze()

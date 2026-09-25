"""Freeze V1.74 after local checks. No API, extraction, Web, or deployment."""

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


AREA = ROOT / "var/codex_v1_74_experience_editor_safe_exit"
PRIOR = ROOT / "var/codex_v1_73_aha_set_editor"
PRIOR_SHA = "e1ae4fcbfb587562238cd9635f84d9b7599f645924ee38b4b12ae6e91c181ec2"
PRIOR_REAL_RUN = ROOT / "var/codex_v1_73_full_chain_execution/pack_1/round_1/codex_full_run.json"
PRIOR_REAL_RUN_SHA = "21e933082d9cea78d6d7c81b5200b371762c6f3164122ba8daddf80d3af41808"
ADDED = {
    "src/diary_one_ci/codex_experience_editor.py",
    "src/diary_one_ci/codex_v174_writer.py",
    "src/diary_one_ci/codex_d5_research.py",
}
CHANGED = {"src/diary_one_ci/x02.py"}
EXPECTED_FUNCTION_CHANGES = {
    "src/diary_one_ci/x02.py": {
        "_run_x02_impl", "_perception_prompt", "_validate_perception_batch",
        "_validated_observation", "_storyline_structure_prompt", "_fixture_perception",
    },
}
CHECKPOINT = "docs/codex_CHECKPOINT_V1_74_EXPERIENCE_EDITOR_SAFE_EXIT.md"
DESIGN = "docs/codex_D5_V1_74_EXPERIENCE_EDITOR_AND_SAFE_WRITER_EXIT_DESIGN_V01.md"


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
    require(sha(PRIOR / "codex_candidate.json") == PRIOR_SHA, "V1.73 candidate drift")
    require(sha(PRIOR_REAL_RUN) == PRIOR_REAL_RUN_SHA, "V1.73 real result drift")
    baseline = load(PRIOR / "codex_candidate.json")
    require(
        inventory(PRIOR / "codex_candidate_runtime") == baseline["source_sha256"],
        "Frozen V1.73 runtime drift",
    )
    current = inventory(ROOT)
    require(set(current) == set(baseline["source_sha256"]) | ADDED,
            "V1.74 runtime file scope drift")
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
    require(not any("ExperienceEditorTests" in test.id() or "V174IntegrationTests" in test.id()
                    for test, _ in result.skipped), "V1.74 protocol tests skipped")
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

    from diary_one_ci import codex_d5_research as research
    from diary_one_ci import codex_experience_editor as editor
    from diary_one_ci import codex_v174_writer as writer
    save(AREA / "codex_local_checks.json", {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": [{"test": test.id(), "reason": reason}
                    for test, reason in result.skipped],
        "v1_74_protocol_and_integration_test_methods": 9,
        "actual_external_calls": 0,
        "new_real_quality_status": "NOT_TESTED",
        "synthetic_image_semantic_errors": 0,
        "protocol_fixtures_meaning": "REFERENCE_AND_EXECUTION_CHECKS_ONLY_NOT_SEMANTIC_GOLD",
        "s09_model_calls_when_fact_palette_nonempty": 1,
        "s09_retries": 0,
        "writer_model_calls": 1,
        "writer_retries": 0,
        "deterministic_copy_fallback": False,
        "automatic_aha_fill": False,
        "aha_count_minimum": 0,
        "aha_count_maximum": editor.MAX_AHAS,
        "writer_exit_policy": writer.POLICY_VERSION,
        "test_files_sha256": tests,
    })
    save(AREA / "codex_candidate.json", {
        "algorithm_candidate": "V1.74",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": current,
        "baseline_candidate_sha256": PRIOR_SHA,
        "baseline_real_run_sha256": PRIOR_REAL_RUN_SHA,
        "baseline_added_files": sorted(ADDED),
        "baseline_modified_files": sorted(CHANGED),
        "baseline_existing_files_unchanged": len(baseline["source_sha256"]) - len(CHANGED),
        "changed_functions": changed_functions,
        "research_profile": research.profile(),
        "full_function_entry": "diary_one_ci.codex_d5_research.run_research",
        "gateway_factory": "diary_one_ci.codex_d5_research.make_gateway",
        "freeze_tool_sha256": sha(Path(__file__)),
        "local_checks_sha256": sha(AREA / "codex_local_checks.json"),
        "implementation_checkpoint_sha256": sha(ROOT / CHECKPOINT),
        "confirmed_design_sha256": sha(ROOT / DESIGN),
        "quality_status": "LOCAL_IMPLEMENTATION_ONLY_FRESH_REAL_CHAIN_NOT_RUN",
        "contracts": {
            "s04_fact_representative_frame": "REQUIRED_AND_MUST_BELONG_TO_FACT_EVIDENCE",
            "invalid_representative_action": "RETAIN_FACT_EXCLUDE_ONLY_FROM_AHA",
            "s07": "CHAPTER_ONLY_EMPTY_AHA_OUTPUT",
            "s09_input": "ALL_USABLE_SUPPORTED_FACTS_WITH_VALID_REPRESENTATIVE",
            "s09_editor": "ONE_TEXT_ONLY_PLUS_CALL",
            "s09_finalists_maximum": editor.MAX_FINALISTS,
            "intrinsic_states": list(editor.INTRINSIC_VALUES),
            "aha_count_range": [0, editor.MAX_AHAS],
            "active_quality_target": "TWO_TO_THREE_WHEN_SUPPORTED",
            "selected_chapter_aha_pairs": "EXACTLY_ONE_AUTHORITATIVE_RELATION_EACH",
            "selected_aha_aha_pairs": "EXACTLY_ONE_AUTHORITATIVE_RELATION_EACH",
            "editor_retries": 0,
            "automatic_fill": False,
            "aha_moment": "ONE_FACT_ONE_S04_REPRESENTATIVE_FRAME",
            "writer_references": "REQUEST_LOCAL_SHORT_IDS_PRIVATE_MAP",
            "writer_policy": writer.POLICY_VERSION,
            "writer_calls": 1,
            "writer_fallback": "FORBIDDEN",
            "chapter_copy_failure": "INTERNAL_MEDIA_LEDGER_NOT_PUBLIC_COPY",
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
            "S10_CHAPTER_MEDIA_CONTRACT", "AHA_20_TARGET_24_HARD_MAX",
            "S13_NOT_EXECUTED", "WEB_APP_DEFAULTS", "V1_73_FROZEN_EVIDENCE",
            "GPS_AND_INCREMENTAL_TRIGGER",
        ],
        "exclusions": [
            "WEB_SWITCH", "APP_R2", "FIRMWARE_SDK", "SHARED_STATE",
            "PUBLIC_SYNC", "LONG_TERM_MEMORY", "SCENE_SPECIFIC_RULES",
            "SYNTHETIC_IMAGE_ERROR_GATES", "API_REDRAW_OR_RETRY",
            "HIGH_INTENSITY_CONTEXT_CAP_NOT_YET_EVIDENCE_VALIDATED",
        ],
    })
    print("V1.74 local candidate frozen; API 0; SHA-256 "
          + sha(AREA / "codex_candidate.json"))


if __name__ == "__main__":
    freeze()

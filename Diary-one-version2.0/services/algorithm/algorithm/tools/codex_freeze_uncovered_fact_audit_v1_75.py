"""Freeze V1.75 after local checks. No API, extraction, Web, or deployment."""

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


AREA = ROOT / "var/codex_v1_75_uncovered_fact_audit"
PRIOR = ROOT / "var/codex_v1_74_1_experience_editor_safe_exit"
PRIOR_SHA = "a613c4de30fdca8fa4d38c8c3bf66d5fac2f45cd021b66d8eb357052009bf96a"
PRIOR_REAL_RUN = ROOT / "var/codex_v1_74_1_full_chain_execution/pack_1/round_1/codex_full_run.json"
PRIOR_REAL_RUN_SHA = "43e4bdd77c01f4f1a267352b02c9ce32c25b1bd4ce83480115fd55377fbe7a89"
CHANGED = {
    "src/diary_one_ci/codex_experience_editor.py",
    "src/diary_one_ci/codex_d5_research.py",
}
EXPECTED_FUNCTION_CHANGES = {
    "src/diary_one_ci/codex_experience_editor.py": {
        "editor_input", "editor_response_schema", "editor_prompt", "compile_editor",
    },
    "src/diary_one_ci/codex_d5_research.py": {
        "profile", "ResearchGateway", "run_research",
    },
}
CHECKPOINT = "docs/codex_CHECKPOINT_V1_75_UNCOVERED_FACT_AUDIT.md"
DESIGN = "docs/codex_D5_V1_75_UNCOVERED_FACT_AUDIT_DESIGN_V01.md"


def top_level_functions(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name: ast.dump(node)
        for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))
    }


def freeze():
    require(not AREA.exists(), "Never overwrite a candidate checkpoint")
    require(sha(PRIOR / "codex_candidate.json") == PRIOR_SHA, "V1.74.1 candidate drift")
    require(sha(PRIOR_REAL_RUN) == PRIOR_REAL_RUN_SHA, "V1.74.1 real result drift")
    baseline = load(PRIOR / "codex_candidate.json")
    require(inventory(PRIOR / "codex_candidate_runtime") == baseline["source_sha256"],
            "Frozen V1.74.1 runtime drift")
    current = inventory(ROOT)
    require(set(current) == set(baseline["source_sha256"]), "V1.75 runtime file scope drift")
    actual_changed = {
        name for name in baseline["source_sha256"]
        if current[name] != baseline["source_sha256"][name]
    }
    require(actual_changed == CHANGED, "V1.75 changed unexpected runtime source")

    changed_functions = {}
    for name, expected in EXPECTED_FUNCTION_CHANGES.items():
        old = top_level_functions(PRIOR / "codex_candidate_runtime" / name)
        new = top_level_functions(ROOT / name)
        require(set(old) == set(new), "Unexpected function/class scope change in " + name)
        actual = {key for key in old if old[key] != new[key]}
        require(actual == expected, "Unexpected function/class behavior change in " + name)
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
    require(not any("V175" in test.id() or "ExperienceEditorTests" in test.id()
                    for test, _ in result.skipped), "V1.75 protocol tests skipped")
    require(inventory(ROOT) == current, "Runtime changed during checks")
    require(all(sha(ROOT / name) == digest for name, digest in tests.items()),
            "Test input changed during checks")

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
    profile = research.profile()
    require(profile["version"] == "CODEX_V1_75_UNCOVERED_FACT_AUDIT",
            "Research version drift")
    require(profile["recording_editor_policy_version"] == editor.POLICY_VERSION,
            "Editor policy/profile mismatch")
    require(profile["additional_model_calls"] == 1 and profile["writer_model_calls"] == 1,
            "Model call contract drift")
    save(AREA / "codex_local_checks.json", {
        "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors),
        "skipped": [{"test": test.id(), "reason": reason} for test, reason in result.skipped],
        "v1_75_protocol_and_integration_test_methods": 11,
        "actual_external_calls": 0,
        "new_real_quality_status": "NOT_TESTED",
        "synthetic_image_semantic_errors": 0,
        "protocol_fixtures_meaning": "REFERENCE_AND_EXECUTION_CHECKS_ONLY_NOT_SEMANTIC_GOLD",
        "s09_model_calls": 1, "s09_retries": 0,
        "writer_model_calls": 1, "writer_retries": 0,
        "deterministic_copy_fallback": False, "automatic_aha_fill": False,
        "scene_specific_runtime_rules": 0,
        "test_files_sha256": tests,
    })
    save(AREA / "codex_candidate.json", {
        "algorithm_candidate": "V1.75",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": current,
        "baseline_candidate_sha256": PRIOR_SHA,
        "baseline_real_run_sha256": PRIOR_REAL_RUN_SHA,
        "baseline_modified_files": sorted(CHANGED),
        "baseline_existing_files_unchanged": len(current) - len(CHANGED),
        "changed_functions": changed_functions,
        "research_profile": profile,
        "full_function_entry": "diary_one_ci.codex_d5_research.run_research",
        "gateway_factory": "diary_one_ci.codex_d5_research.make_gateway",
        "freeze_tool_sha256": sha(Path(__file__)),
        "local_checks_sha256": sha(AREA / "codex_local_checks.json"),
        "implementation_checkpoint_sha256": sha(ROOT / CHECKPOINT),
        "confirmed_design_sha256": sha(ROOT / DESIGN),
        "quality_status": "LOCAL_IMPLEMENTATION_ONLY_FRESH_REAL_CHAIN_NOT_RUN",
        "contracts": {
            "s09_input": "ALL_USABLE_SUPPORTED_FACTS_WITH_SELECTED_CHAPTER_MEMBERSHIP",
            "uncovered_fact_review": "EXACTLY_ONCE_EACH_SELECTION_NOT_REQUIRED",
            "membership_is_value_score": False,
            "finalists_maximum": editor.MAX_FINALISTS,
            "finalist_revisit_hook": "REQUIRED_AND_FACT_GROUNDED",
            "aha_count_range": [0, editor.MAX_AHAS],
            "selected_ahas": "FINAL_COEXISTABLE_SET_NOT_PROVISIONAL",
            "selected_chapter_aha_pairs": "EXACTLY_ONE_AUTHORITATIVE_RELATION_EACH",
            "selected_aha_aha_pairs": "EXACTLY_ONE_AUTHORITATIVE_RELATION_EACH",
            "missing_or_unresolved_relation": "FAIL_CLOSED",
            "editor_calls": 1, "editor_retries": 0, "automatic_fill": False,
            "aha_moment": "ONE_FACT_ONE_S04_REPRESENTATIVE_FRAME",
            "writer_references": "REQUEST_LOCAL_SHORT_IDS_PRIVATE_MAP",
            "writer_policy": writer.POLICY_VERSION,
            "writer_calls": 1, "writer_fallback": "FORBIDDEN",
        },
        "future_run": {
            "pack": 1, "rounds": 1,
            "fresh_decode_and_extraction": True, "fresh_perception": True,
            "cross_run_semantic_cache": False,
            "pipeline_scope": "NORMALIZATION_AND_S04_S12_NOT_S13",
            "review_before_other_packs": True,
            "next_stage_not_launched_by_freeze": True,
        },
        "unchanged": [
            "S04_FACT_AND_REPRESENTATIVE_FRAME", "S07_CHAPTER_GROUPING",
            "CHAPTER_THREE_TO_FIVE_MEDIA", "S10_CHAPTER_MEDIA",
            "AHA_20_TARGET_24_HARD_MAX", "WRITER_SAFE_EXIT",
            "WEB_APP_DEFAULTS", "GPS_AND_INCREMENTAL_TRIGGER",
        ],
        "exclusions": [
            "WEB_SWITCH", "APP_R2", "FIRMWARE_SDK", "SHARED_STATE",
            "PUBLIC_SYNC", "LONG_TERM_MEMORY", "SCENE_SPECIFIC_RULES",
            "SYNTHETIC_IMAGE_ERROR_GATES", "API_REDRAW_OR_RETRY", "S13",
        ],
    })
    print("V1.75 local candidate frozen; API 0; SHA-256 "
          + sha(AREA / "codex_candidate.json"))


if __name__ == "__main__":
    freeze()

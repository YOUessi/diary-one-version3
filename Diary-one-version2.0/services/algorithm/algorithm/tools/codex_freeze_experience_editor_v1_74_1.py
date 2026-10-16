"""Freeze the V1.74.1 profile-only correction. No API or media work."""

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


AREA = ROOT / "var/codex_v1_74_1_experience_editor_safe_exit"
PRIOR = ROOT / "var/codex_v1_74_experience_editor_safe_exit"
PRIOR_SHA = "ec162fe2095c77e25c37a8720569964538239c9d4671a048804ed901522d7378"
CHANGED = {"src/diary_one_ci/codex_d5_research.py"}
CHECKPOINT = "docs/codex_CHECKPOINT_V1_74_1_PROFILE_CORRECTION.md"
DESIGN = "docs/codex_D5_V1_74_EXPERIENCE_EDITOR_AND_SAFE_WRITER_EXIT_DESIGN_V01.md"


def functions(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name: ast.dump(node)
        for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))
    }


def non_import_behavior(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [
        ast.dump(node) for node in tree.body
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom))
    ]


def freeze():
    require(not AREA.exists(), "Never overwrite a candidate checkpoint")
    require(sha(PRIOR / "codex_candidate.json") == PRIOR_SHA, "V1.74 candidate drift")
    baseline = load(PRIOR / "codex_candidate.json")
    require(inventory(PRIOR / "codex_candidate_runtime") == baseline["source_sha256"],
            "Frozen V1.74 runtime drift")
    current = inventory(ROOT)
    require(set(current) == set(baseline["source_sha256"]), "V1.74.1 runtime file scope drift")
    require({
        name for name in baseline["source_sha256"]
        if current[name] != baseline["source_sha256"][name]
    } == CHANGED, "V1.74.1 changed more than profile metadata")
    old_path = PRIOR / "codex_candidate_runtime/src/diary_one_ci/codex_d5_research.py"
    new_path = ROOT / "src/diary_one_ci/codex_d5_research.py"
    old, new = functions(old_path), functions(new_path)
    require(set(old) == set(new), "Profile module function/class scope changed")
    require({name for name in old if old[name] != new[name]} == {"profile"},
            "Only profile() may change")
    require(non_import_behavior(old_path) == non_import_behavior(new_path),
            "Profile module top-level behavior changed")

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
    profile = research.profile()
    require("S09_AHA_SET_EDITOR" not in profile["stage_models"], "Retired route remains")
    require("writer_policy_unchanged" not in profile, "Stale Writer claim remains")
    require(profile["short_reference_stages"] == [
        "S05_S07_STRUCTURE_PROPOSAL", "S09_AHA_EXPERIENCE_EDITOR", "S11_WRITER_*",
    ], "Short-reference stage declaration incomplete")
    save(AREA / "codex_local_checks.json", {
        "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors),
        "skipped": [{"test": test.id(), "reason": reason} for test, reason in result.skipped],
        "actual_external_calls": 0,
        "correction_scope": "RESEARCH_PROFILE_METADATA_ONLY",
        "runtime_behavior_changed": False,
        "test_files_sha256": tests,
    })
    save(AREA / "codex_candidate.json", {
        "algorithm_candidate": "V1.74.1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": current,
        "baseline_candidate_sha256": PRIOR_SHA,
        "baseline_modified_files": sorted(CHANGED),
        "changed_functions": {"src/diary_one_ci/codex_d5_research.py": ["profile"]},
        "research_profile": profile,
        "full_function_entry": "diary_one_ci.codex_d5_research.run_research",
        "gateway_factory": "diary_one_ci.codex_d5_research.make_gateway",
        "freeze_tool_sha256": sha(Path(__file__)),
        "local_checks_sha256": sha(AREA / "codex_local_checks.json"),
        "implementation_checkpoint_sha256": sha(ROOT / CHECKPOINT),
        "confirmed_design_sha256": sha(ROOT / DESIGN),
        "quality_status": "LOCAL_IMPLEMENTATION_ONLY_FRESH_REAL_CHAIN_NOT_RUN",
        "behavior_contract": "IDENTICAL_TO_V1_74_PROFILE_METADATA_CORRECTED_ONLY",
        "exclusions": [
            "MODEL_PROMPT_CHANGE", "RUNTIME_EXECUTION_CHANGE", "WEB_SWITCH", "APP_R2",
            "FIRMWARE_SDK", "SHARED_STATE", "PUBLIC_SYNC", "LONG_TERM_MEMORY",
        ],
    })
    print("V1.74.1 profile-corrected candidate frozen; API 0; SHA-256 "
          + sha(AREA / "codex_candidate.json"))


if __name__ == "__main__":
    freeze()

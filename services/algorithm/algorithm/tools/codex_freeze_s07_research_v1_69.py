"""Run local tests and freeze the opt-in candidate. No API or media extraction."""
import hashlib
import io
import json
import shutil
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
AREA = ROOT / "var/codex_v1_69_s07_plus_short_refs"
PRIOR = ROOT / "var/codex_v1_68_experience_first_chapter"
PRIOR_SHA = "bf333f5c8bb8958b4b6fadca060b787584f53c78a4e029b8a8d33faa668f0c7a"
B3 = ROOT / "var/codex_structure_short_refs_20260907"
B3_PINS = {"codex_preparation.json": "565f892eae74e373a7310d1f32717e4010ddc7e74992fdf1dc53c99794cacf78",
           "codex_execution_summary.json": "5d016f964a3cae4662d2ebefe9f848a97ae970a04c83cf7735ee9611f65446a4"}
ADDITION = "src/diary_one_ci/codex_s07_research.py"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def inventory(root):
    paths = [p for name in ("src", "contracts") for p in (root / name).rglob("*")
             if p.suffix in (".py", ".json") and "__pycache__" not in p.parts]
    require(all(p.is_file() and not p.is_symlink() for p in paths), "Unexpected source path")
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(paths)}


def freeze():
    require(not AREA.exists(), "Never overwrite a frozen checkpoint")
    require(sha(PRIOR / "codex_candidate.json") == PRIOR_SHA, "V1.68 candidate drift")
    baseline = load(PRIOR / "codex_candidate.json")
    require(inventory(PRIOR / "codex_candidate_runtime") == baseline["source_sha256"], "Archived runtime drift")
    current = inventory(ROOT)
    require({k: v for k, v in current.items() if k != ADDITION} == baseline["source_sha256"],
            "Only the new opt-in module may differ from the 43-file baseline")
    require(ADDITION in current, "New gateway missing")
    for name, digest in B3_PINS.items():
        require(sha(B3 / name) == digest, "B3 evidence receipt drift")
    for name, digest in load(B3 / "codex_preparation.json")["files_sha256"].items():
        require(sha(B3 / name) == digest, "B3 prepared request drift")
    # Pin the real replay inputs, not just the code. No originals or review
    # answers are copied into a model request or public handoff.
    archives = (B3, ROOT / "var/codex_structure_model_comparison_20260907",
                ROOT / "var/codex_v1_68_2_experience_first_chapter_execution")
    evidence_pins = {p.relative_to(ROOT).as_posix(): sha(p) for area in archives
                     for p in sorted(area.rglob("*.json")) if "codex_candidate_runtime" not in p.parts}
    test_pins = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / "tests").rglob("*"))
                 if p.suffix in (".py", ".json")}
    from diary_one_ci import codex_s07_research as research
    from diary_one_ci import x02
    output = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(stream=output, verbosity=1).run(suite)
    print(output.getvalue(), end="")
    require(result.wasSuccessful(), "Local suite failed; candidate not frozen")
    require(not any("S07ResearchTests" in test.id() for test, _ in result.skipped),
            "Real integration checks were skipped")
    require(inventory(ROOT) == current, "Source changed during local checks")
    for name, digest in {**evidence_pins, **test_pins}.items():
        require(sha(ROOT / name) == digest, "Test or real replay input changed during checks")
    AREA.mkdir()
    destination = AREA / "codex_candidate_runtime"
    for name, digest in current.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
        require(sha(target) == digest, "Snapshot copy mismatch")
    require(inventory(destination) == current, "Snapshot inventory mismatch")
    report = {"tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
              "skipped": [{"test": t.id(), "reason": reason} for t, reason in result.skipped],
              "new_integration_tests": 5, "actual_b3_replies": 4, "old_invalid_output_roundtrips": 8,
              "old_full_chain_replays": 2, "old_full_chain_mock_transport_calls": 26,
              "actual_external_calls": 0, "synthetic_semantic_examples": 0,
              "qualification": "OFFLINE_WIRING_NOT_NEW_MODEL_QUALITY", "test_files_sha256": test_pins,
              "replay_archives_sha256": evidence_pins}
    save(AREA / "codex_local_checks.json", report)
    original_preparation = load(PRIOR / "codex_preparation.json")
    save(AREA / "codex_candidate.json", {
        "algorithm_candidate": "V1.69", "created_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": current, "baseline_candidate_sha256": PRIOR_SHA,
        "baseline_differences": [ADDITION], "baseline_existing_files_unchanged": 43,
        "research_profile": research.profile(), "runtime_policies": x02.x02_runtime_policies(),
        "full_function_entry": "diary_one_ci.codex_s07_research.run_research",
        "gateway_factory": "diary_one_ci.codex_s07_research.make_gateway",
        "freeze_tool_sha256": sha(Path(__file__)), "local_checks_sha256": sha(AREA / "codex_local_checks.json"),
        "b3_evidence_pins": B3_PINS, "quality_status": "FRESH_REAL_FULL_CHAIN_NOT_RUN",
        "future_run": {"packs": [1, 2, 3], "rounds_each": 1, "fresh_decode_and_extraction": True,
                       "fresh_perception": True, "cross_run_semantic_cache": False,
                       "same_candidate_all_packs": True, "feedback_after_each_pack": True,
                       "pipeline_scope": "NORMALIZATION_AND_EXISTING_S04_S12_NOT_S13_EXPORT",
                       "start_requires_next_stage": True},
        "authorized_pack_inventory_origin": str(PRIOR / "codex_preparation.json"),
        "authorized_pack_inventory_sha256": sha(PRIOR / "codex_preparation.json"),
        "normalizer_snapshot": original_preparation["normalizer_snapshot"],
        "normalizer_sha256": original_preparation["normalizer_sha256"],
        "exclusions": ["WEB_DEFAULT_SWITCH", "APP_R2", "FIRMWARE_SDK", "SHARED_STATE",
                       "AHA_ELIGIBILITY_CHANGES", "SCENE_RULES", "PUBLIC_DEPLOYMENT"],
    })
    print(json.dumps({"event": "V1_69_FROZEN_LOCAL_ONLY", "source_files": len(current),
                      "tests": result.testsRun, "skipped": len(result.skipped), "external_calls": 0,
                      "candidate_sha256": sha(AREA / "codex_candidate.json")}, ensure_ascii=False))


if __name__ == "__main__":
    freeze()

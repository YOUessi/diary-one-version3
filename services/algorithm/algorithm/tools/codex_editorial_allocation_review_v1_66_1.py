"""Execution-only V1.66 revision: serialize Path safely before exclusive creation.

Reuses the frozen harness read-only. Algorithm, candidate, normalizer and original
round records remain unchanged. New executions live below codex_execution_v2.
"""
import argparse
import fcntl
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
OLD_PATH = ROOT / "tools/codex_editorial_allocation_review_v1_66.py"
OLD_SHA = "9609c957a92b0f99b0fd6f278c01bd40051c99f6f6f67032c23d590d3778f23f"
CANDIDATE_SHA = "e833ee755e00d606c625624cb04bdb8d3efc27947e91229dfc7f2c64ee70d096"
spec = importlib.util.spec_from_file_location("frozen_v166_harness", OLD_PATH)
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
AREA = old.AREA
RECEIPT = AREA / "codex_execution_revision_v2.json"


def encode(value):
    def explicit_default(item):
        if isinstance(item, Path):
            return str(item)
        raise TypeError("Unsupported audit value type: " + type(item).__name__)
    return json.dumps(value, ensure_ascii=False, indent=2, default=explicit_default) + "\n"


def save(path, value):
    if path.name == "codex_full_run.json":
        value = {**value, "original_harness_sha256": value["harness_sha256"],
                 "harness_sha256": old.sha(Path(__file__)), "execution_revision": "V1.66.1_AUDIT_IO_ONLY",
                 "execution_revision_receipt_sha256": old.sha(RECEIPT),
                 "input_evidence_redecoded_for_revision": False,
                 "input_evidence_reuse_reason": "ALREADY_FRESH_FULL_NORMALIZATION_NO_PRIOR_SEMANTIC_CALL"}
    serialized = encode(value)  # Must finish before creating a file; unknown types remain errors.
    with path.open("x", encoding="utf-8") as stream:
        stream.write(serialized)


def identities():
    candidate_path = AREA / "codex_candidate.json"
    old.require(old.sha(OLD_PATH) == OLD_SHA, "Frozen original harness drift")
    old.require(old.sha(candidate_path) == CANDIDATE_SHA, "Frozen candidate receipt drift")
    candidate = old.load(candidate_path)
    old.require(candidate["harness_sha256"] == OLD_SHA, "Original harness identity mismatch")
    old.require(old.source_inventory(AREA / "codex_candidate_runtime") == candidate["source_sha256"], "Frozen algorithm drift")
    return candidate


def prepare_revision():
    candidate = identities()
    old.require(not RECEIPT.exists(), "Revision already sealed; do not overwrite")
    original = AREA / "pack_1/round_1/codex_full_run.json"
    partial = AREA / "pack_1/round_1/codex_stage_calls/codex_001_request.json"
    failure = old.load(original)
    old.require(failure["status"] == "FAILED" and not failure["stage_calls"] and not failure["transport_attempts"],
                "Original attempt must have zero semantic/API calls")
    old.require(not list(partial.parent.glob("*_provider.json")), "Unexpected original provider attempt")
    try:
        old.load(partial)
    except json.JSONDecodeError:
        pass
    else:
        raise RuntimeError("Expected preserved partial original audit record")
    old.run("1", False)  # Existing manifest/frame hashes only; never reads a credential.
    x02 = old.import_candidate(AREA / "codex_candidate_runtime")
    from diary_one_ci.bundle import load_app_library_bundle
    bundle = load_app_library_bundle(AREA / "pack_1/round_1/codex_manifest.json")
    evidence = x02._perception_evidence(bundle, bundle.manifest["assets"][:3])
    value = {"_perception_evidence": evidence}
    decoded = json.loads(encode(value))
    old.require(decoded["_perception_evidence"][0][2] == str(evidence[0][2]), "Path conversion failed")
    invalid_path = AREA / "codex_v2_unsupported_value_must_not_exist.json"
    old.require(not invalid_path.exists(), "Preflight output path already exists")
    try:
        save(invalid_path, {"unsupported": object()})
    except TypeError:
        pass
    else:
        raise RuntimeError("Unknown audit types must remain errors")
    old.require(not invalid_path.exists(), "Serialization failure created a partial file")
    save(RECEIPT, {
        "revision": "V1.66.1_AUDIT_IO_ONLY", "created_at": old.now(), "original_harness_sha256": OLD_SHA,
        "runner_sha256": old.sha(Path(__file__)), "candidate_sha256": CANDIDATE_SHA,
        "algorithm_source_sha256_unchanged": candidate["source_sha256"],
        "normalization_harness_sha256_unchanged": candidate["normalization_harness_sha256"],
        "original_zero_call_failure": {"path": str(original), "sha256": old.sha(original),
            "partial_request_path": str(partial), "partial_request_sha256": old.sha(partial),
            "stage_calls": 0, "transports": 0, "error_type": failure["error_type"],
            "cause": "Path in _perception_evidence failed JSON serialization after exclusive file creation; next batch collided"},
        "local_preflight": {"actual_evidence_Path_serialization": "PASS",
            "unknown_type_rejected_before_file_creation": "PASS", "pack_1_existing_manifest_and_frames": "PASS"},
        "execution_directory": "pack_<n>/round_1/codex_execution_v2", "model_calls": 0,
        "frames_redecoded": False, "semantic_cache_reused": False,
    })
    old.emit({"event": "EXECUTION_REVISION_PREPARED_NO_MODEL_CALL", "receipt": str(RECEIPT),
              "runner_sha256": old.sha(Path(__file__)), "algorithm_unchanged": True})


def run(pack_id, live):
    candidate = identities()
    receipt = old.load(RECEIPT)
    old.require(receipt["runner_sha256"] == old.sha(Path(__file__)), "Execution revision runner drift")
    old.require(receipt["candidate_sha256"] == CANDIDATE_SHA and receipt["original_harness_sha256"] == OLD_SHA,
                "Execution revision identity mismatch")
    original = receipt["original_zero_call_failure"]
    old.require(old.sha(Path(original["path"])) == original["sha256"]
                and old.sha(Path(original["partial_request_path"])) == original["partial_request_sha256"],
                "Original zero-call failure was modified")
    old.run(pack_id, False)  # Keep all frozen input/candidate/harness checks, without starting old slots.
    if not live:
        old.emit({"event": "EXECUTION_V2_PREFLIGHT_PASS_NO_MODEL_CALL", "pack": pack_id})
        return 0
    round_dir = AREA / ("pack_" + pack_id) / "round_1"
    execution = round_dir / "codex_execution_v2"
    with (AREA / "codex_live_serial.lock").open("a+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("Another V1.66 live run is active") from None
        old.require(not execution.exists(), "Refusing to repeat an attempted execution_v2 slot")
        from diary_one_ci.x01_server import _resolve_qwen_api_key
        from diary_one_ci.x01 import QwenChatCompletionsAdapter
        from diary_one_ci.bundle import load_app_library_bundle
        key, credential_source = _resolve_qwen_api_key()
        old.require(bool(key), "Existing server-side Qwen credential unavailable")
        manifest_path = round_dir / "codex_manifest.json"
        bundle = load_app_library_bundle(manifest_path)
        execution.mkdir()
        save(execution / "codex_attempt.json", {"started_at": old.now(), "pack": pack_id, "round": 1,
             "execution_revision": "V1.66.1_AUDIT_IO_ONLY", "revision_receipt_sha256": old.sha(RECEIPT),
             "candidate_sha256": CANDIDATE_SHA, "manifest_path": manifest_path,
             "model": old.MODEL, "endpoint": old.ENDPOINT})
        old.save = save  # Runtime-only audit writer replacement; never modify the frozen module file.
        x02 = old.import_candidate(AREA / "codex_candidate_runtime")
        summary = {"pack": pack_id, "round": 1, "assets": len(bundle.manifest["assets"]),
                   "frames": sum(len(a["frames"]) for a in bundle.manifest["assets"]), "policies": candidate["runtime_policies"]}
        return old.execute_live(x02, QwenChatCompletionsAdapter, key, credential_source, execution, manifest_path,
            old.load(round_dir / "codex_normalization.json"), old.preparation(), candidate, candidate["runtime_policies"], summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare-revision", "run"))
    parser.add_argument("--pack", choices=("1", "2", "3"))
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare-revision":
        old.require(not args.live and args.pack is None, "Revision preparation is local only")
        prepare_revision()
    else:
        old.require(args.pack is not None, "Run requires --pack")
        sys.exit(run(args.pack, args.live))

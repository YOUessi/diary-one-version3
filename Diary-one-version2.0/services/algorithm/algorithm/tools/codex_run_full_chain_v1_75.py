"""One fresh pack per command, frozen V1.75; no API without explicit --live."""

import argparse
import copy
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import codex_run_full_chain_v1_74_1 as base


BASE_RUNNER = ROOT / "tools/codex_run_full_chain_v1_74_1.py"
BASE_RUNNER_SHA = "a8de2ecd17d7568132c1ae5788f4a6f89ddb3bae707a8ad9b3d920209ab55067"
NORMALIZER = ROOT / "tools/codex_prepare_experience_first_evidence_v1_68.mjs"
NORMALIZER_SHA = "e7795b18537ea94e6e7364fd2fbf9c505fecc7daa5885fea7963e458a55cbe88"
LOADER = ROOT / "tools/codex_v175_normalizer_loader.mjs"
LOADER_SHA = "6325a8b6f4487b7f52f96dd03e414ca762bca5c7dd336ef1fb8e957d69f74375"
FROZEN = ROOT / "var/codex_v1_75_uncovered_fact_audit"
AREA = ROOT / "var/codex_v1_75_full_chain_execution"
PRIOR = ROOT / "var/codex_v1_74_1_experience_editor_safe_exit"
PRIOR_RUN = ROOT / "var/codex_v1_74_1_full_chain_execution"
CANDIDATE_SHA = "70442cf035a4f2f1416606b13b4b70caff41b810ed9b63be6442c08a432f127f"
PRIOR_SHA = "a613c4de30fdca8fa4d38c8c3bf66d5fac2f45cd021b66d8eb357052009bf96a"

require, now, sha, load, save, emit = (
    base.require, base.now, base.sha, base.load, base.save, base.emit,
)


def configure_base():
    """Reuse the pinned transport/audit implementation with V1.75 identity."""
    require(sha(BASE_RUNNER) == BASE_RUNNER_SHA, "Pinned V1.74.1 runner drift")
    base.__file__ = __file__
    base.NORMALIZER = NORMALIZER
    base.NORMALIZER_SHA = NORMALIZER_SHA
    base.LOADER = LOADER
    base.LOADER_SHA = LOADER_SHA
    base.FROZEN = FROZEN
    base.AREA = AREA
    base.PRIOR = PRIOR
    base.PRIOR_RUN = PRIOR_RUN
    base.CANDIDATE_SHA = CANDIDATE_SHA
    base.PRIOR_SHA = PRIOR_SHA


configure_base()


def verify():
    candidate, policies = base.verify()
    require(candidate["algorithm_candidate"] == "V1.75", "V1.75 candidate identity drift")
    require(candidate["baseline_candidate_sha256"] == PRIOR_SHA, "V1.75 baseline drift")
    return candidate, policies


def prepare():
    candidate, policies = verify()
    require(not AREA.exists(), "Never overwrite a run area")
    origin = load(PRIOR_RUN / "codex_preparation.json")
    require(origin["candidate_sha256"] == PRIOR_SHA, "V1.74.1 pack inventory origin drift")
    packs = [
        copy.deepcopy(pack) for pack in origin["packs"]
        if str(pack["pack_id"]) == "1"
    ]
    require(len(packs) == 1, "Pack 1 inventory missing or duplicated")
    for pack in packs:
        pack["session_id"] = str(uuid.uuid5(
            uuid.NAMESPACE_URL, "codex-v175-full-pack-" + str(pack["pack_id"]),
        ))
        pack["exported_at"] = now()
    AREA.mkdir()
    shutil.copyfile(FROZEN / "codex_candidate.json", AREA / "codex_candidate.json")
    save(AREA / "codex_preparation.json", {
        "experiment": "CODEX_V1_75_FULL_CHAIN",
        "algorithm_baseline": "V1.74.1", "algorithm_candidate": "V1.75",
        "candidate_sha256": CANDIDATE_SHA, "created_at": now(), "packs": packs,
        "authorized_pack_inventory_origin": str(PRIOR_RUN / "codex_preparation.json"),
        "authorized_pack_inventory_sha256": sha(PRIOR_RUN / "codex_preparation.json"),
        "normalizer_snapshot": origin["normalizer_snapshot"],
        "normalizer_sha256": origin["normalizer_sha256"],
        "normalizer_preparation_sha256": origin["normalizer_preparation_sha256"],
        "normalization_harness_sha256": NORMALIZER_SHA,
        "loader_sha256": LOADER_SHA, "runner_sha256": sha(Path(__file__)),
        "base_runner_sha256": BASE_RUNNER_SHA,
        "research_profile": candidate["research_profile"], "runtime_policies": policies,
        "pack_order": [1], "rounds_per_pack": 1,
        "fresh_decode_and_extraction": True, "cross_run_semantic_cache": False,
        "harness_retries": 0,
        "external_payload": "AUTHORIZED_NORMALIZED_FRAMES_AND_DERIVED_TEXT_NO_ORIGINALS",
        "pipeline_scope": "NORMALIZATION_THEN_S04_S12_NOT_S13",
        "deployment": "NO_WEB_APP_SWITCH",
    })
    emit({"event": "PREPARED_NO_API", "packs": {
        pack["pack_id"]: len(pack["assets"]) for pack in packs
    }})


def preparation():
    candidate, policies = verify()
    prep = load(AREA / "codex_preparation.json")
    require(prep["candidate_sha256"] == CANDIDATE_SHA
            and sha(AREA / "codex_candidate.json") == CANDIDATE_SHA,
            "Preparation candidate drift")
    require(prep["runner_sha256"] == sha(Path(__file__))
            and prep["base_runner_sha256"] == BASE_RUNNER_SHA
            and prep["loader_sha256"] == sha(LOADER), "Execution harness drift")
    require(prep["research_profile"] == candidate["research_profile"]
            and prep["runtime_policies"] == policies, "Runtime profile drift")
    return prep, candidate


base.preparation = preparation


def save_with_v175_metadata(path, value):
    if path.name == "codex_full_run.json" and isinstance(value, dict):
        value["experiment"] = "CODEX_V1_75_FULL_CHAIN"
        value["algorithm_candidate"] = "V1.75"
        value["base_runner_sha256"] = BASE_RUNNER_SHA
    return save(path, value)


base.save = save_with_v175_metadata


def normalize(pack_id):
    preparation()
    require(pack_id == "1", "V1.75 first validation is limited to pack 1")
    require(not (AREA / ("pack_" + pack_id)).exists(), "Normalization already attempted")
    return subprocess.run([
        "node", "--no-warnings", "--experimental-loader", str(LOADER),
        str(NORMALIZER), pack_id,
    ], cwd=ROOT, check=False).returncode


def run(pack_id, live):
    require(pack_id == "1", "V1.75 first validation is limited to pack 1")
    return base.run(pack_id, live)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "normalize", "run"))
    parser.add_argument("--pack", choices=("1",))
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare":
        require(args.pack is None and not args.live, "Preparation is local only")
        prepare()
    elif args.command == "normalize":
        require(args.pack is not None and not args.live, "Normalize one explicit pack only")
        sys.exit(normalize(args.pack))
    else:
        require(args.pack is not None, "Run one explicit pack only")
        sys.exit(run(args.pack, args.live))

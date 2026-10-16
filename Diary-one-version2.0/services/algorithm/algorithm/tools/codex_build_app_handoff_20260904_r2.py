"""Mechanically package frozen V1.63 bytes; never uses active source or a model.

Repository-side prepare/seal tool. The delivered offline runner is standalone;
this builder intentionally requires the original frozen repository references.
"""
import argparse
import datetime
import hashlib
import io
import json
import shutil
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
R1 = ROOT / "handoffs/codex_app_20260904_r1"
AREA = ROOT / "var/codex_v1_64_repeat_review"
PACKAGE = ROOT / "handoffs/codex_app_20260904_r2"
CANDIDATE = PACKAGE.name
PREPARATION_SHA = "ef514491a983d29374b922246306f9e71df2d004cb774876c4653b92edbc5a32"
R1_TAR_SHA = "bba1db3866560fa9c43d7fe1c8153a26551b256644dad26bf4d2fff28e2dde99"
R1_MANIFEST_SHA = "3925dec1eabc5e33985a2ccafa7c7023632b035200fd42d7c8cdb0cd33afb581"
HELPER_SHA = "4a85330734086fbdf13d92d96d4df8866f971ebd04af194542f4b47f2100b2dc"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def pinned_files():
    preparation = AREA / "codex_preparation.json"
    assert sha(preparation) == PREPARATION_SHA, "frozen preparation drift"
    assert sha(R1.with_suffix(".tar")) == R1_TAR_SHA, "sealed R1 drift"
    assert sha(R1 / "codex_source_manifest.json") == R1_MANIFEST_SHA
    expected = json.loads(preparation.read_text())["source_sha256"]
    assert len(expected) == 40
    paths = {}
    for name, expected_sha in expected.items():
        relative = Path(name)
        assert not relative.is_absolute() and ".." not in relative.parts
        assert relative.parts[0] in {"src", "contracts"} and relative.suffix in {".py", ".json"}
        path = AREA / "codex_runtime" / relative
        assert path.is_file() and not path.is_symlink() and sha(path) == expected_sha
        paths[name] = path
    old = json.loads((R1 / "codex_source_manifest.json").read_text())
    config = next(r for r in old["files"] if r["path"] == "pyproject.toml")
    path = R1 / "source/pyproject.toml"
    assert sha(path) == config["sha256"]
    paths["pyproject.toml"] = path
    return paths, old


def archive_files(destination, paths, prefix=""):
    assert not destination.exists(), "refusing to overwrite archive"
    with tarfile.open(destination, "w", format=tarfile.USTAR_FORMAT) as archive:
        for name, path in sorted(paths.items()):
            raw = path.read_bytes()
            member = tarfile.TarInfo(prefix + name)
            member.size, member.mode, member.mtime = len(raw), 0o644, 0
            archive.addfile(member, io.BytesIO(raw))


def prepare():
    paths, old = pinned_files()
    assert sha(R1 / "codex_contract_test_support.py") == HELPER_SHA
    runner = ROOT / "tools/codex_verify_app_handoff_20260904_r2.py"
    assert runner.exists(), "offline runner must be ready before packaging"
    PACKAGE.mkdir(parents=True, exist_ok=False)
    records = []
    for name, path in sorted(paths.items()):
        destination = PACKAGE / "source" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        records.append({"path": name, "sha256": sha(path), "bytes": path.stat().st_size,
                        "origin": "SEALED_R1_UNCHANGED_PROJECT_METADATA" if name == "pyproject.toml" else "V1_63_FROZEN_RUNTIME_IN_V1_64_EVALUATION"})
    archive_files(PACKAGE / "codex_source.tar", paths)
    source_manifest = {
        "candidate_id": CANDIDATE, "runtime_checkpoint": "V1.63",
        "source_kind": "VERIFIED_FROZEN_RUNTIME_NOT_ACTIVE_WORKTREE_NOT_GIT_HEAD",
        "evaluation_record": "V1.64_NOT_ALGORITHM_VERSION",
        "excluded_active_checkpoint": "V1.65",
        "preparation_manifest_sha256": PREPARATION_SHA,
        "archive_sha256": sha(PACKAGE / "codex_source.tar"), "files": records,
        "quality_status": "KNOWN_FAILURES_NOT_ACCEPTED_NOT_AN_INTEGRATION_BLOCKER",
        "git_head_context_only": "8b79fb7faa4981cf352551e4f15dff24c92a3a7e",
        "git_branch_context_only": "codex/validation-v01-v02-20260829",
        "exclusions": ["active V1.65 source", ".git", "environment and credentials", "real media", "real model responses", "user notes", "Web", "App", "Firmware/SDK", "shared status", "paid experiment tools"],
    }
    emit(PACKAGE / "codex_source_manifest.json", source_manifest)
    previous = {r["path"]: r for r in old["files"]}
    now = {r["path"]: r for r in records}
    difference = []
    for name in sorted(previous.keys() | now.keys()):
        left, right = previous.get(name), now.get(name)
        status = "ADDED" if left is None else "REMOVED" if right is None else "UNCHANGED" if left["sha256"] == right["sha256"] else "CHANGED"
        difference.append({"path": name, "status": status, "r1_sha256": left["sha256"] if left else None,
                           "r2_sha256": right["sha256"] if right else None})
    emit(PACKAGE / "codex_r1_r2_file_differences.json", {"r1": old["candidate_id"], "r2": CANDIDATE, "files": difference})
    assert sha(R1 / "codex_source.tar") == old["archive_sha256"]
    shutil.copyfile(R1 / "codex_source.tar", PACKAGE / "codex_rollback_r1_source.tar")
    shutil.copyfile(R1 / "codex_source_manifest.json", PACKAGE / "codex_rollback_r1_source_manifest.json")
    shutil.copyfile(R1 / "codex_contract_test_support.py", PACKAGE / "codex_contract_test_support.py")
    shutil.copyfile(runner, PACKAGE / "codex_offline_runner.py")
    shutil.copyfile(Path(__file__), PACKAGE / "codex_build_package.py")
    emit(PACKAGE / "codex_helper_provenance.json", {
        "source": "sealed R1 codex_contract_test_support.py", "source_sha256": HELPER_SHA,
        "synthetic_helpers_only": True, "no_real_fixture_or_semantic_gold_included": True,
        "runner_repository_path": str(runner.relative_to(ROOT)), "runner_sha256": sha(runner),
        "schema_validator_limit": "EXISTING_SUBSET_VALIDATOR_NOT_FULL_DRAFT2020_12_CERTIFICATION",
    })
    print(json.dumps({"candidate": CANDIDATE, "source_files": len(records), "source_sha256": source_manifest["archive_sha256"]}))


def seal():
    paths, old = pinned_files()
    manifest = json.loads((PACKAGE / "codex_source_manifest.json").read_text())
    assert {r["path"] for r in manifest["files"]} == set(paths)
    assert sha(PACKAGE / "codex_source.tar") == manifest["archive_sha256"]
    with tarfile.open(PACKAGE / "codex_source.tar") as archive:
        assert {m.name for m in archive} == set(paths)
        for r in manifest["files"]:
            assert sha(paths[r["path"]]) == sha(PACKAGE / "source" / r["path"]) == r["sha256"]
            assert hashlib.sha256(archive.extractfile(r["path"]).read()).hexdigest() == r["sha256"]
    for required in ("codex_README.md", "codex_profile.json", "codex_examples/codex_offline_evidence.json", "codex_independent_verification.json"):
        assert (PACKAGE / required).is_file(), required
    artifact_manifest = PACKAGE / "codex_artifact_manifest.json"
    assert not artifact_manifest.exists(), "already sealed; create a new candidate instead"
    assert sha(PACKAGE / "codex_contract_test_support.py") == HELPER_SHA
    assert sha(PACKAGE / "codex_rollback_r1_source.tar") == old["archive_sha256"]
    assert sha(PACKAGE / "codex_rollback_r1_source_manifest.json") == R1_MANIFEST_SHA
    helper = json.loads((PACKAGE / "codex_helper_provenance.json").read_text())
    assert sha(PACKAGE / "codex_offline_runner.py") == helper["runner_sha256"]
    assert sha(PACKAGE / "codex_build_package.py") == sha(Path(__file__))
    allowed = {"source/" + name for name in paths} | {
        "codex_source.tar", "codex_source_manifest.json", "codex_r1_r2_file_differences.json",
        "codex_rollback_r1_source.tar", "codex_rollback_r1_source_manifest.json",
        "codex_contract_test_support.py", "codex_offline_runner.py", "codex_build_package.py",
        "codex_helper_provenance.json", "codex_README.md", "codex_profile.json",
        "codex_independent_verification.json", "codex_examples/codex_synthetic_artifacts.json",
    }
    generated = json.loads((PACKAGE / "codex_examples/codex_synthetic_artifacts.json").read_text())
    for record in generated["files"]:
        relative = Path(record["path"])
        assert not relative.is_absolute() and ".." not in relative.parts
        name = "codex_examples/" + relative.as_posix()
        path = PACKAGE / name
        assert path.is_file() and not path.is_symlink()
        assert sha(path) == record["sha256"] and path.stat().st_size == record["bytes"]
        allowed.add(name)
    actual = {p.relative_to(PACKAGE).as_posix() for p in PACKAGE.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    assert actual == allowed, {"unexpected": sorted(actual - allowed), "missing": sorted(allowed - actual)}
    records = []
    for path in sorted(PACKAGE.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        assert not path.is_symlink()
        name = path.relative_to(PACKAGE).as_posix()
        assert path.suffix in {".py", ".json", ".md", ".toml", ".tar", ".jpg"}, name
        assert not any(p.startswith(".") for p in Path(name).parts), name
        records.append({"path": name, "sha256": sha(path), "bytes": path.stat().st_size})
    emit(artifact_manifest, {"candidate_id": CANDIDATE, "files": records,
        "excluded": ["codex_artifact_manifest.json (self)", "__pycache__"],
        "privacy_scope": "NO_REAL_MEDIA_REAL_MODEL_OUTPUT_USER_NOTES_OR_CREDENTIALS"})
    archive = PACKAGE.with_suffix(".tar")
    archive_files(archive, {r["path"]: PACKAGE / r["path"] for r in records} | {artifact_manifest.name: artifact_manifest}, CANDIDATE + "/")
    receipt_path = PACKAGE.parent / (CANDIDATE + "_delivery.json")
    assert not receipt_path.exists()
    selected = [archive, artifact_manifest, PACKAGE / "codex_source.tar", PACKAGE / "codex_source_manifest.json", PACKAGE / "codex_profile.json", PACKAGE / "codex_README.md", PACKAGE / "codex_examples/codex_offline_evidence.json", PACKAGE / "codex_independent_verification.json"]
    receipt = {"candidate_id": CANDIDATE, "runtime_checkpoint": "V1.63", "sealed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "OFFLINE_INTEGRATION_CANDIDATE_NOT_DEPLOYED_NOT_QUALITY_ACCEPTED", "r1_archive_sha256_unchanged": R1_TAR_SHA,
        "api_calls": 0, "service_started": False, "default_upgraded": False,
        "artifacts": [{"path": str(p), "sha256": sha(p), "bytes": p.stat().st_size} for p in selected]}
    emit(receipt_path, receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "seal"))
    args = parser.parse_args()
    prepare() if args.action == "prepare" else seal()

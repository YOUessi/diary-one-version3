"""Package exact runtime bytes and synthetic contract fixtures. Never calls a model."""
import argparse
import ast
import hashlib
import io
import json
import shutil
import subprocess
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def emit(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def source_files():
    return sorted([ROOT / "pyproject.toml"] + [p for base in ("src", "contracts")
                  for p in (ROOT / base).rglob("*")
                  if p.is_file() and p.suffix in (".py", ".json") and "__pycache__" not in p.parts])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    files = source_files()
    source_records = []
    archive = out / "codex_source.tar"
    with tarfile.open(archive, "w", format=tarfile.USTAR_FORMAT) as tar:
        for path in files:
            if path.is_symlink():
                raise ValueError("symlinks are outside the handoff scope")
            raw = path.read_bytes()
            name = path.relative_to(ROOT).as_posix()
            item = tarfile.TarInfo(name)
            item.size, item.mode, item.mtime = len(raw), 0o644, 0
            tar.addfile(item, io.BytesIO(raw))
            source_records.append({"path": name, "sha256": digest(raw), "bytes": len(raw)})
            destination = out / "source" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)
    manifest = {
        "candidate_id": "codex_app_20260904_r1",
        "source_kind": "EXACT_DIRTY_WORKTREE_RUNTIME_SNAPSHOT_NOT_GIT_HEAD",
        "runtime_checkpoint": "V1.49",
        "latest_research_checkpoint": "V1.51_NOT_ACTIVATED",
        "git_head_context_only": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "git_branch_context_only": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
        "archive_sha256": digest(archive.read_bytes()),
        "files": source_records,
        "exclusions": [".git", "environment and credentials", "real media", "real model responses", "user notes", "Web", "App", "Firmware/SDK", "live Writer experiments"],
    }
    emit(out / "codex_source_manifest.json", manifest)
    rollback = ROOT / "var/codex_content_handoff_ab_v1_47/codex_candidate_v1_46.tar"
    expected = "3654c0026df67eed1c768ed27cd4e02aba10397559a6cae63835fa676ba861da"
    if digest(rollback.read_bytes()) != expected:
        raise ValueError("historical rollback snapshot drift")
    rollback_records = []
    with tarfile.open(rollback) as tar:
        for item in tar:
            if item.isdir():
                continue
            if not item.isfile() or item.name not in {r["path"] for r in source_records}:
                raise ValueError("rollback contains files outside source allowlist")
            raw = tar.extractfile(item).read()
            rollback_records.append({"path": item.name, "sha256": digest(raw), "bytes": len(raw)})
    shutil.copyfile(rollback, out / "codex_rollback_v1_46.tar")
    emit(out / "codex_rollback_manifest.json", {"checkpoint": "V1.46", "archive_sha256": expected,
         "not_quality_accepted": True, "not_previously_accepted_app_backend": True,
         "files": sorted(rollback_records, key=lambda r: r["path"])})
    # Mechanical extraction of already-existing, synthetic integration helpers only.
    # No tests/fixtures or real-run text is included.
    helper_source = ROOT / "tests/test_x02.py"
    source = helper_source.read_text(encoding="utf-8")
    wanted = {"assert_json_schema_instance", "ScriptedGateway", "make_x02_bundle_v02"}
    parts = [ast.get_source_segment(source, node) for node in ast.parse(source).body
             if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in wanted]
    if len(parts) != len(wanted):
        raise ValueError("test helper extraction is incomplete")
    header = ("# Mechanically extracted synthetic helpers; NOT production runtime.\n"
              "import json, re, uuid\nfrom pathlib import Path\n"
              "from diary_one_ci.x02 import StageModelGateway, StageRun\n"
              "from diary_one_ci.bundle import APP_LIBRARY_BUNDLE_VERSION_V02, PHONE_TEST_EVIDENCE_PROFILE_V01\n"
              "from diary_one_ci.core import sha256_file\n\n")
    (out / "codex_contract_test_support.py").write_text(header + "\n\n".join(parts) + "\n", encoding="utf-8")
    emit(out / "codex_helper_provenance.json", {"source": "tests/test_x02.py",
         "source_sha256": digest(helper_source.read_bytes()), "extracted_definitions": sorted(wanted),
         "schema_validator_scope": "EXISTING_REPOSITORY_SUBSET_VALIDATOR_NOT_FULL_DRAFT2020_12_CERTIFICATION"})
    shutil.copyfile(ROOT / "tools/codex_verify_app_handoff_20260904_r1.py", out / "codex_offline_runner.py")
    shutil.copyfile(Path(__file__), out / "codex_build_package.py")
    if source_records != [{"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p.read_bytes()), "bytes": p.stat().st_size} for p in source_files()]:
        raise ValueError("source changed during packaging")
    print(json.dumps({"output": str(out), "source_files": len(files), "archive_sha256": manifest["archive_sha256"]}))


if __name__ == "__main__":
    main()

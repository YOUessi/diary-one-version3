"""Verify package source isolation, record read-only local health, and seal artifacts."""
import datetime
import hashlib
import io
import json
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "handoffs/codex_app_20260904_r1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    manifest = json.loads((PACKAGE / "codex_source_manifest.json").read_text())
    assert sha(PACKAGE / "codex_source.tar") == manifest["archive_sha256"]
    for record in manifest["files"]:
        assert sha(PACKAGE / "source" / record["path"]) == record["sha256"]
        assert sha(ROOT / record["path"]) == record["sha256"], "working source drifted after snapshot"
    with tarfile.open(PACKAGE / "codex_source.tar") as tar:
        assert {m.name for m in tar} == {r["path"] for r in manifest["files"]}
        for record in manifest["files"]:
            assert hashlib.sha256(tar.extractfile(record["path"]).read()).hexdigest() == record["sha256"]
    checked_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    health = subprocess.run(["curl", "--noproxy", "*", "--connect-timeout", "2", "--max-time", "4",
        "-sS", "-o", "/dev/null", "-w", "%{http_code}", "http://127.0.0.1:8787/health"], capture_output=True, text=True)
    listener = subprocess.run(["lsof", "-nP", "-iTCP:8787", "-sTCP:LISTEN"], capture_output=True, text=True)
    emit(PACKAGE / "codex_service_observation.json", {
        "checked_at_utc": checked_at, "scope": "CURRENT_SANDBOX_READ_ONLY_LOCALHOST_ONLY",
        "url": "http://127.0.0.1:8787/health", "curl_exit_code": health.returncode,
        "http_status": health.stdout, "curl_error": health.stderr.strip(),
        "listener_exit_code": listener.returncode,
        "visible_listening_records_present": bool(listener.stdout.strip()),
        "live_identity": "NOT_OBTAINED" if health.returncode else "HTTP_STATUS_ONLY_BODY_NOT_INSPECTED",
        "does_not_prove_absence_of_cloud_resources": True,
        "no_keys_read_no_start_no_deployment": True,
    })
    # Preserve only reproducible, scoped tooling and reference hashes; no test
    # corpora or original user/project checkpoint contents are copied.
    references = [ROOT / "tests/test_x02.py", ROOT / "tools/codex_run_app_handoff_regression_20260904_r1.py",
        ROOT.parent / "Nexleap-Diary-One/04_App/integration_checkpoints/APP-ENG-075_algorithm_handoff_refresh_and_memory_truth_input_2026-09-04.md",
        ROOT.parent / "Nexleap-Diary-One/04_App/integration_checkpoints/APP-ENG-076_memory_home_truth_acceptance_2026-09-04.md"]
    emit(PACKAGE / "codex_readonly_reference_hashes.json", [{"path": str(p), "sha256": sha(p)} for p in references])
    records = []
    for path in sorted(PACKAGE.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.name == "codex_artifact_manifest.json":
            continue
        assert not path.is_symlink()
        name = path.relative_to(PACKAGE).as_posix()
        assert path.suffix in {".py", ".json", ".md", ".toml", ".tar", ".jpg"}, name
        records.append({"path": name, "sha256": sha(path), "bytes": path.stat().st_size})
    artifact_manifest = PACKAGE / "codex_artifact_manifest.json"
    emit(artifact_manifest, {"candidate_id": manifest["candidate_id"], "files": records,
         "excluded": ["codex_artifact_manifest.json (self)", "__pycache__"],
         "privacy_scope": "NO_REAL_MEDIA_REAL_FACT_TEXT_USER_NOTES_OR_CREDENTIALS"})
    archive = ROOT / "handoffs/codex_app_20260904_r1.tar"
    with tarfile.open(archive, "w", format=tarfile.USTAR_FORMAT) as tar:
        for name in sorted([r["path"] for r in records] + [artifact_manifest.name]):
            path = PACKAGE / name
            data = path.read_bytes()
            member = tarfile.TarInfo(PACKAGE.name + "/" + name)
            member.size, member.mode, member.mtime = len(data), 0o644, 0
            tar.addfile(member, io.BytesIO(data))
    paths = [PACKAGE / "codex_README.md", PACKAGE / "codex_source.tar", PACKAGE / "codex_source_manifest.json",
        PACKAGE / "codex_rollback_v1_46.tar", PACKAGE / "codex_regression_evidence.json",
        PACKAGE / "codex_examples/codex_offline_evidence.json",
        PACKAGE / "codex_examples/codex_contract_identities.json", artifact_manifest, archive]
    receipt = {"candidate_id": manifest["candidate_id"], "handoff_status": "OFFLINE_TECHNICAL_ONLY_NOT_DEPLOYED",
        "runtime_source_unchanged_from_snapshot": True, "git_commit_created": False,
        "artifacts": [{"path": str(p), "sha256": sha(p), "bytes": p.stat().st_size} for p in paths]}
    emit(ROOT / "handoffs/codex_app_20260904_r1_delivery.json", receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()

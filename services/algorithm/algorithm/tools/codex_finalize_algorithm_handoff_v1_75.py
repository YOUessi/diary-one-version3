"""Hash, verify, and archive the standalone V1.75 engineering handoff."""

import hashlib
import json
import re
import subprocess
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME = "codex_diary_one_algorithm_v1_75_engineering_handoff_20260916"
AREA = ROOT / "handoffs" / NAME
ARCHIVE = ROOT / "handoffs" / (NAME + ".zip")
RECEIPT = ROOT / "handoffs" / (NAME + "_delivery.json")
CANDIDATE_SHA = "70442cf035a4f2f1416606b13b4b70caff41b810ed9b63be6442c08a432f127f"
EXCLUDED = {"artifact_manifest.json", "MANIFEST.sha256"}
MEDIA_SUFFIXES = {".jpg", ".jpeg", ".png", ".heic", ".mp4", ".mov", ".avi", ".mkv"}
FORBIDDEN_NAMES = {".env", "id_rsa", "id_ed25519"}
FORBIDDEN_SUFFIXES = {".pem", ".p12", ".pfx", ".key"}
SECRET_PATTERNS = (
    re.compile(rb"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(rb"Bearer [A-Za-z0-9._-]{30,}"),
)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    require(AREA.is_dir(), "Handoff directory missing")
    require(not (AREA / "artifact_manifest.json").exists(), "Manifest already exists")
    require(not (AREA / "MANIFEST.sha256").exists(), "SHA manifest already exists")
    require(not ARCHIVE.exists() and not RECEIPT.exists(), "Delivery output already exists")

    paths = sorted(
        path for path in AREA.rglob("*")
        if path.is_file() and path.relative_to(AREA).as_posix() not in EXCLUDED
    )
    require(paths, "Handoff is empty")
    media = []
    secret_like = []
    files = []
    groups = Counter()
    for path in paths:
        relative = path.relative_to(AREA).as_posix()
        groups[relative.split("/", 1)[0]] += 1
        require(path.name not in FORBIDDEN_NAMES, "Forbidden credential filename: " + relative)
        require(path.suffix.lower() not in FORBIDDEN_SUFFIXES,
                "Forbidden credential suffix: " + relative)
        if path.suffix.lower() in MEDIA_SUFFIXES:
            media.append(relative)
        data = path.read_bytes()
        if any(pattern.search(data) for pattern in SECRET_PATTERNS):
            secret_like.append(relative)
        files.append({
            "path": relative,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    require(not media, "Raw media unexpectedly included: " + ", ".join(media[:5]))
    require(not secret_like, "Credential-like value unexpectedly included: " + ", ".join(secret_like))
    require(sha(AREA / "evidence/codex_candidate.json") == CANDIDATE_SHA,
            "Candidate receipt drift")
    candidate = json.loads((AREA / "evidence/codex_candidate.json").read_text(encoding="utf-8"))
    require(len(candidate["source_sha256"]) == 55, "Frozen runtime file count drift")
    for name, digest in candidate["source_sha256"].items():
        require(sha(AREA / name) == digest, "Frozen runtime mismatch: " + name)

    manifest = {
        "artifact": "DIARY_ONE_ALGORITHM_ENGINEERING_HANDOFF",
        "handoff_version": "V1.75-20260916",
        "algorithm_candidate": "V1.75",
        "candidate_receipt_sha256": CANDIDATE_SHA,
        "quality_status": "LOCAL_IMPLEMENTATION_COMPLETE_REAL_V1_75_QUALITY_NOT_VALIDATED",
        "production_ready": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "file_count_excluding_manifests": len(files),
        "total_bytes_excluding_manifests": sum(item["bytes"] for item in files),
        "top_level_counts": dict(sorted(groups.items())),
        "privacy": {
            "raw_media_files": 0,
            "api_keys_or_certificates": 0,
            "private_model_request_response_archives": 0,
            "historical_document_local_paths": "SANITIZED_IN_HANDOFF_COPY",
        },
        "verification": {
            "freeze_environment": "333_EXECUTED_0_SKIPPED_0_FAILED",
            "portable_environment": "307_EXECUTED_26_DECLARED_SKIPPED_0_FAILED",
            "external_calls_for_handoff": 0,
        },
        "files": files,
    }
    with (AREA / "artifact_manifest.json").open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    with (AREA / "MANIFEST.sha256").open("x", encoding="utf-8") as stream:
        for item in files:
            stream.write(item["sha256"] + "  " + item["path"] + "\n")

    subprocess.run(
        [sys.executable, str(AREA / "handoff_support/verify_handoff.py")],
        cwd=AREA, check=True,
    )
    with zipfile.ZipFile(ARCHIVE, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(p for p in AREA.rglob("*") if p.is_file()):
            archive.write(path, (Path(NAME) / path.relative_to(AREA)).as_posix())
    receipt = {
        "artifact": NAME,
        "archive": ARCHIVE.name,
        "archive_bytes": ARCHIVE.stat().st_size,
        "archive_sha256": sha(ARCHIVE),
        "artifact_manifest_sha256": sha(AREA / "artifact_manifest.json"),
        "sha_manifest_sha256": sha(AREA / "MANIFEST.sha256"),
        "candidate_receipt_sha256": CANDIDATE_SHA,
        "production_ready": False,
        "external_calls": 0,
    }
    with RECEIPT.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

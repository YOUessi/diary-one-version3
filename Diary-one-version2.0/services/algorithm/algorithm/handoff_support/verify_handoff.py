"""Verify the V1.75 engineering handoff without network or model calls."""

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_SHA = "70442cf035a4f2f1416606b13b4b70caff41b810ed9b63be6442c08a432f127f"
IGNORED = {"artifact_manifest.json", "MANIFEST.sha256"}
FORBIDDEN_NAMES = {".env", "id_rsa", "id_ed25519"}
FORBIDDEN_SUFFIXES = {".pem", ".p12", ".pfx", ".key"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    manifest_path = ROOT / "artifact_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest["algorithm_candidate"] == "V1.75", "Candidate identity mismatch")
    require(manifest["candidate_receipt_sha256"] == CANDIDATE_SHA,
            "Pinned candidate digest mismatch")
    declared = {item["path"]: item for item in manifest["files"]}
    actual = {
        path.relative_to(ROOT).as_posix(): path
        for path in ROOT.rglob("*")
        if path.is_file() and path.relative_to(ROOT).as_posix() not in IGNORED
    }
    require(set(actual) == set(declared), "Handoff file inventory mismatch")
    for name, path in actual.items():
        item = declared[name]
        require(path.stat().st_size == item["bytes"], "Byte size mismatch: " + name)
        require(sha(path) == item["sha256"], "SHA-256 mismatch: " + name)
        require(path.name not in FORBIDDEN_NAMES and path.suffix.lower() not in FORBIDDEN_SUFFIXES,
                "Forbidden credential-like file: " + name)

    candidate_path = ROOT / "evidence/codex_candidate.json"
    require(sha(candidate_path) == CANDIDATE_SHA, "Candidate receipt drift")
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    require(candidate["quality_status"] == "LOCAL_IMPLEMENTATION_ONLY_FRESH_REAL_CHAIN_NOT_RUN",
            "Quality status was overstated")
    require(len(candidate["source_sha256"]) == 55, "Frozen runtime inventory count drift")
    for name, digest in candidate["source_sha256"].items():
        require(sha(ROOT / name) == digest, "Frozen runtime source drift: " + name)

    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT / "src"))
    from diary_one_ci import codex_d5_research as research
    from diary_one_ci import codex_experience_editor as editor
    require(research.profile() == candidate["research_profile"], "Research profile drift")
    require(editor.POLICY_VERSION == "CODEX_D5_FULL_FACT_AHA_EDITOR_V02",
            "V1.75 editor policy drift")
    print(json.dumps({
        "status": "HANDOFF_VERIFIED",
        "algorithm_candidate": "V1.75",
        "files": len(actual),
        "frozen_runtime_files": len(candidate["source_sha256"]),
        "candidate_receipt_sha256": CANDIDATE_SHA,
        "network_calls": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

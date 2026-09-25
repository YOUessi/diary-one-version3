"""Execute frozen V1.68 in a normal local Chrome/network environment."""

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_WRAPPER = ROOT / "tools/codex_resume_experience_first_v1_68_1.py"
BASE_WRAPPER_SHA = "23d07006ba698e43a4cee5370209aef28389bbcc3b2f3476b464e04034b8584a"
V1681_LOADER = ROOT / "tools/codex_v1681_normalizer_loader.mjs"
V1681_LOADER_SHA = "b55b158473e3401cad266f0a2aad6dd72066d76d15e6595c387a10107dee053e"
V1681_AREA = ROOT / "var/codex_v1_68_1_experience_first_chapter_transport"
V1681_RECEIPT_SHA = "9d12091948cada566758dc6da19a8b3c35395a9edf5947fc025795b31a79493a"
V1681_FAILURES = {
    "1": {"inventory_sha256": "64b9fb66a3e0b04e152759ebb5ee37c1df4f441459e5d6822c1b733820c7f234",
          "normalization_sha256": "907be0dd15d9f95c24f15150559687517b4cc24f39cb192029ceda1f5a9ae958"},
    "2": {"inventory_sha256": "dd40ff007e140783b515837151e968fda69cb1e10b3e295a2d44559335948c40",
          "normalization_sha256": "583f44a01b1b8129b314f38947ecf214a5034b172eb4062f13ea1d6824e5f9dc"},
    "3": {"inventory_sha256": "722e61832ec340f9c341c9737cabddebb9f4cfe55fe2a33603db1277122315e6",
          "normalization_sha256": "ca9f1a38b3fb9abb7b5ad32dd3072b6ada8d80c40c249b47acff19e3bdd40f71"},
}
AREA = ROOT / "var/codex_v1_68_2_experience_first_chapter_execution"
LOADER = ROOT / "tools/codex_v1682_normalizer_loader.mjs"
EXECUTION_REVISION = "V1.68.2_EXECUTION_ENVIRONMENT_ONLY"
sys.dont_write_bytecode = True


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def inventory(root):
    root = Path(root)
    return {path.relative_to(root).as_posix(): sha(path)
            for path in sorted(root.rglob("*")) if path.is_file()}


def inventory_sha(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def save_atomic(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".v1682-final")
    require(not temporary.exists(), "Refusing to replace an existing temporary receipt")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def emit(value):
    print(json.dumps(value, ensure_ascii=False), flush=True)


def load_base():
    require(sha(BASE_WRAPPER) == BASE_WRAPPER_SHA, "Frozen V1.68.1 wrapper drift")
    require(sha(V1681_LOADER) == V1681_LOADER_SHA, "Frozen V1.68.1 loader drift")
    spec = importlib.util.spec_from_file_location("codex_v1681_frozen_wrapper", BASE_WRAPPER)
    require(spec is not None and spec.loader is not None, "Could not load frozen V1.68.1 wrapper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.AREA = AREA
    module.NORMALIZER_LOADER = LOADER
    module.EXECUTION_REVISION = EXECUTION_REVISION
    module.__file__ = str(Path(__file__).resolve())
    return module


def verify_v1681_failure():
    require(sha(V1681_AREA / "codex_execution_revision.json") == V1681_RECEIPT_SHA,
            "V1.68.1 execution receipt drift")
    observed = {}
    for pack_id, expected in V1681_FAILURES.items():
        directory = V1681_AREA / ("pack_" + pack_id) / "round_1"
        files = inventory(directory)
        require(set(files) == {"codex_normalization.json"},
                "V1.68.1 normalization failure evidence changed")
        require(inventory_sha(files) == expected["inventory_sha256"],
                "V1.68.1 normalization failure inventory drift")
        require(files["codex_normalization.json"] == expected["normalization_sha256"],
                "V1.68.1 normalization failure receipt drift")
        record = load(directory / "codex_normalization.json")
        require(record.get("status") == "PREPARATION_FAILED"
                and record.get("manifest_sha256") is None
                and record.get("frames") == [],
                "V1.68.1 failure was not pre-normalization")
        require(not any(directory.rglob("codex_attempt.json"))
                and not any(directory.rglob("codex_full_run.json")),
                "V1.68.1 unexpectedly reached a model attempt")
        observed[pack_id] = {"inventory_sha256": inventory_sha(files), **files}
    return observed


def verify_receipt():
    failures = verify_v1681_failure()
    receipt_path = AREA / "codex_execution_revision.json"
    receipt = load(receipt_path)
    require(receipt.get("execution_revision") == EXECUTION_REVISION, "V1.68.2 identity drift")
    require(receipt.get("wrapper_harness_sha256") == sha(Path(__file__)), "V1.68.2 wrapper drift")
    require(receipt.get("normalizer_loader_sha256") == sha(LOADER), "V1.68.2 loader drift")
    require(receipt.get("superseded_v1_68_1_receipt_sha256") == V1681_RECEIPT_SHA,
            "V1.68.1 supersession receipt missing")
    require(receipt.get("superseded_v1_68_1_failures") == failures,
            "V1.68.1 supersession evidence drift")
    return receipt


def prepare():
    require(not AREA.exists(), "Refusing to overwrite V1.68.2 execution revision")
    failures = verify_v1681_failure()
    base = load_base()
    with contextlib.redirect_stdout(io.StringIO()):
        base.prepare()
    receipt_path = AREA / "codex_execution_revision.json"
    receipt = load(receipt_path)
    receipt.update({
        "execution_revision": EXECUTION_REVISION,
        "execution_environment_change": "NORMAL_LOCAL_CHROME_AND_DIRECT_DASHSCOPE_NETWORK",
        "supersedes_execution_revision": "V1.68.1_TRANSPORT_ONLY",
        "superseded_v1_68_1_receipt_sha256": V1681_RECEIPT_SHA,
        "superseded_v1_68_1_wrapper_sha256": BASE_WRAPPER_SHA,
        "superseded_v1_68_1_loader_sha256": V1681_LOADER_SHA,
        "superseded_v1_68_1_failures": failures,
        "superseded_v1_68_1_model_calls": 0,
        "superseded_v1_68_1_reason": "HEADLESS_CHROME_BLOCKED_BEFORE_DECODE_IN_RESTRICTED_EXECUTION_ENVIRONMENT",
        "finalized_at": now(),
    })
    save_atomic(receipt_path, receipt)
    verify_receipt()
    emit({"event": "V1_68_2_EXECUTION_REVISION_PREPARED_NO_MODEL_CALL", "area": str(AREA),
          "candidate_sha256": receipt["candidate_sha256"], "fresh_normalization_required": ["1", "2", "3"]})


def execute(command, pack_id=None, live=False):
    verify_receipt()
    base = load_base()
    if command == "normalize":
        return base.normalize(pack_id)
    if command == "probe":
        return base.probe()
    return base.run(pack_id, live)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "normalize", "probe", "run"))
    parser.add_argument("--pack", choices=("1", "2", "3"))
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare":
        require(args.pack is None and not args.live, "Prepare is local only")
        prepare()
    elif args.command == "normalize":
        require(args.pack is not None and not args.live, "Normalize requires --pack and is local only")
        execute("normalize", args.pack)
    elif args.command == "probe":
        require(args.pack is None and not args.live, "Probe is an unauthenticated HEAD only")
        execute("probe")
    else:
        require(args.pack is not None, "Run requires --pack")
        sys.exit(execute("run", args.pack, args.live))

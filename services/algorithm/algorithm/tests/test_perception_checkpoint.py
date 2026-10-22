"""Local perception receipts survive restarts without weakening input identity."""

import hashlib
import importlib
import importlib.util
import json
import stat
from concurrent.futures import ThreadPoolExecutor

import pytest


@pytest.fixture
def store_class():
    def create(*args):
        name = "diary_one_ci.perception_checkpoint"
        assert importlib.util.find_spec(name) is not None, "perception checkpoint storage is not implemented"
        return importlib.import_module(name).PerceptionCheckpointStore(*args)
    return create


@pytest.fixture
def identity():
    return {
        "manifest_sha256": "a" * 64,
        "model": "test-vision-v1",
        "provider": "test-local",
        "request_options": {"temperature": 0, "detail": "high"},
        "implementation_sha256": "b" * 64,
    }


@pytest.fixture
def evidence(tmp_path):
    frame = tmp_path / "input" / "frame.jpg"
    frame.parent.mkdir()
    frame.write_bytes(b"exact-image-bytes-not-a-real-image")
    return [({"asset_id": "A1", "media_kind": "PHOTO"},
             {"frame_id": "F1", "relative_path": "frame.jpg", "sha256": "stale-metadata-hash"}, frame)]


@pytest.fixture
def receipt():
    return {
        "stage": "S04_PERCEPTION_BATCH_1",
        "call_status": "COMPLETED",
        "output": {"observations": [{"asset_id": "A1", "description": "a tree"}]},
        "provider": "test-local", "model": "test-vision-v1", "request_id": "r1",
        "input_tokens": 123, "output_tokens": 45, "model_calls": 1,
        "selected_evidence": [{"asset_id": "A1", "frame_id": "F1"}],
    }


def test_relocated_identical_bytes_and_reordered_mappings_reuse_key(store_class, identity, evidence, tmp_path):
    store = store_class(tmp_path / "cache", identity)
    key = store.key("observe", {"type": "object", "required": ["observations"]}, evidence)
    relocated = tmp_path / "second-input" / "different-name.jpg"
    relocated.parent.mkdir()
    relocated.write_bytes(evidence[0][2].read_bytes())
    moved = [(dict(reversed(list(evidence[0][0].items()))), evidence[0][1], relocated)]
    other = store_class(tmp_path / "cache", dict(reversed(list(identity.items()))))
    assert other.key("observe", {"required": ["observations"], "type": "object"}, moved) == key
    assert len(key) == 64


@pytest.mark.parametrize("change", ["bytes", "model", "manifest", "implementation", "options", "prompt", "schema", "asset", "frame", "roles", "order"])
def test_semantic_or_byte_changes_invalidate_key(store_class, identity, evidence, tmp_path, change):
    store = store_class(tmp_path / "cache", identity)
    evidence.append(({"asset_id": "A2"}, {"frame_id": "F2"}, evidence[0][2]))
    key = store.key("observe", {"type": "object"}, evidence)
    prompt, schema = "observe", {"type": "object"}
    if change == "bytes":
        evidence[0][2].write_bytes(b"changed-image-bytes")
    elif change in {"model", "manifest", "implementation", "options"}:
        field = {"manifest": "manifest_sha256", "implementation": "implementation_sha256", "options": "request_options"}.get(change, change)
        identity[field] = "different"
        store = store_class(tmp_path / "cache", identity)
    elif change == "prompt":
        prompt = "observe differently"
    elif change == "schema":
        schema = {"type": "array"}
    elif change == "asset":
        evidence[0][0]["asset_id"] = "changed"
    elif change == "frame":
        evidence[0][1]["frame_id"] = "changed"
    elif change == "roles":
        asset, frame, path = evidence[0]
        evidence[0] = frame, asset, path
    else:
        evidence.reverse()
    assert store.key(prompt, schema, evidence) != key


def test_round_trip_preserves_receipt_and_stores_no_input_payload(store_class, identity, evidence, receipt, tmp_path):
    root = tmp_path / "cache"
    store = store_class(root, identity)
    key = store.key("observe", {}, evidence)
    assert store.load(key) is None
    store.save(key, receipt)
    assert store_class(root, identity).load(key) == receipt
    files = list(root.rglob("*.json"))
    assert len(files) == 1
    encoded = files[0].read_bytes()
    assert evidence[0][2].read_bytes() not in encoded
    assert str(evidence[0][2]).encode() not in encoded
    assert stat.S_IMODE(files[0].stat().st_mode) == 0o600
    assert stat.S_IMODE(files[0].parent.stat().st_mode) == 0o700


@pytest.mark.parametrize("invalid", [
    {"call_status": "FAILED_BEFORE_RESPONSE"},
    {"call_status": "COMPLETED", "output": {"value": object()}},
    {"call_status": "COMPLETED", "output": {"value": float("nan")}},
    {"call_status": "COMPLETED", "api_key": "secret-value"},
    {"call_status": "COMPLETED", "output": {"Authorization": "Bearer secret-value"}},
    {"call_status": "COMPLETED", "output": {"image_base64": "aW1hZ2U="}},
    {"call_status": "COMPLETED", "output": {"url": "data:image/jpeg;base64,aW1hZ2U="}},
    {"call_status": "COMPLETED", "output": {"image": b"image-bytes"}},
])
def test_invalid_receipt_is_rejected_without_poisoning_success(store_class, identity, receipt, invalid, tmp_path):
    store = store_class(tmp_path / "cache", identity)
    key = "c" * 64
    store.save(key, receipt)
    with pytest.raises((ValueError, TypeError)):
        store.save(key, invalid)
    assert store.load(key) == receipt


@pytest.mark.parametrize("corruption", ["truncated", "checksum", "failed", "identity", "key", "oversized", "non_object"])
def test_corrupted_or_mismatched_record_is_safe_miss(store_class, identity, receipt, tmp_path, corruption):
    root = tmp_path / "cache"
    store = store_class(root, identity)
    key = "c" * 64
    store.save(key, receipt)
    path = next(root.rglob("*.json"))
    record = json.loads(path.read_text())
    if corruption == "truncated":
        path.write_bytes(path.read_bytes()[:30])
    elif corruption == "oversized":
        path.write_bytes(b" " * (8 * 1024 * 1024 + 1))
    elif corruption == "non_object":
        path.write_text("[]")
    else:
        if corruption == "checksum":
            record["receipt"]["output"] = {"poison": True}
        else:
            if corruption == "failed":
                record["receipt"]["call_status"] = "FAILED_BEFORE_RESPONSE"
            else:
                record[corruption] = "d" * 64
            payload = {k: v for k, v in record.items() if k != "checksum"}
            record["checksum"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()
        path.write_text(json.dumps(record))
    assert store.load(key) is None


def test_identity_namespace_does_not_reuse_an_existing_key(store_class, identity, receipt, tmp_path):
    root = tmp_path / "cache"
    store_class(root, identity).save("c" * 64, receipt)
    assert store_class(root, {**identity, "model": "different"}).load("c" * 64) is None


def test_symlink_record_is_not_followed(store_class, identity, receipt, tmp_path):
    root = tmp_path / "cache"
    store = store_class(root, identity)
    key = "c" * 64
    store.save(key, receipt)
    path = next(root.rglob("*.json"))
    external = tmp_path / "outside.json"
    path.rename(external)
    path.symlink_to(external)
    assert store.load(key) is None
    original = external.read_bytes()
    store.save(key, {**receipt, "request_id": "replacement"})
    assert external.read_bytes() == original
    assert not path.is_symlink()
    assert store.load(key)["request_id"] == "replacement"


def test_symlink_namespace_is_not_used(store_class, identity, receipt, tmp_path):
    root = tmp_path / "cache"
    store = store_class(root, identity)
    key = "c" * 64
    store.save(key, receipt)
    namespace = next(root.rglob("*.json")).parent
    external = tmp_path / "outside"
    namespace.rename(external)
    namespace.symlink_to(external, target_is_directory=True)
    assert store.load(key) is None
    with pytest.raises(OSError):
        store.save(key, receipt)


def test_oversized_write_and_invalid_key_do_not_create_records(store_class, identity, tmp_path):
    root = tmp_path / "cache"
    store = store_class(root, identity)
    with pytest.raises(ValueError):
        store.save("c" * 64, {"call_status": "COMPLETED", "output": "x" * (8 * 1024 * 1024)})
    with pytest.raises(ValueError):
        store.save("../../escape", {"call_status": "COMPLETED"})
    assert store.load("../../escape") is None
    assert not list(root.rglob("*.json"))


def test_concurrent_atomic_writes_never_expose_partial_receipts(store_class, identity, receipt, tmp_path):
    root = tmp_path / "cache"
    store = store_class(root, identity)
    key = "c" * 64
    first = {**receipt, "output": {"description": "a" * 20000}, "request_id": "first"}
    second = {**receipt, "output": {"description": "b" * 20000}, "request_id": "second"}
    store.save(key, first)

    def write(value):
        for _ in range(40):
            store_class(root, identity).save(key, value)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(write, value) for value in (first, second)]
        for _ in range(100):
            assert store.load(key) in (first, second)
        for future in futures:
            future.result()
    assert store.load(key) in (first, second)
    assert len(list(root.rglob("*.json"))) == 1
    assert not [p for p in root.rglob("*") if p.is_file() and p.suffix != ".json"]

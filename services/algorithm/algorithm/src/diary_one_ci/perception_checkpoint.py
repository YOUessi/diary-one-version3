"""Private local receipts, originally for validated perception batches.

Product editorial calls reuse the persistence mechanism in a separate editorial
namespace: they validate schemas on save/load and still run all semantic gates.
This is input-addressed storage, not an admission decision. Callers must
validate outputs before saving and again after loading. Write and
fingerprinting errors propagate so the caller can log them and continue without
a checkpoint. Read errors are misses. Checksums detect accidental corruption;
they do not authenticate records against someone who can edit the cache.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Mapping, Optional, Sequence, Tuple
import uuid


_FORMAT = "perception-checkpoint-v1"
_MAX_RECORD_BYTES = 8 * 1024 * 1024
_KEY_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
_FORBIDDEN_FIELDS = {
    "apikey", "authorization", "proxyauthorization", "password", "secret",
    "clientsecret", "accesstoken", "refreshtoken", "credential", "credentials",
    "imagebase64", "base64image", "imagebytes", "imagepayload", "base64",
}


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _check_receipt(value: Mapping[str, object]) -> None:
    if value.get("call_status") != "COMPLETED":
        raise ValueError("only COMPLETED perception receipts may be checkpointed")

    def check(item: object) -> None:
        if isinstance(item, Mapping):
            for name, nested in item.items():
                normalized = re.sub(r"[^a-z0-9]", "", str(name).lower())
                if normalized in _FORBIDDEN_FIELDS:
                    raise ValueError("checkpoint receipts must not contain credentials or image payloads")
                check(nested)
        elif isinstance(item, (list, tuple)):
            for nested in item:
                check(nested)
        elif isinstance(item, str) and "data:image/" in item.lower():
            raise ValueError("checkpoint receipts must not contain embedded images")

    check(value)


class PerceptionCheckpointStore:
    """Store JSON receipts in a private namespace derived from full input identity.

    Identity should include the manifest digest, model/provider, request options
    and implementation digests. Metadata must be JSON-compatible and stable
    across relocations (use manifest-relative paths). The evidence Path is used
    only to hash exact bytes and is never serialized into the key or the record.
    Each record is limited to 8 MiB; callers own retention of old namespaces.
    """

    def __init__(self, root: Path, identity: Mapping[str, object]) -> None:
        self.root = Path(root)
        self._identity = hashlib.sha256(_canonical(dict(identity))).hexdigest()
        self._namespace = _FORMAT + "-" + self._identity

    def key(
        self,
        prompt: str,
        schema: Mapping[str, object],
        evidence: Sequence[Tuple[Mapping[str, object], Mapping[str, object], Path]],
    ) -> str:
        fingerprints = []
        for asset, frame, path in evidence:
            digest = hashlib.sha256()
            with Path(path).open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            fingerprints.append({
                "asset": dict(asset), "frame": dict(frame),
                "image_sha256": digest.hexdigest(),
            })
        return hashlib.sha256(_canonical({
            "format": _FORMAT, "identity": self._identity, "prompt": prompt,
            "schema": dict(schema), "evidence": fingerprints,
        })).hexdigest()

    def _open_namespace(self, *, create: bool = False) -> int:
        if create:
            self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        root_fd = os.open(self.root, flags)
        try:
            if create:
                try:
                    os.mkdir(self._namespace, mode=0o700, dir_fd=root_fd)
                except FileExistsError:
                    pass
            namespace_fd = os.open(self._namespace, flags, dir_fd=root_fd)
            try:
                if create:
                    os.fchmod(namespace_fd, 0o700)
                return namespace_fd
            except BaseException:
                os.close(namespace_fd)
                raise
        finally:
            os.close(root_fd)

    def load(self, key: str) -> Optional[Mapping[str, object]]:
        if not isinstance(key, str) or not _KEY_PATTERN.fullmatch(key):
            return None
        try:
            namespace_fd = self._open_namespace()
            try:
                fd = os.open(
                    key + ".json", os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                    dir_fd=namespace_fd,
                )
                with os.fdopen(fd, "rb") as stream:
                    info = os.fstat(stream.fileno())
                    if not stat.S_ISREG(info.st_mode) or info.st_size > _MAX_RECORD_BYTES:
                        return None
                    encoded = stream.read(_MAX_RECORD_BYTES + 1)
            finally:
                os.close(namespace_fd)
            if len(encoded) > _MAX_RECORD_BYTES:
                return None
            record = json.loads(encoded)
            if not isinstance(record, dict):
                return None
            checksum = record.pop("checksum", None)
            if (record.get("format") != _FORMAT or record.get("key") != key
                    or record.get("identity") != self._identity
                    or hashlib.sha256(_canonical(record)).hexdigest() != checksum):
                return None
            receipt = record.get("receipt")
            if not isinstance(receipt, dict):
                return None
            _check_receipt(receipt)
            return receipt
        except (OSError, ValueError, TypeError, UnicodeError, RecursionError):
            return None

    def save(self, key: str, receipt: Mapping[str, object]) -> None:
        if not isinstance(key, str) or not _KEY_PATTERN.fullmatch(key):
            raise ValueError("checkpoint key must be a lowercase SHA256 digest")
        # Snapshot and validate before touching an existing successful record.
        # Preserve provider object order: later prompts may serialize the output
        # verbatim. Checksums/keys remain canonical, payload order does not drift
        # merely because a response was loaded from disk.
        snapshot = json.loads(json.dumps(dict(receipt), ensure_ascii=False, allow_nan=False))
        _check_receipt(snapshot)
        record = {
            "format": _FORMAT, "identity": self._identity, "key": key,
            "receipt": snapshot,
        }
        record["checksum"] = hashlib.sha256(_canonical(record)).hexdigest()
        encoded = json.dumps(record, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
        if len(encoded) > _MAX_RECORD_BYTES:
            raise ValueError("perception checkpoint exceeds 8 MiB record limit")

        namespace_fd = self._open_namespace(create=True)
        temporary = "." + key + "." + uuid.uuid4().hex + ".tmp"
        try:
            fd = os.open(
                temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o600, dir_fd=namespace_fd,
            )
            with os.fdopen(fd, "wb") as stream:
                os.fchmod(stream.fileno(), 0o600)
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(
                temporary, key + ".json",
                src_dir_fd=namespace_fd, dst_dir_fd=namespace_fd,
            )
        finally:
            try:
                os.unlink(temporary, dir_fd=namespace_fd)
            except FileNotFoundError:
                pass
            finally:
                os.close(namespace_fd)

"""Validate uploaded evidence before quota, storage, or billable inference."""
from __future__ import annotations

import hashlib
import io
import json
import re
from pathlib import Path, PurePosixPath

from fastapi import HTTPException
from PIL import Image

from shared.form_fields import read_form_bytes

_RESERVED = {"manifest", "app_client_profile", "day_revision_id"}
_ID = re.compile(r"[A-Za-z0-9_-]{1,200}")


class EvidenceInputError(ValueError):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason

    def detail(self) -> dict:
        return {"code": "EVIDENCE_INPUT_INVALID", "reason": self.reason,
                "retryable": False, "action": "reimport",
                "message": "Evidence failed validation. Select the original media again."}


def _require(condition, reason):
    if not condition:
        raise EvidenceInputError(reason)


def parse_input_manifest(raw: bytes) -> tuple[dict, dict]:
    try:
        manifest = json.loads(raw)
    except (ValueError, TypeError, UnicodeError) as exc:
        raise EvidenceInputError("invalid_input_manifest") from exc
    _require(isinstance(manifest, dict), "invalid_input_manifest")
    session = manifest.get("session")
    _require(isinstance(session, dict) and isinstance(session.get("session_id"), str)
             and bool(session["session_id"].strip()), "invalid_input_session")
    assets = manifest.get("assets")
    _require(isinstance(assets, list) and bool(assets), "missing_input_assets")
    frames, asset_ids, paths = {}, set(), set()
    for asset in assets:
        _require(isinstance(asset, dict), "invalid_input_asset")
        aid = asset.get("asset_id")
        _require(isinstance(aid, str) and bool(aid) and aid not in asset_ids, "invalid_input_asset_identity")
        asset_ids.add(aid)
        _require(asset.get("media_kind") in ("PHOTO", "VIDEO"), "invalid_input_media_kind")
        _require(isinstance(asset.get("frames"), list), "invalid_input_frames")
        for frame in asset["frames"]:
            _require(isinstance(frame, dict), "invalid_input_frame")
            fid, rel = frame.get("frame_id"), frame.get("relative_path")
            _require(isinstance(fid, str) and _ID.fullmatch(fid) and fid not in _RESERVED, "unsafe_frame_id")
            _require(fid not in frames, "duplicate_input_frame")
            _require(isinstance(rel, str) and bool(rel) and "\\" not in rel
                     and chr(0) not in rel and not PurePosixPath(rel).is_absolute() and ".." not in PurePosixPath(rel).parts,
                     "unsafe_evidence_path")
            _require(rel not in paths, "duplicate_evidence_path")
            _require(all(type(frame.get(key)) is int and frame[key] > 0 for key in ("width", "height")),
                     "invalid_evidence_dimensions")
            _require(isinstance(frame.get("sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", frame["sha256"]),
                     "invalid_evidence_hash")
            paths.add(rel)
            frames[fid] = frame
    _require(bool(frames), "missing_input_frame")
    return manifest, frames


def validate_evidence_bytes(content: bytes, frame: dict) -> None:
    _require(hashlib.sha256(content).hexdigest() == frame.get("sha256"), "evidence_hash_mismatch")
    try:
        with Image.open(io.BytesIO(content)) as image:
            _require(image.format == "JPEG" and image.size == (frame.get("width"), frame.get("height")),
                     "evidence_format_or_dimensions_mismatch")
            image.verify()
        with Image.open(io.BytesIO(content)) as image:
            image.load()  # verify() alone does not decode truncated image data.
    except EvidenceInputError:
        raise
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError) as exc:
        raise EvidenceInputError("evidence_decode_failed") from exc


async def read_validated_upload(form) -> tuple[bytes, dict, dict[str, bytes]]:
    """Read each part once. Only manifest-declared, unique frame IDs may be stored."""
    try:
        items = list(form.multi_items())
        keys = [key for key, _ in items]
        _require(len(keys) == len(set(keys)), "duplicate_upload_part")
        raw = await read_form_bytes(form.get("manifest"))
        manifest, frames = parse_input_manifest(raw)
        _require(set(keys) - _RESERVED == set(frames), "uploaded_frame_set_mismatch")
        contents = {}
        for fid, frame in frames.items():
            part = form.get(fid)
            _require(hasattr(part, "read"), "invalid_frame_part")
            data = await part.read()
            validate_evidence_bytes(data, frame)
            contents[fid] = data
        return raw, manifest, contents
    except EvidenceInputError as exc:
        raise HTTPException(status_code=422, detail=exc.detail()) from exc


def validate_stored_evidence(manifest_bytes: bytes, bundle_dir: Path) -> None:
    _, frames = parse_input_manifest(manifest_bytes)
    root = bundle_dir.resolve()
    for fid, frame in frames.items():
        path = (root / frame["relative_path"]).resolve()
        _require(path.is_relative_to(root), "unsafe_evidence_path")
        if not path.is_file():
            path = (root / "frames" / f"{fid}.jpg").resolve()
        _require(path.is_relative_to(root) and path.is_file(), "missing_input_frame")
        try:
            content = path.read_bytes()
        except OSError as exc:
            raise EvidenceInputError("missing_input_frame") from exc
        validate_evidence_bytes(content, frame)


def validate_stored_bundle(bundle_dir: Path) -> None:
    try:
        raw = (bundle_dir / "bundle.json").read_bytes()
    except OSError as exc:
        raise EvidenceInputError("missing_input_manifest") from exc
    validate_stored_evidence(raw, bundle_dir)

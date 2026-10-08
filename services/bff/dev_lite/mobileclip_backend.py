"""
Windows / Dev Lite MobileCLIP backend for POST /v1/evidence/semantic-analyze.

Loads the research embedder from:
  diary_one_app_evidence_v0_2_dev8_mobileclip_router

Env:
  DIARY_ONE_EVIDENCE_ROUTER_ROOT  — package root (default: sibling of diary-one)
  DIARY_ONE_MOBILECLIP_CHECKPOINT — path to mobileclip_s0.pt (required to enable)
  DIARY_ONE_MOBILECLIP_DEVICE     — auto|cpu|cuda|mps (default auto)
  DIARY_ONE_MOBILECLIP_PROMPTS    — 1/0 enable scene prompt labels (default 1)
"""
from __future__ import annotations

import os
import sys
import threading
from pathlib import Path
from typing import Any

import numpy as np

_LOCK = threading.Lock()
_EMBEDDER: Any | None = None
_STATUS: dict[str, Any] = {
    "available": False,
    "reason": "not_initialized",
    "model_id": None,
    "checkpoint": None,
    "device": None,
    "prompts": False,
}


def default_evidence_router_root() -> Path:
    env = (os.environ.get("DIARY_ONE_EVIDENCE_ROUTER_ROOT") or "").strip()
    if env:
        return Path(env).resolve()
    # …/diary-one/services/bff/dev_lite → …/diary_one_app_evidence_v0_2_dev8_mobileclip_router
    here = Path(__file__).resolve()
    # parents[4] = workspace root containing both diary-one and the reference package
    candidate = here.parents[4] / "diary_one_app_evidence_v0_2_dev8_mobileclip_router"
    return candidate.resolve()


def ensure_reference_on_path() -> Path:
    root = default_evidence_router_root()
    src = root / "src"
    if src.is_dir():
        sp = str(src)
        if sp not in sys.path:
            sys.path.insert(0, sp)
    return root


def mobileclip_status() -> dict[str, Any]:
    with _LOCK:
        return dict(_STATUS)


def _pick_device(requested: str) -> str:
    try:
        import torch
    except ImportError:
        return "cpu"
    req = (requested or "auto").strip().lower()
    if req == "cpu":
        return "cpu"
    if req == "cuda":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if req == "mps":
        return "mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available() else "cpu"
    # auto
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def get_embedder() -> Any | None:
    """Lazy-load MobileCLIP embedder. Returns None if unavailable."""
    global _EMBEDDER
    with _LOCK:
        if _EMBEDDER is not None:
            return _EMBEDDER
        ckpt = (os.environ.get("DIARY_ONE_MOBILECLIP_CHECKPOINT") or "").strip()
        if not ckpt:
            _STATUS.update(
                available=False,
                reason="DIARY_ONE_MOBILECLIP_CHECKPOINT not set",
                checkpoint=None,
            )
            return None
        path = Path(ckpt).expanduser().resolve()
        if not path.is_file():
            _STATUS.update(
                available=False,
                reason=f"checkpoint missing: {path}",
                checkpoint=str(path),
            )
            return None

        ensure_reference_on_path()
        try:
            from diary_one_app.engine.semantic import (  # type: ignore
                MOBILECLIP_SCENE_PROMPTS,
                MobileClipSemanticEmbedder,
            )
        except Exception as exc:  # noqa: BLE001
            _STATUS.update(
                available=False,
                reason=f"import diary_one_app failed: {exc}",
                checkpoint=str(path),
            )
            return None

        want_prompts = (os.environ.get("DIARY_ONE_MOBILECLIP_PROMPTS") or "1").strip() not in (
            "0",
            "false",
            "False",
            "no",
        )
        device = _pick_device(os.environ.get("DIARY_ONE_MOBILECLIP_DEVICE") or "auto")
        # Reference ctor only accepts cpu|mps — always construct on cpu, then move.
        ctor_device = "mps" if device == "mps" else "cpu"
        prompts = MOBILECLIP_SCENE_PROMPTS if want_prompts else None
        model_id = (
            "MOBILECLIP_S0_IMAGE_512_SCENE_PROMPTS_V01"
            if prompts
            else "MOBILECLIP_S0_FASTVIT_MCI0_IMAGE_512"
        )
        try:
            embedder = MobileClipSemanticEmbedder(
                path,
                device=ctor_device,
                prompt_labels=prompts,
                model_id=model_id,
            )
        except Exception as exc:  # noqa: BLE001
            # Retry without prompts if apple/ml-mobileclip missing
            if prompts is not None:
                try:
                    embedder = MobileClipSemanticEmbedder(
                        path,
                        device=ctor_device,
                        prompt_labels=None,
                        model_id="MOBILECLIP_S0_FASTVIT_MCI0_IMAGE_512",
                    )
                    prompts = None
                    model_id = embedder.model_id
                except Exception as exc2:  # noqa: BLE001
                    _STATUS.update(
                        available=False,
                        reason=f"MobileCLIP init failed: {exc2}",
                        checkpoint=str(path),
                    )
                    return None
            else:
                _STATUS.update(
                    available=False,
                    reason=f"MobileCLIP init failed: {exc}",
                    checkpoint=str(path),
                )
                return None

        if device == "cuda":
            try:
                import torch

                embedder._model.to("cuda")  # type: ignore[attr-defined]
                embedder.device = "cuda"
            except Exception:  # noqa: BLE001
                device = "cpu"

        _EMBEDDER = embedder
        _STATUS.update(
            available=True,
            reason="ok",
            model_id=model_id,
            checkpoint=str(path),
            device=getattr(embedder, "device", device),
            prompts=bool(prompts),
        )
        return _EMBEDDER


def analyze_jpeg_bytes(blobs: list[bytes]) -> dict[str, Any]:
    """
    Analyze probe JPEGs → API body for the phone remoteSemanticAnalyzer.

    Returns:
      { modelId, degraded, results: [{ vector, classifications }], backend }
    """
    embedder = get_embedder()
    if embedder is None:
        st = mobileclip_status()
        raise RuntimeError(st.get("reason") or "MobileCLIP unavailable")

    import cv2

    images: list[np.ndarray] = []
    for raw in blobs:
        arr = np.frombuffer(raw, dtype=np.uint8)
        bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if bgr is None:
            raise ValueError("failed to decode probe JPEG")
        images.append(bgr)

    embeddings = embedder.analyze_bgr(images)
    results = []
    for emb in embeddings:
        vec = emb.vector
        if hasattr(vec, "tolist"):
            vec = vec.tolist()
        else:
            vec = [float(x) for x in vec]
        results.append(
            {
                "vector": vec,
                "classifications": [
                    {"identifier": c.identifier, "confidence": float(c.confidence)}
                    for c in (emb.classifications or [])
                ],
            }
        )

    st = mobileclip_status()
    return {
        "modelId": st.get("model_id") or getattr(embedder, "model_id", "MOBILECLIP_S0"),
        "degraded": False,
        "backend": "mobileclip_windows",
        "device": st.get("device"),
        "prompts": st.get("prompts"),
        "results": results,
    }

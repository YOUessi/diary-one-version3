from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Sequence, Tuple


AUTO_SOURCE = "DIARY_ONE_AUTO"
MANUAL_SOURCE = "DIARY_ONE_MANUAL"
PHOTO = "PHOTO"
VIDEO = "VIDEO"

AUTO_DURATION_MS = 9_000
AUTO_FRAME_OFFSETS_MS = (1_500, 4_500, 7_500)

MAX_RAW_ASSETS_PER_DAY = 256
MAX_EVIDENCE_WINDOWS_PER_DAY = 320
MAX_REPRESENTATIVE_FRAMES_PER_DAY = 1_024
MAX_MANUAL_VIDEO_DURATION_MS = 120_000
MANUAL_VIDEO_WINDOW_COUNTS = {
    15_000: 2,
    60_000: 4,
    120_000: 6,
}


class EvidencePlanError(ValueError):
    """The daily input cannot produce a trustworthy Evidence plan."""


@dataclass(frozen=True)
class RawAssetSpec:
    raw_asset_id: str
    capture_source: str
    media_kind: str
    captured_at_ms: int
    duration_ms: Optional[int]
    source_ref: str


@dataclass(frozen=True)
class EvidenceWindow:
    window_id: str
    raw_asset_id: str
    capture_source: str
    media_kind: str
    source_start_ms: int
    source_end_ms: int
    timeline_start_ms: int
    timeline_end_ms: int
    windowing_strategy: str


@dataclass(frozen=True)
class EvidenceFramePlan:
    frame_id: str
    window_id: str
    raw_asset_id: str
    frame_index: int
    source_timestamp_ms: Optional[int]
    timeline_timestamp_ms: int


@dataclass(frozen=True)
class EvidencePlan:
    raw_assets: Tuple[RawAssetSpec, ...]
    windows: Tuple[EvidenceWindow, ...]
    frames: Tuple[EvidenceFramePlan, ...]

    @property
    def summary(self) -> Dict[str, object]:
        return {
            "plan_version": "DIARY_ONE_EVIDENCE_PLAN_V01",
            "raw_asset_count": len(self.raw_assets),
            "evidence_window_count": len(self.windows),
            "representative_frame_count": len(self.frames),
            "capacity": {
                "max_raw_assets_per_day": MAX_RAW_ASSETS_PER_DAY,
                "max_evidence_windows_per_day": MAX_EVIDENCE_WINDOWS_PER_DAY,
                "max_representative_frames_per_day": MAX_REPRESENTATIVE_FRAMES_PER_DAY,
            },
        }

    def to_dict(self) -> Dict[str, object]:
        return {
            **self.summary,
            "raw_assets": [asdict(asset) for asset in self.raw_assets],
            "windows": [asdict(window) for window in self.windows],
            "frames": [asdict(frame) for frame in self.frames],
        }


def _validate_raw_asset(asset: RawAssetSpec) -> None:
    if not asset.raw_asset_id.strip():
        raise EvidencePlanError("raw_asset_id must not be empty")
    if not asset.source_ref.strip():
        raise EvidencePlanError(f"{asset.raw_asset_id}: source_ref must not be empty")
    if asset.captured_at_ms < 0 or asset.captured_at_ms >= 86_400_000:
        raise EvidencePlanError(
            f"{asset.raw_asset_id}: captured_at_ms must be inside one local day"
        )
    if asset.capture_source not in (AUTO_SOURCE, MANUAL_SOURCE):
        raise EvidencePlanError(
            f"{asset.raw_asset_id}: unsupported capture_source {asset.capture_source}"
        )
    if asset.media_kind not in (PHOTO, VIDEO):
        raise EvidencePlanError(
            f"{asset.raw_asset_id}: unsupported media_kind {asset.media_kind}"
        )
    if asset.capture_source == AUTO_SOURCE:
        if asset.media_kind != VIDEO or asset.duration_ms != AUTO_DURATION_MS:
            raise EvidencePlanError(
                f"{asset.raw_asset_id}: Auto must be one 9000ms video"
            )
        return
    if asset.media_kind == PHOTO:
        if asset.duration_ms is not None:
            raise EvidencePlanError(
                f"{asset.raw_asset_id}: Manual Photo duration_ms must be null"
            )
        return
    if (
        asset.duration_ms is None
        or asset.duration_ms <= 0
        or asset.duration_ms > MAX_MANUAL_VIDEO_DURATION_MS
    ):
        raise EvidencePlanError(
            f"{asset.raw_asset_id}: Manual Video duration_ms must be 1..120000"
        )
    if asset.duration_ms not in MANUAL_VIDEO_WINDOW_COUNTS:
        raise EvidencePlanError(
            f"{asset.raw_asset_id}: Manual Video duration {asset.duration_ms}ms "
            "has no frozen Evidence Window contract"
        )


def _manual_video_window_count(duration_ms: int) -> int:
    return MANUAL_VIDEO_WINDOW_COUNTS[duration_ms]


def _video_window_bounds(duration_ms: int, window_count: int) -> List[Tuple[int, int]]:
    return [
        (
            duration_ms * index // window_count,
            duration_ms * (index + 1) // window_count,
        )
        for index in range(window_count)
    ]


def _frame_timestamps(start_ms: int, end_ms: int) -> Tuple[int, int]:
    duration_ms = end_ms - start_ms
    return (
        start_ms + duration_ms // 3,
        start_ms + duration_ms * 2 // 3,
    )


def build_evidence_plan(raw_assets: Sequence[RawAssetSpec]) -> EvidencePlan:
    """Build a deterministic, media-free Evidence plan for one user-local day.

    V0.1 implements only the three frozen Manual Video capture modes. Arbitrary
    durations stay contract-invalid until their Window policy is decided. This
    function does not read, create, upload, or model any media.
    """

    if not raw_assets:
        raise EvidencePlanError("daily Evidence plan needs at least one RawAsset")
    if len(raw_assets) > MAX_RAW_ASSETS_PER_DAY:
        raise EvidencePlanError(
            f"raw asset capacity exceeded: {len(raw_assets)} > {MAX_RAW_ASSETS_PER_DAY}"
        )

    seen_ids = set()
    for asset in raw_assets:
        _validate_raw_asset(asset)
        if asset.raw_asset_id in seen_ids:
            raise EvidencePlanError(f"duplicate raw_asset_id: {asset.raw_asset_id}")
        seen_ids.add(asset.raw_asset_id)

    ordered_assets = tuple(
        sorted(raw_assets, key=lambda item: (item.captured_at_ms, item.raw_asset_id))
    )
    windows: List[EvidenceWindow] = []
    frames: List[EvidenceFramePlan] = []

    for asset in ordered_assets:
        if asset.media_kind == PHOTO:
            bounds = [(0, 0)]
            strategy = "MANUAL_PHOTO_SINGLE_EVIDENCE"
        elif asset.capture_source == AUTO_SOURCE:
            bounds = [(0, AUTO_DURATION_MS)]
            strategy = "AUTO_9S_CANONICAL"
        else:
            assert asset.duration_ms is not None
            bounds = _video_window_bounds(
                asset.duration_ms,
                _manual_video_window_count(asset.duration_ms),
            )
            strategy = "MANUAL_CAPTURE_MODE_WINDOW_V01"

        for window_index, (start_ms, end_ms) in enumerate(bounds):
            window_id = f"window_{asset.raw_asset_id}_{window_index + 1:02d}"
            windows.append(
                EvidenceWindow(
                    window_id=window_id,
                    raw_asset_id=asset.raw_asset_id,
                    capture_source=asset.capture_source,
                    media_kind=asset.media_kind,
                    source_start_ms=start_ms,
                    source_end_ms=end_ms,
                    timeline_start_ms=asset.captured_at_ms + start_ms,
                    timeline_end_ms=asset.captured_at_ms + end_ms,
                    windowing_strategy=strategy,
                )
            )

            if asset.media_kind == PHOTO:
                timestamps: Tuple[Optional[int], ...] = (None,)
            elif asset.capture_source == AUTO_SOURCE:
                timestamps = AUTO_FRAME_OFFSETS_MS
            else:
                timestamps = _frame_timestamps(start_ms, end_ms)

            for frame_index, timestamp_ms in enumerate(timestamps):
                frames.append(
                    EvidenceFramePlan(
                        frame_id=f"frame_{window_id}_{frame_index + 1:02d}",
                        window_id=window_id,
                        raw_asset_id=asset.raw_asset_id,
                        frame_index=frame_index,
                        source_timestamp_ms=timestamp_ms,
                        timeline_timestamp_ms=(
                            asset.captured_at_ms
                            if timestamp_ms is None
                            else asset.captured_at_ms + timestamp_ms
                        ),
                    )
                )

    ordered_windows = tuple(
        sorted(windows, key=lambda item: (item.timeline_start_ms, item.window_id))
    )
    ordered_frames = tuple(
        sorted(frames, key=lambda item: (item.timeline_timestamp_ms, item.frame_id))
    )

    if len(ordered_windows) > MAX_EVIDENCE_WINDOWS_PER_DAY:
        raise EvidencePlanError(
            "Evidence window capacity exceeded: "
            f"{len(ordered_windows)} > {MAX_EVIDENCE_WINDOWS_PER_DAY}"
        )
    if len(ordered_frames) > MAX_REPRESENTATIVE_FRAMES_PER_DAY:
        raise EvidencePlanError(
            "representative frame capacity exceeded: "
            f"{len(ordered_frames)} > {MAX_REPRESENTATIVE_FRAMES_PER_DAY}"
        )

    return EvidencePlan(ordered_assets, ordered_windows, ordered_frames)

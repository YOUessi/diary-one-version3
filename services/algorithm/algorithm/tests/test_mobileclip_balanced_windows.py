import copy
import json
import tempfile
from pathlib import Path

import pytest

from diary_one_ci.bundle import load_app_library_bundle
from diary_one_ci.mobileclip_evidence import BALANCED_PROFILE, PROFILE, validate_mobileclip_frames
from test_mobileclip_evidence import MobileClipIntakeTests


def balanced_asset(duration):
    windows = (duration + 9999) // 10000
    return {
        "original_duration_ms": duration, "evidence_sampling_profile": BALANCED_PROFILE,
        "evidence_window_count": windows,
        "frames": [{"source_timestamp_ms": i * duration // windows, "window_index": i,
                    "window_count": windows, "sample_role": "WINDOW_MIDDLE", "canonical_offset_ms": 4500}
                   for i in range(windows)],
    }


@pytest.mark.parametrize("duration", [1, 16, 500, 9999, 10000, 10001, 10010, 20001, 119999, 120000])
def test_balanced_real_pts_and_every_window_are_required(duration):
    asset = balanced_asset(duration)
    validate_mobileclip_frames(asset)
    for frame in asset["frames"]:
        invalid = copy.deepcopy(asset)
        invalid["frames"][frame["window_index"]]["source_timestamp_ms"] = (frame["window_index"] + 1) * duration // asset["evidence_window_count"]
        with pytest.raises(ValueError):
            validate_mobileclip_frames(invalid)


@pytest.mark.parametrize("mutation", ["missing", "wrong_count", "duplicate", "old_layout", "fake_pts"])
def test_bad_balanced_evidence_is_rejected(mutation):
    asset = balanced_asset(10010)
    if mutation == "missing": asset["frames"].pop()
    if mutation == "wrong_count": asset["evidence_window_count"] = 1
    if mutation == "duplicate": asset["frames"][1]["source_timestamp_ms"] = 0
    if mutation == "old_layout": asset["evidence_sampling_profile"] = PROFILE
    if mutation == "fake_pts": asset["frames"][1]["source_timestamp_ms"] = 5005.5
    with pytest.raises(ValueError): validate_mobileclip_frames(asset)


def test_full_bundle_accepts_new_layout_without_relaxing_old_contract():
    with tempfile.TemporaryDirectory() as tmp:
        path, value = MobileClipIntakeTests().make(Path(tmp), 1, 10010)
        asset = value["assets"][1]
        asset["evidence_sampling_profile"] = BALANCED_PROFILE
        asset["frames"][0]["source_timestamp_ms"] = 16
        asset["frames"][1]["source_timestamp_ms"] = 5021
        path.write_text(json.dumps(value))
        assert load_app_library_bundle(path).validation["passed"]
        asset["evidence_sampling_profile"] = PROFILE
        path.write_text(json.dumps(value))
        with pytest.raises(ValueError): load_app_library_bundle(path)

"""Sydney 00:00-01:20 exclusion occurs BEFORE direct VLM input assembly."""
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys
import uuid

import pytest
from diary_one_ci.direct_vlm import guard_sydney_intro_not_in_input
from diary_one_ci.x02 import X02ExecutionError

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts"))
from trim_sydney_intro_for_chapter import create_clean_input  # noqa: E402


def _dataset(tmp_path, clips=(5, 17)):
    inp = tmp_path / "source"
    frames = inp / "frames"
    frames.mkdir(parents=True)
    assets = []
    for index, clip in enumerate(clips):
        aid = f"sydney_04_{clip:06d}"
        fid = aid + "-f0"
        image = frames / (aid + "_f0.jpg")
        image.write_bytes(f"photo from clip {clip}".encode())
        assets.append({
            "asset_id": aid, "sequence_index": index,
            "frames": [{
                "frame_id": fid,
                "relative_path": f"frames/{aid}_f0.jpg",
                "sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
            }],
        })
    sid = str(uuid.uuid4())
    manifest = inp / "bundle.json"
    manifest.write_text(json.dumps({"session": {"session_id": sid}, "assets": assets}))
    timestamps = tmp_path / "timestamps.csv"
    with timestamps.open("w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=("original_clip_id", "start_seconds", "end_seconds"))
        writer.writeheader()
        for clip in clips:
            writer.writerow({"original_clip_id": clip, "start_seconds": (clip - 1) * 10,
                             "end_seconds": clip * 10})
    return manifest, timestamps


@pytest.mark.parametrize("bad_id", ["sydney_00_000001", "sydney_04_000005", "sydney_07_000008"])
def test_legacy_sydney_intro_rejected_before_provider(bad_id):
    with pytest.raises(X02ExecutionError) as exc:
        guard_sydney_intro_not_in_input([{"asset_id": bad_id}])
    assert exc.value.code == "SYDNEY_INTRO_NOT_REMOVED"


def test_other_days_and_after_cutoff_are_not_blocked():
    guard_sydney_intro_not_in_input([{"asset_id": "asset_123"}, {"asset_id": "sydney_08_000009"}])


def test_pre_vlm_cut_physically_omits_intro_images_but_preserves_original(tmp_path):
    source, timestamps = _dataset(tmp_path)
    output = tmp_path / "clean" / "input"
    receipt = create_clean_input(source, timestamps, output, Decimal("80"))
    result = json.loads((output / "bundle.json").read_text())
    assert len(result["assets"]) == 1
    assert result["assets"][0]["asset_id"] == "sydney_04_000017"
    assert result["assets"][0]["sequence_index"] == 0
    assert len(list((output / "frames").glob("*.jpg"))) == 1
    assert receipt["removed_frame_ids"] == ["sydney_04_000005-f0"]
    assert receipt["first_remaining_clip_start_seconds"] == "160"
    assert (source.parent / "frames" / "sydney_04_000005_f0.jpg").is_file()
    assert result["session"]["session_id"] != json.loads(source.read_text())["session"]["session_id"]
    with pytest.raises(FileExistsError):
        create_clean_input(source, timestamps, output, Decimal("80"))


def test_seventy_to_eighty_is_still_intro_and_removed(tmp_path):
    source, timestamps = _dataset(tmp_path, clips=(8, 20))
    receipt = create_clean_input(source, timestamps, tmp_path / "clean" / "input")
    assert receipt["removed_assets"] == 1
    assert receipt["removed_intervals"][0]["crosses_cutoff"] is False
    assert receipt["first_remaining_clip_start_seconds"] == "190"


def test_unknown_absolute_start_fails_not_guessed(tmp_path):
    source, timestamps = _dataset(tmp_path)
    timestamps.write_text("original_clip_id,start_seconds,end_seconds\n17,160,170\n")
    with pytest.raises(ValueError):
        create_clean_input(source, timestamps, tmp_path / "clean" / "input")



def test_cutoff_exactly_eighty_seconds_keeps_clip_starting_80(tmp_path):
    source, timestamps = _dataset(tmp_path, clips=(7, 8, 9, 17))
    output = tmp_path / "cut80" / "input"
    receipt = create_clean_input(source, timestamps, output)
    result = json.loads((output / "bundle.json").read_text())
    assert receipt["source_intro_cutoff_seconds"] == "80"
    assert receipt["removed_assets"] == 2
    assert receipt["first_remaining_clip_start_seconds"] == "80"
    assert [asset["asset_id"] for asset in result["assets"]] == [
        "sydney_04_000009", "sydney_04_000017"]
    assert [asset["sequence_index"] for asset in result["assets"]] == [0, 1]
    guard_sydney_intro_not_in_input(result["assets"])
    with pytest.raises(X02ExecutionError):
        guard_sydney_intro_not_in_input([{"asset_id": "sydney_04_000008"}])

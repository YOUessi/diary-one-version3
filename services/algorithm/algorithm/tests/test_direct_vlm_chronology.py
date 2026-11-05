"""Ensure per-JPEG sequence and source elapsed time actually enter VLM requests."""
import json
from pathlib import Path

import pytest

from diary_one_ci.direct_vlm import frame_chronology_labels, prompt_for_day
from diary_one_ci.x01 import QwenChatCompletionsAdapter
from diary_one_ci.x02 import QwenStageGateway, X02ContractError


def _frame(tmp_path, name, fid, pts=0, seq=0, **extra):
    asset = {"asset_id": name, "sequence_index": seq, "media_kind": "VIDEO", **extra}
    frame = {"frame_id": fid, "canonical_offset_ms": 4500,
             "source_timestamp_ms": pts, "window_count": 1, "window_index": 0}
    image = tmp_path / (fid + ".jpg")
    image.write_bytes(b"synthetic-image")
    return (asset, frame, image)


def test_source_video_timeline_recovers_sydney_120s_spaced_clips(tmp_path):
    evidence = [
        _frame(tmp_path, "sydney_08_000009", "sydney_08_000009-f1", 3003, 0),
        _frame(tmp_path, "sydney_08_000021", "sydney_08_000021-f0", 8008, 1),
    ]
    labels = frame_chronology_labels(evidence)
    assert "CLIP_SEQUENCE_1_BASED=1" in labels["sydney_08_000009-f1"]
    assert "SOURCE_VIDEO_CLIP_START_MS=80000" in labels["sydney_08_000009-f1"]
    assert "SOURCE_VIDEO_FRAME_TIME_MS=83003" in labels["sydney_08_000009-f1"]
    assert "CLIP_SEQUENCE_1_BASED=2" in labels["sydney_08_000021-f0"]
    assert "SOURCE_VIDEO_CLIP_START_MS=200000" in labels["sydney_08_000021-f0"]
    assert "SOURCE_VIDEO_FRAME_TIME_MS=208008" in labels["sydney_08_000021-f0"]
    assert "SOURCE_VIDEO_TIME_IS_RELATIVE_NOT_WALL_CLOCK=true" in labels["sydney_08_000021-f0"]


def test_generic_phone_frames_dont_invent_wall_clock(tmp_path):
    evidence = [_frame(tmp_path, "asset_generic", "frame1", 1000, 17)]
    labels = frame_chronology_labels(evidence)
    assert "CLIP_SEQUENCE_1_BASED=18" in labels["frame1"]
    assert "INTER_CLIP_ELAPSED_TIME_UNKNOWN=true" in labels["frame1"]
    assert "SOURCE_VIDEO_FRAME_TIME_MS" not in labels["frame1"]
    verified = [_frame(tmp_path, "asset_verified", "frame2", 2400, 18,
                       capture_time_ms=1740000000000, capture_time_confidence="VERIFIED",
                       capture_time_source="DEVICE_VERIFIED")]
    assert "VERIFIED_CAPTURE_TIME_UNIX_MS=1740000000000" in frame_chronology_labels(verified)["frame2"]


def test_prompt_requires_time_aware_chapter_boundaries():
    text = prompt_for_day()
    assert "时间线优先" in text
    assert "随着时间推进" in text
    assert "地点、活动或经历主题发生实质变化" in text
    assert "不强制每两分钟" in text
    assert "同一地标" in text


def test_qwen_request_contains_adjacent_chronology_label(tmp_path):
    evidence = [
        _frame(tmp_path, "sydney_08_000009", "sydney_08_000009-f1", 3003, 0),
        _frame(tmp_path, "sydney_08_000021", "sydney_08_000021-f0", 8008, 1),
    ]
    requests = []
    def transport(url, headers, body, timeout):
        payload = json.loads(body)
        blocks = payload["messages"][0]["content"]
        requests.append(blocks)
        assert len(blocks) == 5  # prompt + text/image + text/image
        assert blocks[1]["type"] == "text" and blocks[2]["type"] == "image_url"
        assert "SOURCE_VIDEO_FRAME_TIME_MS=83003" in blocks[1]["text"]
        assert "CLIP_SEQUENCE_1_BASED=2" in blocks[3]["text"]
        assert "SOURCE_VIDEO_FRAME_TIME_MS=208008" in blocks[3]["text"]
        assert blocks[4]["type"] == "image_url"
        answer = {"choices": [{"message": {"content": '{"ok": true}'}}],
                  "usage": {"prompt_tokens": 4, "completion_tokens": 2}}
        return 200, {}, json.dumps(answer).encode()
    adapter = QwenChatCompletionsAdapter(
        api_key="test-only", model="qwen3.8-flash", transport=transport
    )
    result = QwenStageGateway(adapter).call(
        "DIRECT_VLM_GLOBAL_EDITOR", prompt_for_day(), {"type": "object"},
        evidence=evidence,
        context={"_audit_stage_failures": True,
                 "_direct_vlm_frame_chronology": frame_chronology_labels(evidence)},
    )
    assert result.output == {"ok": True}
    assert len(requests) == 1


def test_direct_gateway_refuses_missing_labels_before_billing(tmp_path):
    image = _frame(tmp_path, "asset_1", "frame1", 200, 0)
    calls = []
    def transport(*args):
        calls.append(1)
        raise AssertionError("Must not send unlabelled direct input")
    adapter = QwenChatCompletionsAdapter(api_key="test-only", model="qwen3.8-flash",
                                        transport=transport)
    with pytest.raises(X02ContractError):
        QwenStageGateway(adapter).call(
            "DIRECT_VLM_GLOBAL_EDITOR", "test", {"type": "object"},
            evidence=[image], context={}
        )
    assert not calls

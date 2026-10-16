import unittest
from collections import Counter

from diary_one_ci.evidence import (
    AUTO_SOURCE,
    MANUAL_SOURCE,
    PHOTO,
    VIDEO,
    EvidencePlanError,
    RawAssetSpec,
    build_evidence_plan,
)


def make_high_intensity_day():
    start_ms = 8 * 60 * 60 * 1000
    assets = [
        RawAssetSpec(
            raw_asset_id=f"auto_{index + 1:03d}",
            capture_source=AUTO_SOURCE,
            media_kind=VIDEO,
            captured_at_ms=start_ms + index * 120_000,
            duration_ms=9_000,
            source_ref=f"fixture://auto/{index + 1:03d}",
        )
        for index in range(150)
    ]

    manual_timestamps = [
        start_ms + (index + 1) * (300 * 60 * 1000 // 37)
        for index in range(36)
    ]
    for index in range(20):
        assets.append(
            RawAssetSpec(
                raw_asset_id=f"manual_photo_{index + 1:02d}",
                capture_source=MANUAL_SOURCE,
                media_kind=PHOTO,
                captured_at_ms=manual_timestamps[index],
                duration_ms=None,
                source_ref=f"fixture://manual/photo/{index + 1:02d}",
            )
        )

    manual_video_durations = [15_000] * 10 + [60_000] * 3 + [120_000] * 3
    for index, duration_ms in enumerate(manual_video_durations):
        assets.append(
            RawAssetSpec(
                raw_asset_id=f"manual_video_{index + 1:02d}",
                capture_source=MANUAL_SOURCE,
                media_kind=VIDEO,
                captured_at_ms=manual_timestamps[20 + index],
                duration_ms=duration_ms,
                source_ref=f"fixture://manual/video/{index + 1:02d}",
            )
        )
    return assets


class EvidenceBuilderTests(unittest.TestCase):
    def test_high_intensity_day_builds_expected_capacity(self):
        plan = build_evidence_plan(make_high_intensity_day())

        self.assertEqual(len(plan.raw_assets), 186)
        self.assertEqual(len(plan.windows), 220)
        self.assertEqual(len(plan.frames), 570)
        self.assertEqual(plan.summary["plan_version"], "DIARY_ONE_EVIDENCE_PLAN_V01")

        source_counts = Counter(asset.capture_source for asset in plan.raw_assets)
        kind_counts = Counter(asset.media_kind for asset in plan.raw_assets)
        self.assertEqual(source_counts, {AUTO_SOURCE: 150, MANUAL_SOURCE: 36})
        self.assertEqual(kind_counts, {VIDEO: 166, PHOTO: 20})

    def test_manual_video_duration_controls_window_count(self):
        plan = build_evidence_plan(make_high_intensity_day())
        asset_by_id = {asset.raw_asset_id: asset for asset in plan.raw_assets}
        windows_by_asset = Counter(window.raw_asset_id for window in plan.windows)
        frames_by_asset = Counter(frame.raw_asset_id for frame in plan.frames)

        for raw_asset_id, asset in asset_by_id.items():
            if asset.capture_source == AUTO_SOURCE:
                self.assertEqual(windows_by_asset[raw_asset_id], 1)
                self.assertEqual(frames_by_asset[raw_asset_id], 3)
            elif asset.media_kind == PHOTO:
                self.assertEqual(windows_by_asset[raw_asset_id], 1)
                self.assertEqual(frames_by_asset[raw_asset_id], 1)
            elif asset.duration_ms == 15_000:
                self.assertEqual(windows_by_asset[raw_asset_id], 2)
                self.assertEqual(frames_by_asset[raw_asset_id], 4)
            elif asset.duration_ms == 60_000:
                self.assertEqual(windows_by_asset[raw_asset_id], 4)
                self.assertEqual(frames_by_asset[raw_asset_id], 8)
            elif asset.duration_ms == 120_000:
                self.assertEqual(windows_by_asset[raw_asset_id], 6)
                self.assertEqual(frames_by_asset[raw_asset_id], 12)

    def test_every_window_and_frame_is_traceable_to_raw_asset(self):
        plan = build_evidence_plan(make_high_intensity_day())
        raw_asset_ids = {asset.raw_asset_id for asset in plan.raw_assets}
        window_ids = {window.window_id for window in plan.windows}

        self.assertTrue(all(window.raw_asset_id in raw_asset_ids for window in plan.windows))
        self.assertTrue(all(frame.raw_asset_id in raw_asset_ids for frame in plan.frames))
        self.assertTrue(all(frame.window_id in window_ids for frame in plan.frames))

    def test_windows_and_frames_follow_the_full_day_timeline(self):
        plan = build_evidence_plan(make_high_intensity_day())
        self.assertEqual(
            [window.timeline_start_ms for window in plan.windows],
            sorted(window.timeline_start_ms for window in plan.windows),
        )
        self.assertEqual(
            [frame.timeline_timestamp_ms for frame in plan.frames],
            sorted(frame.timeline_timestamp_ms for frame in plan.frames),
        )

    def test_manual_windows_cover_the_source_without_gaps(self):
        plan = build_evidence_plan(make_high_intensity_day())
        for duration_ms, raw_asset_id in (
            (15_000, "manual_video_01"),
            (60_000, "manual_video_11"),
            (120_000, "manual_video_14"),
        ):
            windows = sorted(
                (
                    window
                    for window in plan.windows
                    if window.raw_asset_id == raw_asset_id
                ),
                key=lambda item: item.source_start_ms,
            )
            self.assertEqual(windows[0].source_start_ms, 0)
            self.assertEqual(windows[-1].source_end_ms, duration_ms)
            self.assertTrue(
                all(
                    current.source_end_ms == following.source_start_ms
                    for current, following in zip(windows, windows[1:])
                )
            )

    def test_input_order_does_not_change_evidence_plan(self):
        assets = make_high_intensity_day()
        forward = build_evidence_plan(assets).to_dict()
        reverse = build_evidence_plan(list(reversed(assets))).to_dict()
        self.assertEqual(forward, reverse)

    def test_duplicate_raw_asset_id_is_rejected(self):
        assets = make_high_intensity_day()
        assets.append(assets[0])
        with self.assertRaisesRegex(EvidencePlanError, "duplicate raw_asset_id"):
            build_evidence_plan(assets)

    def test_invalid_auto_asset_is_rejected(self):
        asset = RawAssetSpec(
            raw_asset_id="bad_auto",
            capture_source=AUTO_SOURCE,
            media_kind=VIDEO,
            captured_at_ms=0,
            duration_ms=15_000,
            source_ref="fixture://bad-auto",
        )
        with self.assertRaisesRegex(EvidencePlanError, "Auto must be one 9000ms video"):
            build_evidence_plan([asset])

    def test_arbitrary_manual_video_duration_is_not_silently_defined(self):
        for duration_ms in (16_000, 73_000):
            asset = RawAssetSpec(
                raw_asset_id=f"manual_{duration_ms}",
                capture_source=MANUAL_SOURCE,
                media_kind=VIDEO,
                captured_at_ms=0,
                duration_ms=duration_ms,
                source_ref=f"fixture://manual/{duration_ms}",
            )
            with self.assertRaisesRegex(
                EvidencePlanError, "has no frozen Evidence Window contract"
            ):
                build_evidence_plan([asset])

    def test_raw_asset_capacity_is_enforced(self):
        assets = [
            RawAssetSpec(
                raw_asset_id=f"photo_{index:03d}",
                capture_source=MANUAL_SOURCE,
                media_kind=PHOTO,
                captured_at_ms=index,
                duration_ms=None,
                source_ref=f"fixture://photo/{index:03d}",
            )
            for index in range(257)
        ]
        with self.assertRaisesRegex(EvidencePlanError, "raw asset capacity exceeded"):
            build_evidence_plan(assets)

    def test_window_capacity_is_enforced(self):
        assets = [
            RawAssetSpec(
                raw_asset_id=f"video_{index:03d}",
                capture_source=MANUAL_SOURCE,
                media_kind=VIDEO,
                captured_at_ms=index,
                duration_ms=120_000,
                source_ref=f"fixture://video/{index:03d}",
            )
            for index in range(54)
        ]
        with self.assertRaisesRegex(EvidencePlanError, "window capacity exceeded"):
            build_evidence_plan(assets)


if __name__ == "__main__":
    unittest.main()

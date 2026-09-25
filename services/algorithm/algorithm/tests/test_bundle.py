import json
import tempfile
import unittest
from pathlib import Path

from diary_one_ci.bundle import (
    APP_LIBRARY_BUNDLE_VERSION,
    APP_LIBRARY_BUNDLE_VERSION_V02,
    APP_LIBRARY_BUNDLE_VERSION_V03,
    BUNDLE_VERSION,
    PHONE_TEST_EVIDENCE_PROFILE_V01,
    load_any_bundle,
    load_bundle,
    run_bundle_e00,
)
from diary_one_ci.core import sha256_file


def make_bundle(root: Path) -> Path:
    media = root / "media"
    media.mkdir(parents=True)
    source = media / "source.json"
    source.write_text(json.dumps({
        "duration_ms": 249000, "width": 120, "height": 160,
        "orientation": "PORTRAIT", "aspect_ratio": "3:4",
    }))
    manifest = {
        "bundle_version": BUNDLE_VERSION, "research_only": True,
        "session": {"session_id": "TEST_001", "exported_at": "2026-08-18T12:00:00+08:00", "timezone": "Asia/Shanghai"},
        "device": {"device_id": "pseudo", "hardware_revision": "test", "firmware_version": "test", "sdk_version": "test"},
        "media_profile": {"profile_id": "TEST", "width": 120, "height": 160, "orientation": "PORTRAIT", "aspect_ratio": "3:4"},
        "source": {"kind": "FIXTURE", "relative_path": "media/source.json", "sha256": sha256_file(source), "duration_ms": 249000},
        "processing": {"capture_interval_ms": 120000, "logical_asset_duration_ms": 9000, "frame_offsets_ms": [1500, 4500, 7500], "materialize_logical_assets": False},
    }
    path = root / "bundle.json"
    path.write_text(json.dumps(manifest))
    return path


def make_app_library_bundle(root: Path) -> Path:
    evidence = root / "evidence"
    evidence.mkdir(parents=True)
    assets = []
    for asset_index, (kind, original_width, original_height, duration_ms) in enumerate([
        ("PHOTO", 4032, 3024, None),
        ("VIDEO", 1920, 1080, 2300),
    ]):
        frames = []
        for frame_index, offset in enumerate((1500, 4500, 7500)):
            frame_path = evidence / f"asset_{asset_index}_frame_{frame_index}.jpg"
            frame_path.write_bytes(f"normalized-{asset_index}-{frame_index}".encode())
            frames.append({
                "frame_id": f"frame_{asset_index}_{frame_index}",
                "canonical_offset_ms": offset,
                "source_timestamp_ms": None if kind == "PHOTO" else [383, 1150, 1917][frame_index],
                "relative_path": f"evidence/{frame_path.name}",
                "sha256": sha256_file(frame_path),
                "width": 768, "height": 1024,
                "spatial_transform": "CENTER_CROP_ASPECT_FILL",
            })
        assets.append({
            "asset_id": f"asset_{asset_index}", "media_kind": kind,
            "original_sha256": f"{asset_index + 1:064x}", "original_bytes": 1000 + asset_index,
            "original_width": original_width, "original_height": original_height,
            "original_duration_ms": duration_ms, "capture_time": None,
            "original_included": False, "timeline_offset_ms": asset_index * 120000,
            "logical_asset_duration_ms": 9000, "materialized_video": False,
            "frames": frames,
        })
    manifest = {
        "bundle_version": APP_LIBRARY_BUNDLE_VERSION, "research_only": True,
        "session": {"session_id": "LIBRARY_TEST_001", "exported_at": "2026-08-18T12:00:00+08:00", "timezone": "Asia/Shanghai"},
        "device": {"device_id": "pseudo", "hardware_revision": "test", "firmware_version": "test", "sdk_version": "test"},
        "normalization": {
            "width": 768, "height": 1024, "orientation": "PORTRAIT", "aspect_ratio": "3:4",
            "spatial_transform": "CENTER_CROP_ASPECT_FILL",
            "temporal_transform": "NORMALIZED_FRACTIONS_TO_CANONICAL_9S",
            "canonical_frame_offsets_ms": [1500, 4500, 7500],
        },
        "assets": assets,
    }
    path = root / "app-library-bundle.json"
    path.write_text(json.dumps(manifest))
    return path


def make_app_library_bundle_v03(root: Path) -> Path:
    path = make_app_library_bundle(root)
    manifest = json.loads(path.read_text())
    manifest["bundle_version"] = APP_LIBRARY_BUNDLE_VERSION_V03
    manifest["session"]["session_id"] = "195d9278-0247-4ac0-bd3c-3acecda5af97"
    manifest["normalization"].update({
        "temporal_transform": PHONE_TEST_EVIDENCE_PROFILE_V01,
        "evidence_profile_version": PHONE_TEST_EVIDENCE_PROFILE_V01,
    })
    for index, asset in enumerate(manifest["assets"]):
        asset.pop("capture_time", None)
        asset.pop("timeline_offset_ms", None)
        asset.update({
            "source_display_name": "asset-%d" % index,
            "media_source": "PHONE_LIBRARY_DAY_TEST",
            "original_file_extension": "jpg" if asset["media_kind"] == "PHOTO" else "mp4",
            "sequence_index": index,
            "evidence_window_count": 1,
            "evidence_sampling_profile": (
                "PHOTO_SINGLE_FRAME"
                if asset["media_kind"] == "PHOTO"
                else "VIDEO_SINGLE_WINDOW_THREE"
            ),
        })
        if asset["media_kind"] == "PHOTO":
            asset["frames"] = [asset["frames"][1]]
            sample_roles = ["PHOTO_REPRESENTATIVE"]
        else:
            sample_roles = ["WINDOW_EARLY", "WINDOW_MIDDLE", "WINDOW_LATE"]
        for frame, sample_role in zip(asset["frames"], sample_roles):
            frame.update({
                "window_index": 0,
                "window_count": 1,
                "sample_role": sample_role,
            })
    path.write_text(json.dumps(manifest))
    return path


class BundleTests(unittest.TestCase):
    def test_bundle_gate_and_e00(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = make_bundle(root)
            self.assertTrue(load_bundle(manifest).validation["passed"])
            run = run_bundle_e00(manifest, root / "artifacts")
            context = json.loads((run / "experiment_context.json").read_text())
            self.assertEqual(context["session"]["session_id"], "TEST_001")

    def test_hash_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = make_bundle(Path(tmp))
            data = json.loads(manifest.read_text())
            data["source"]["sha256"] = "0" * 64
            manifest.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "source_hash"):
                load_bundle(manifest)

    def test_path_escape_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = make_bundle(Path(tmp))
            data = json.loads(manifest.read_text())
            data["source"]["relative_path"] = "../source.json"
            manifest.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "escapes"):
                load_bundle(manifest)

    def test_arbitrary_photo_and_short_landscape_video_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = make_app_library_bundle(root)
            imported = load_any_bundle(manifest)
            self.assertTrue(imported.validation["passed"])
            self.assertEqual(imported.validation["media_kinds"], ["PHOTO", "VIDEO"])
            run = run_bundle_e00(manifest, root / "artifacts")
            result = json.loads((run / "manifest.json").read_text())
            self.assertEqual(result["experiment"], "E00_APP_LIBRARY_SMOKE")
            self.assertFalse(result["leaderboard_eligible"])
            frames = json.loads((run / "frames.json").read_text())
            self.assertEqual(len(frames), 6)
            self.assertTrue(all(frame["aspect_ratio"] == "3:4" for frame in frames))
            self.assertTrue(all(not Path(frame["path"]).is_absolute() for frame in frames))

    def test_app_library_frame_hash_tamper_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = make_app_library_bundle(root)
            data = json.loads(manifest.read_text())
            data["assets"][0]["frames"][0]["sha256"] = "0" * 64
            manifest.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "evidence_hash"):
                load_any_bundle(manifest)

    def test_app_library_bundle_v03_accepts_contiguous_sequence_indices(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = make_app_library_bundle_v03(Path(tmp))
            imported = load_any_bundle(manifest_path)
            self.assertEqual(
                imported.manifest["bundle_version"],
                APP_LIBRARY_BUNDLE_VERSION_V03,
            )
            self.assertEqual(
                imported.validation["validation_version"],
                "APP_LIBRARY_BUNDLE_GATE_V03",
            )
            self.assertEqual(
                [asset["sequence_index"] for asset in imported.manifest["assets"]],
                [0, 1],
            )

    def test_app_library_bundle_v03_requires_sequence_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = make_app_library_bundle_v03(Path(tmp))
            manifest = json.loads(manifest_path.read_text())
            manifest["assets"][0].pop("sequence_index")
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "sequence_index"):
                load_any_bundle(manifest_path)

    def test_app_library_bundle_v03_rejects_out_of_order_sequence_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = make_app_library_bundle_v03(Path(tmp))
            manifest = json.loads(manifest_path.read_text())
            manifest["assets"][1]["sequence_index"] = 2
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "zero-based array position 1"):
                load_any_bundle(manifest_path)

    def test_app_library_bundle_v03_rejects_timeline_offset(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = make_app_library_bundle_v03(Path(tmp))
            manifest = json.loads(manifest_path.read_text())
            manifest["assets"][0]["timeline_offset_ms"] = 0
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "timeline_offset_ms is forbidden"):
                load_any_bundle(manifest_path)

    def test_app_library_bundle_v03_runtime_matches_closed_schema_sections(self):
        mutations = (
            (
                "top-level additional property",
                lambda manifest: manifest.update({"unexpected": True}),
                "bundle has unsupported fields",
            ),
            (
                "session additional property",
                lambda manifest: manifest["session"].update({"unexpected": True}),
                "session has unsupported fields",
            ),
            (
                "session id must be UUID",
                lambda manifest: manifest["session"].update({"session_id": "not-a-uuid"}),
                "session.session_id must be a UUID",
            ),
            (
                "frame additional property",
                lambda manifest: manifest["assets"][0]["frames"][0].update({"unexpected": True}),
                "frames\\[0\\] has unsupported fields",
            ),
            (
                "photo duration must be null",
                lambda manifest: manifest["assets"][0].update({"original_duration_ms": 1}),
                "original_duration_ms must be null for PHOTO",
            ),
            (
                "sample role must match photo",
                lambda manifest: manifest["assets"][0]["frames"][0].update({"sample_role": "WINDOW_EARLY"}),
                "sample roles do not match",
            ),
        )
        for label, mutate, error in mutations:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                manifest_path = make_app_library_bundle_v03(Path(tmp))
                manifest = json.loads(manifest_path.read_text())
                mutate(manifest)
                manifest_path.write_text(json.dumps(manifest))
                with self.assertRaisesRegex(ValueError, error):
                    load_any_bundle(manifest_path)

    def test_app_library_bundle_v03_rejects_schema_type_coercion(self):
        mutations = (
            (
                lambda manifest: manifest["assets"][0].update({"original_bytes": "1000"}),
                "original_bytes must be an integer",
            ),
            (
                lambda manifest: manifest["assets"][1]["frames"][0].update({"window_index": "0"}),
                "window_index must be an integer",
            ),
            (
                lambda manifest: manifest["assets"][1].update({"evidence_window_count": "1"}),
                "evidence_window_count must be an integer",
            ),
            (
                lambda manifest: manifest["assets"][1]["frames"][0].update({"window_count": True}),
                "window_count must be an integer",
            ),
            (
                lambda manifest: manifest["assets"][1]["frames"][0].update({"sha256": "A" * 64}),
                "64 lowercase hexadecimal",
            ),
        )
        for mutate, error in mutations:
            with self.subTest(error=error), tempfile.TemporaryDirectory() as tmp:
                manifest_path = make_app_library_bundle_v03(Path(tmp))
                manifest = json.loads(manifest_path.read_text())
                mutate(manifest)
                manifest_path.write_text(json.dumps(manifest))
                with self.assertRaisesRegex(ValueError, error):
                    load_any_bundle(manifest_path)

    def test_app_library_bundle_v02_historical_manifest_still_loads(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = make_app_library_bundle_v03(Path(tmp))
            manifest = json.loads(manifest_path.read_text())
            manifest["bundle_version"] = APP_LIBRARY_BUNDLE_VERSION_V02
            for asset in manifest["assets"]:
                asset["timeline_offset_ms"] = asset.pop("sequence_index") * 120_000
            manifest_path.write_text(json.dumps(manifest))
            imported = load_any_bundle(manifest_path)
            self.assertEqual(
                imported.validation["validation_version"],
                "APP_LIBRARY_BUNDLE_GATE_V02",
            )

    def test_app_library_bundle_v03_schema_declares_sequence_only_asset_order(self):
        schema_path = Path(__file__).resolve().parents[1] / "contracts" / "app_library_bundle_v03.schema.json"
        schema = json.loads(schema_path.read_text())
        asset_schema = schema["$defs"]["asset"]
        self.assertEqual(
            schema["properties"]["bundle_version"]["const"],
            APP_LIBRARY_BUNDLE_VERSION_V03,
        )
        self.assertFalse(asset_schema["additionalProperties"])
        self.assertIn("sequence_index", asset_schema["required"])
        self.assertNotIn("timeline_offset_ms", asset_schema["properties"])

    def test_app_library_bundle_v03_cannot_fall_back_to_time_shaped_e00(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = make_app_library_bundle_v03(root)
            with self.assertRaisesRegex(
                ValueError,
                "E00 synthesizes time-shaped 120-second offsets",
            ):
                run_bundle_e00(manifest_path, root / "artifacts")

"""Transport/geometry regressions, not synthetic semantic or model-quality tests."""
import json
import tempfile
import unittest
from pathlib import Path

from diary_one_ci.bundle import load_any_bundle, run_bundle_e00
from diary_one_ci.x02 import X02ContractError, run_x02, run_x02_v03
from test_bundle import make_app_library_bundle_v03
from test_x02 import ScriptedGateway, assert_json_schema_instance, make_x02_bundle_v03

ROOT = Path(__file__).resolve().parents[1]
V04 = "DIARY_ONE_APP_LIBRARY_BUNDLE_V04"
FIT = "ASPECT_FIT_LETTERBOX"


def upgrade_to_full_frame(path):
    manifest = json.loads(path.read_text())
    manifest["bundle_version"] = V04
    manifest["normalization"]["spatial_transform"] = FIT
    for asset in manifest["assets"]:
        for frame in asset["frames"]:
            frame["spatial_transform"] = FIT
    path.write_text(json.dumps(manifest))
    return path


def make_x02_bundle_v04(root):
    return upgrade_to_full_frame(make_x02_bundle_v03(root))


class FullFrameBundleTests(unittest.TestCase):
    def test_full_frame_contract_preserves_strict_sequence_envelope(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = upgrade_to_full_frame(make_app_library_bundle_v03(Path(temporary)))
            bundle = load_any_bundle(path)
            self.assertEqual(bundle.validation["validation_version"], "APP_LIBRARY_BUNDLE_GATE_V04")
            self.assertTrue(bundle.validation["checks"]["aspect_fit_letterbox_declared"])
            self.assertNotIn("center_crop_declared", bundle.validation["checks"])
            schema = json.loads((ROOT / "contracts/codex_app_library_bundle_v04.schema.json").read_text())
            assert_json_schema_instance(self, schema, bundle.manifest)
            original = json.loads(path.read_text())
            for where in ("normalization", "frame", "fake_time"):
                altered = json.loads(json.dumps(original))
                if where == "normalization":
                    altered["normalization"]["spatial_transform"] = "CENTER_CROP_ASPECT_FILL"
                elif where == "frame":
                    altered["assets"][0]["frames"][0]["spatial_transform"] = "CENTER_CROP_ASPECT_FILL"
                else:
                    altered["assets"][0]["timeline_offset_ms"] = 0
                path.write_text(json.dumps(altered))
                with self.subTest(where=where), self.assertRaises(ValueError):
                    load_any_bundle(path)

    def test_v03_is_not_silently_redefined_as_full_frame(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = make_app_library_bundle_v03(Path(temporary))
            manifest = json.loads(path.read_text())
            manifest["normalization"]["spatial_transform"] = FIT
            path.write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                load_any_bundle(path)

    def test_full_pipeline_transport_retains_frame_plan_and_actual_version(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = make_x02_bundle_v04(Path(temporary))
            result = run_x02(path, ScriptedGateway())
            counts = {}
            for item in result["decision_trace"]["evidence_selection"]["selected"]:
                key = item["source_asset_id"]
                counts[key] = counts.get(key, 0) + 1
            self.assertEqual(list(counts.values()), [1, 3, 4, 8, 12])
            self.assertEqual(result["trace"]["input_bundle_version"], V04)
            self.assertEqual(result["timeline_basis"], "SYNTHETIC_SEQUENCE_ONLY")
            schema = json.loads((ROOT / "contracts/codex_x02_staged_preview_v04_1_media_v01_input_v04.schema.json").read_text())
            assert_json_schema_instance(self, schema, result)
            with self.assertRaises(X02ContractError):
                run_x02_v03(path, ScriptedGateway())
            with self.assertRaises(ValueError):
                run_bundle_e00(path, Path(temporary) / "e00")

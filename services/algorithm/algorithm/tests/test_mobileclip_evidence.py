import copy
import json
import tempfile
import unittest
import jsonschema
from pathlib import Path
from diary_one_ci.bundle import load_app_library_bundle, APP_LIBRARY_BUNDLE_VERSION_V04
from diary_one_ci.mobileclip_evidence import PROFILE, REPLAY_PROFILE
from test_bundle import make_app_library_bundle_v03

class MobileClipIntakeTests(unittest.TestCase):
    def test_offline_replay_preserves_real_duration_without_phone_padding(self):
        with tempfile.TemporaryDirectory() as tmp:
            path,value=self.make(Path(tmp),2,10000)
            asset=value['assets'][1]
            asset.update(original_duration_ms=10017,evidence_sampling_profile=REPLAY_PROFILE)
            asset['frames'][-1]['source_timestamp_ms']=10005
            path.write_text(json.dumps(value))
            self.assertTrue(load_app_library_bundle(path).validation['passed'])
            asset['evidence_sampling_profile']=PROFILE
            path.write_text(json.dumps(value))
            with self.assertRaises(ValueError):load_app_library_bundle(path)

    def make(self, root, count=2, duration=10000):
        path=make_app_library_bundle_v03(root)
        value=json.loads(path.read_text())
        value['bundle_version']=APP_LIBRARY_BUNDLE_VERSION_V04
        value['normalization']['spatial_transform']='ASPECT_FIT_LETTERBOX'
        for asset in value['assets']:
            for frame in asset['frames']:frame['spatial_transform']='ASPECT_FIT_LETTERBOX'
        asset=value['assets'][1]
        asset.update(original_duration_ms=duration,evidence_sampling_profile=PROFILE,evidence_window_count=(duration+9999)//10000)
        template=asset['frames'][0];asset['frames']=[]
        for window in range(asset['evidence_window_count']):
            for i in range(count):
                frame=copy.deepcopy(template)
                ratio=i/(count-1) if count>1 else .5
                role,offset=('WINDOW_EARLY',1500) if ratio<=.34 else ('WINDOW_LATE',7500) if ratio>=.66 else ('WINDOW_MIDDLE',4500)
                frame.update(frame_id=f'mc-{window}-{i}',window_index=window,window_count=asset['evidence_window_count'],sample_role=role,canonical_offset_ms=offset,source_timestamp_ms=window*10000+i*100)
                asset['frames'].append(frame)
        path.write_text(json.dumps(value));return path,value

    def test_exact_counts_and_twelve_windows(self):
        for count in (1,2,3,4,5,10):
            for duration in (10000,120000):
                with self.subTest(count=count,duration=duration), tempfile.TemporaryDirectory() as tmp:
                    path,value=self.make(Path(tmp),count,duration)
                    result=load_app_library_bundle(path)
                    self.assertTrue(result.validation['passed'])
                    schema=json.loads((Path(__file__).parents[1]/'contracts/codex_app_library_bundle_v04.schema.json').read_text())
                    jsonschema.validate(value,schema)
                    self.assertEqual(len(result.manifest['assets'][1]['frames']),count*((duration+9999)//10000))

    def test_invalid_timeline_windows_and_roles(self):
        for mutation in ('duplicate','outside','missing','role','negative','float'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as tmp:
                path,value=self.make(Path(tmp),2,20000);asset=value['assets'][1]
                if mutation=='duplicate':asset['frames'][1]['source_timestamp_ms']=0
                if mutation=='outside':asset['frames'][0]['source_timestamp_ms']=10000
                if mutation=='missing':asset['frames']=asset['frames'][:2]
                if mutation=='role':asset['frames'][0]['sample_role']='WINDOW_LATE'
                if mutation=='negative':asset['frames'][0]['window_index']=-1
                if mutation=='float':asset['frames'][0]['source_timestamp_ms']=0.5
                path.write_text(json.dumps(value))
                with self.assertRaises(ValueError):load_app_library_bundle(path)

    def test_old_profiles_stay_strict(self):
        for mutation in ('profile','v03'):
            with tempfile.TemporaryDirectory() as tmp:
                path,value=self.make(Path(tmp),2)
                if mutation=='profile':value['assets'][1]['evidence_sampling_profile']='VIDEO_SINGLE_WINDOW_THREE'
                else:
                    value['bundle_version']='DIARY_ONE_APP_LIBRARY_BUNDLE_V03'
                    value['normalization']['spatial_transform']='CENTER_CROP_ASPECT_FILL'
                    for asset in value['assets']:
                        for frame in asset['frames']:frame['spatial_transform']='CENTER_CROP_ASPECT_FILL'
                path.write_text(json.dumps(value))
                with self.assertRaises(ValueError):load_app_library_bundle(path)

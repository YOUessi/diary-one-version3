"""Product-only V05 S04 replay must never exhaust genuine API-attempt quota."""
import dataclasses
import json
from pathlib import Path

from diary_one_ci import x02
from diary_one_ci.bundle import APP_LIBRARY_BUNDLE_VERSION_V05
from test_product_editor import Gateway
from test_x02 import make_x02_bundle_v03


def make_v05(root: Path):
    path = make_x02_bundle_v03(root)
    manifest = json.loads(path.read_text())
    manifest['bundle_version'] = APP_LIBRARY_BUNDLE_VERSION_V05
    manifest['normalization']['spatial_transform'] = 'ASPECT_FIT_LETTERBOX'
    for asset in manifest['assets']:
        asset.update(capture_time_ms=None,
                     capture_time_source='UNKNOWN',
                     capture_time_confidence='UNKNOWN')
        for frame in asset['frames']:
            frame['spatial_transform'] = 'ASPECT_FIT_LETTERBOX'
    path.write_text(json.dumps(manifest))
    return path


class ReplayedS04(Gateway):
    def call(self, stage, prompt, schema, evidence=(), context=None):
        result = super().call(stage, prompt, schema, evidence, context)
        if stage.startswith('S04_PERCEPTION_BATCH_'):
            return dataclasses.replace(
                result, model_calls=0, model_frame_count=0,
                input_tokens=0, output_tokens=0, latency_seconds=0.,
                checkpoint_provenance={
                    'reuse': 'PRIOR_REAL_S04_MATCHED_FRAMES',
                    'prior_input_tokens': result.input_tokens,
                    'prior_output_tokens': result.output_tokens})
        return result


def test_v05_replayed_s04_is_free_against_real_attempt_limit(tmp_path, monkeypatch):
    manifest = make_v05(tmp_path)
    gateway = ReplayedS04()
    result = x02.run_x02_product(manifest, gateway)
    assert result['chapters'] and result['trace']['model_calls'] > 0
    s04 = [s for s in result['trace']['stage_metrics'] if s['stage'].startswith('S04_')]
    assert s04 and all(s['model_calls'] == 0 for s in s04)
    real_attempts = result['trace']['model_calls']
    # Tight quota: enough for all genuinely paid requests but not if an
    # already-paid, zero-cost S04 replay is erroneously charged again.
    monkeypatch.setattr(x02, 'V041_RUN_MAX_MODEL_CALL_ATTEMPTS', real_attempts)
    second = x02.run_x02_product(manifest, ReplayedS04())
    assert second['chapters']
    assert second['decision_trace']['final_verification_terminal_failure'] is False
    editor=second['decision_trace']['editor_input']
    assert editor['global_chapter_plan']['chapter_candidates']
    assert all('anchor_evidence' in item and 'fact_ids' not in item
               for item in editor['global_chapter_plan']['chapter_candidates'])


def test_v05_paid_s04_still_counts_as_real_attempt(tmp_path):
    manifest = make_v05(tmp_path)
    result = x02.run_x02_product(manifest, Gateway())
    assert result['trace']['model_calls'] > 1
    assert result['chapters']

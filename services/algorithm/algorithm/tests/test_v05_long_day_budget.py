"""Bounded cold-start V05 budget; V04 behavior and historical data remain valid."""
from diary_one_ci import x02


def test_legacy_limits_are_unchanged():
    assert x02.V041_RUN_MAX_MODEL_CALL_ATTEMPTS == 96
    assert x02.model_attempt_limit('DIARY_ONE_APP_LIBRARY_BUNDLE_V04',161,True)==96
    assert x02.model_attempt_limit('DIARY_ONE_APP_LIBRARY_BUNDLE_V05',2,True)==96
    assert x02.model_attempt_limit('DIARY_ONE_APP_LIBRARY_BUNDLE_V05',161,False)==96


def test_long_v05_product_has_finite_quota_for_final_image_review():
    assert x02.model_attempt_limit('DIARY_ONE_APP_LIBRARY_BUNDLE_V05',161,True)==180
    assert x02.V05_LONG_DAY_MAX_MODEL_CALL_ATTEMPTS==180
    assert x02.model_attempt_limit('DIARY_ONE_APP_LIBRARY_BUNDLE_V05',32,True)==180


def test_result_schema_supports_old_and_new_operational_quotas():
    from pathlib import Path
    import json
    contract=Path(__file__).resolve().parents[1]/'contracts/x02_staged_preview_v04_1.schema.json'
    data=json.loads(contract.read_text())
    conf=data['$defs']['perceptionBatching']['properties']
    assert conf['run_max_model_call_attempts']=={'enum':[96,180]}
    assert conf['model_call_attempt_count']['maximum']==180
    assert data['properties']['trace']['properties']['model_call_attempted_count']['maximum']==180

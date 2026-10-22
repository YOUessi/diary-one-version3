"""PRD DAT01 / AI03 — result admission contract (keep App deliveryAdmit.ts in sync)."""
from __future__ import annotations

import pytest

from shared.result_admit import apply_admission, build_publish_envelope


def test_ready_admits():
    env = build_publish_envelope(
        {"delivery_state": "READY_PRIMARY_COPY", "schema_version": "x02-preview-v1"},
        bundle_version="V04",
        allow_mock=False,
    )
    assert env["publish_admit"] is True
    assert env["admit_reason"] == "ok"


def test_no_grounded_is_honest_empty():
    env = build_publish_envelope(
        {"delivery_state": "NO_GROUNDED_MEMORY"},
        bundle_version="V04",
        allow_mock=False,
    )
    assert env["publish_admit"] is True
    assert env["admit_reason"] == "no_grounded_memory"
    assert env["fail_job"] is False


def test_mock_blocked_when_disallowed():
    env = build_publish_envelope(
        {"delivery_state": "READY_PRIMARY_COPY", "dev_lite_fallback": True},
        bundle_version="V04",
        allow_mock=False,
    )
    assert env["publish_admit"] is False
    assert env["admit_reason"] == "mock_disallowed"
    assert env["fail_job"] is True


def test_pipeline_blocked_fails():
    env = build_publish_envelope(
        {"delivery_state": "PIPELINE_BLOCKED"},
        bundle_version="V04",
        allow_mock=False,
    )
    assert env["publish_admit"] is False
    assert env["fail_job"] is True


def test_missing_delivery_fails_closed():
    env = build_publish_envelope(
        {"chapters": []},
        bundle_version="V04",
        allow_mock=False,
    )
    assert env["publish_admit"] is False
    assert env["admit_reason"] == "missing_delivery_state"


def test_apply_admission_attaches_envelope():
    result, env = apply_admission(
        {"delivery_state": "READY_WITH_ITEM_BLOCKS"},
        bundle_version="V04",
        allow_mock=False,
    )
    assert result["_publish"] == env
    assert env["publish_admit"] is False
    assert 'missing_input_manifest' in env['admit_reason']


@pytest.mark.parametrize('delivery', [
    'READY_PRIMARY_COPY', 'READY_WITH_GROUNDED_COPY_FALLBACK',
    'READY_WITH_ITEM_BLOCKS', 'STAGED_PREVIEW_DELIVERED', 'NO_GROUNDED_MEMORY',
])
@pytest.mark.parametrize('incomplete', [
    {'coverage_status': 'INCOMPLETE'},
    {'coverage_status': 'PARTIAL_UNRESOLVED'},
    {'unresolved_asset_ids': ['asset-0']},
    {'observations': [{'status': 'FAILED'}]},
], ids=['incomplete-coverage', 'partial-unresolved-coverage', 'unresolved-input', 'failed-observation'])
def test_incomplete_input_cannot_be_admitted_as_ready_or_honest_empty(delivery, incomplete):
    result = {
        'delivery_state': delivery, 'coverage_status': 'COMPLETE',
        'unresolved_asset_ids': [], 'observations': [{'status': 'OBSERVED'}],
        **incomplete,
    }
    env = build_publish_envelope(result, bundle_version='V04', allow_mock=False)

    assert env['publish_admit'] is False, env
    assert env['fail_job'] is True

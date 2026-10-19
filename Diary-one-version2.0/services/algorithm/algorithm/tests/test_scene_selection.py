import json
from pathlib import Path

from diary_one_ci.scene_selection import (
    EXPERIENCE_KINDS, moment_policy_context, policy_for, selection_policy_context,
)


def test_requested_scene_rules_are_distinct_and_reach_both_selection_stages():
    kinds = ('GARDEN', 'CITYWALK', 'OUTDOOR_SCENERY', 'FISHING', 'CYCLING', 'ZOO_ANIMALS', 'MUSEUM')
    editorial, moments = selection_policy_context(), moment_policy_context()
    covers, highlights = set(), set()
    for kind in kinds:
        policy = editorial['policies'][kind]
        covers.add(tuple(policy['cover_priorities']))
        highlights.add(tuple(moments['policies'][kind]['highlight_priorities']))
        assert policy['activation'] and policy['evidence_limits'] and policy['downrank']
    assert len(covers) == len(kinds)
    assert len(highlights) == len(kinds)


def test_unrecognized_source_label_cannot_activate_scene_and_context_is_not_mutable_shared_state():
    assert policy_for('tokyo_zoo__group_01')['experience_kind'] == 'UNCERTAIN'
    first = selection_policy_context()
    first['policies']['MUSEUM']['cover_priorities'].clear()
    assert policy_for('MUSEUM')['cover_priorities']
    assert moment_policy_context()['policies']['MUSEUM']['highlight_priorities']


def test_public_schema_accepts_every_policy_scene():
    schema = json.loads((Path(__file__).resolve().parents[1] / 'contracts/product_preview_v01.schema.json').read_text())
    allowed = schema['$defs']['selection_focus']['properties']['experience_kind']['enum']
    assert set(allowed) == set(EXPERIENCE_KINDS)

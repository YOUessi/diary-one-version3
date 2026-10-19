from final_copy_test_support import write_and_review_with_test_images
from test_product_editor import scripted_final_verdict
"""Offline replay of the real C02 failure; scripted responses test contracts, not model quality.

The recorded source result is retained unchanged under release-v07-20261019-043945.
This minimal fixture is copied verbatim from its audited facts and writer/review rows.
"""
from copy import deepcopy
import json

import jsonschema
import pytest

from diary_one_ci import product_editor as p

SOURCE_RESULT_SHA256 = 'ec0b30f613e14a8f89442f2b3313b8ae8207cc580f2e82113c09d25f4fc553c6'
RECORDED_C02 = json.loads(r'''
{
  "facts": {
    "F005": {
      "asset_id": "V005",
      "evidence_frame_ids": [
        "asset-4-f0",
        "asset-4-f1",
        "asset-4-f2"
      ],
      "fact_id": "1eb8dd41-1246-54d0-b047-c3f5c351ef8f",
      "frame_pts_ms": [
        0,
        4004,
        5005
      ],
      "id": "F005",
      "observation_id": "e6baeda2-259f-5caa-bf6a-dcaad167bb67",
      "original_text": "镜头跟随两名男子穿过铺设红色地砖的宽阔步道，两侧种植棕榈树。远处可见白色石柱门廊结构及一艘停泊的白色船只。",
      "source_asset_id": "asset-4",
      "support_grade": "STRONG",
      "temporal_support": "STATE",
      "text": "镜头跟随两名男子穿过铺设红色地砖的宽阔步道，两侧种植棕榈树。远处可见白色石柱门廊结构及一艘停泊的白色船只。",
      "visual_reviewed": true
    },
    "F006": {
      "asset_id": "V006",
      "evidence_frame_ids": [
        "asset-5-f0",
        "asset-5-f1",
        "asset-5-f2"
      ],
      "fact_id": "c6210a7c-e83d-5d0c-a091-426ddbfa93b3",
      "frame_pts_ms": [
        3003,
        5005,
        9977
      ],
      "id": "F006",
      "observation_id": "312675c6-056c-5951-b185-91a862d31d09",
      "original_text": "视频展示了海滨区域的连续移动画面。起初在沙滩上经过蓝色健身器材和高楼，随后视角转向开阔的海滩，可见海水、远处的山脉以及零散游客。",
      "source_asset_id": "asset-5",
      "support_grade": "STRONG",
      "temporal_support": "CHANGE",
      "text": "视频展示了海滨区域的连续移动画面。起初在沙滩上经过蓝色健身器材和高楼，随后视角转向开阔的海滩，可见海水、远处的山脉以及零散游客。",
      "visual_reviewed": true
    }
  },
  "writer": {
    "id": "C02",
    "story": "沿着铺设红色地砖的宽阔步道前行，两侧棕榈树影婆娑，两名男子在前方行走。远处白色的石柱门廊下停泊着一艘船。视线转向开阔的海滩，海水波光粼粼，背景是连绵的山脉，沙滩上散落着蓝色的健身器材和高楼，零星的游客在海风中漫步。",
    "title": "红砖步道与海滨风光"
  },
  "review": {
    "decision": "PUBLISH",
    "id": "C02",
    "reason": "修正了无依据的修饰词（树影婆娑、波光粼粼、海风），保留核心动作与场景事实。",
    "sentences": [
      {
        "fact_ids": [
          "F005"
        ],
        "source_index": 0,
        "text": "沿着铺设红色地砖的宽阔步道前行，两侧种植棕榈树，两名男子在前方行走。"
      },
      {
        "fact_ids": [
          "F005"
        ],
        "source_index": 1,
        "text": "远处可见白色石柱门廊结构及一艘停泊的白色船只。"
      },
      {
        "fact_ids": [
          "F006"
        ],
        "source_index": 2,
        "text": "视线转向开阔的海滩，海水、远处的山脉以及零散游客可见，沙滩上有蓝色的健身器材和高楼。"
      }
    ],
    "title": "红砖步道与海滨风光",
    "title_fact_ids": [
      "F005",
      "F006"
    ],
    "voice_issues": []
  },
  "original_failed_repair": {
    "decision": "PUBLISH",
    "id": "C02",
    "reason": "修正跨镜头衔接，按证据组独立成句，去除无依据修饰。",
    "sentences": [
      {
        "fact_ids": [
          "F005"
        ],
        "source_index": 0,
        "text": "两名男子穿过铺着红色地砖的宽阔步道，两侧种满棕榈树。"
      },
      {
        "fact_ids": [
          "F005"
        ],
        "source_index": 1,
        "text": "远处立着白色石柱门廊，旁边停泊着一艘白色船只。"
      },
      {
        "fact_ids": [
          "F006"
        ],
        "source_index": 2,
        "text": "视线转向开阔海滩，海水旁是连绵远山，沙滩上有蓝色健身器材和高楼，零散游客在走动。"
      }
    ],
    "title": "红砖步道与海滨漫步",
    "title_fact_ids": [
      "F005",
      "F006"
    ],
    "voice_issues": []
  }
}
''' )


def memory():
    chapter = {'id': 'C02', 'theme': '海滨步道与沙滩观察', 'fact_ids': ['F005', 'F006']}
    return p.memory_specs([chapter], [], deepcopy(RECORDED_C02['facts']))[0]


GOOD_LOCAL_CHANGE = '沙滩边有蓝色健身器材和高楼；视角随后转向开阔海滩，远处是山脉，还有零散游客。'


def run_copy(*, target=GOOD_LOCAL_CHANGE, verdicts=(True, True, True), title_supported=True,
             repair_mutation=None, verify_failure=False, review=None):
    seen = []
    reviewed = deepcopy(review or RECORDED_C02['review'])
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        if stage.endswith("_FINAL_STYLE"):
            raise TimeoutError("Synthetic optional polish outage; retain previously verified local repair")
        seen.append((stage, deepcopy(context)))
        if stage.endswith('_NARRATIVE_BRIEF'):
            output = {'items': [{'id': 'C02', 'details': [{'fact_id': 'F006',
                'evidence_quote': '开阔的海滩', 'role': 'MAIN'}]}]}
        elif stage == 'WRITE':
            output = {'items': [deepcopy(RECORDED_C02['writer'])]}
        elif stage == 'REVIEW':
            output = {'items': [deepcopy(reviewed)]}
        elif stage == 'REPAIR':
            row = deepcopy(reviewed)
            row['removed_source_indices'] = []
            row['sentences'][2]['text'] = target
            if repair_mutation:
                repair_mutation(row)
            output = {'items': [row]}
        elif stage == 'REPAIR_VERIFY':
            if verify_failure:
                raise TimeoutError('injected independent verification failure')
            output = {'items': [{'id': 'C02', 'title_supported': title_supported,
                'title_reason': '依据两条本地事实核验标题',
                'sentences': [{'source_index': i, 'supported': supported,
                               'reason': '句义得到本视频事实支持' if supported else '本视频不支持所写关系'}
                              for i, supported in enumerate(verdicts)]}]}
        else:
            raise AssertionError(stage)
        if not (stage == 'REPAIR' and repair_mutation):
            jsonschema.validate(output, schema)
        return output
    packet = write_and_review_with_test_images([memory()], ('WRITE', 'REVIEW', 'REPAIR'), ask=ask,
                               time_basis='IMPORT_ORDER_ONLY', stage_runs=[])
    return packet, seen


def test_real_c02_failure_is_located_without_treating_change_as_cross_clip_permission():
    frozen = deepcopy(RECORDED_C02)
    item = memory()
    assert item['facts'][1]['temporal_support'] == 'CHANGE'
    for key in ('review', 'original_failed_repair'):
        accepted, ledger = p.compile_copy({'items': [RECORDED_C02[key]]}, [item], review=True)
        assert not accepted and 'CROSS_CLIP_TRANSITION:2' in ledger[0]['reason']
        issue = ledger[0]['copy_issues'][0]
        assert issue['source_index'] == 2 and issue['trigger_text'] == '视线转向'
        assert issue['previous_asset_id'] == 'V005' and issue['asset_id'] == 'V006'
        assert issue['local_change_fact_ids'] == ['F006']
    assert RECORDED_C02 == frozen


def test_real_c02_one_local_repair_and_independent_verdict_preserve_valid_copy():
    packet, calls = run_copy()
    assert [stage for stage, _ in calls] == ['WRITE_NARRATIVE_BRIEF', 'WRITE', 'REVIEW', 'REPAIR', 'REPAIR_VERIFY']
    result = packet['reviewed']['C02']
    assert result['title'] == RECORDED_C02['review']['title']
    assert result['sentences'][:2] == [{k: s[k] for k in ('text', 'fact_ids')}
                                      for s in RECORDED_C02['review']['sentences'][:2]]
    assert result['sentences'][2]['text'] == GOOD_LOCAL_CHANGE
    repair = next(c for s, c in calls if s == 'REPAIR')['items'][0]
    assert 'facts' not in repair and 'evidence_groups' not in repair
    assert [f['id'] for f in repair['target_sentences'][0]['facts']] == ['F006']
    assert repair['target_sentences'][0]['facts'][0]['temporal_support'] == 'CHANGE'
    verify = calls[-1][1]['items'][0]
    assert verify['review_mode'] == 'LOCAL_COPY_VERDICTS'
    assert '红色地砖' not in str(verify['sentence_checks'][2]['facts'])
    assert 'draft' not in verify and 'facts' not in verify


def test_replacing_connector_does_not_make_cross_clip_route_true():
    wrong = '红砖步道直通这片海滩，白船就停在蓝色健身器材旁。'
    packet, _ = run_copy(target=wrong, verdicts=(True, True, False))
    result = packet['reviewed']['C02']
    assert wrong not in result['story'] and len(result['sentences']) == 2
    assert packet['repair_verification_ledger'][0]['sentence_verification'][2]['status'] == 'REMOVED'


def test_semantic_supported_cannot_waive_unresolved_cross_clip_guard():
    packet, _ = run_copy(target=RECORDED_C02['review']['sentences'][2]['text'])
    assert packet['repair_ledger'][0]['status'] == 'PENDING_LOCAL_VERIFICATION'
    assert len(packet['reviewed']['C02']['sentences']) == 2
    assert packet['repair_verification_ledger'][0]['sentence_verification'][2]['reason'] == 'UNRESOLVED_CROSS_CLIP_TRANSITION'


@pytest.mark.parametrize('title_supported,verdicts', [(False, (True, True, True)), (True, (False, False, False))])
def test_unsupported_title_or_all_invalid_sentences_still_block(title_supported, verdicts):
    packet, _ = run_copy(title_supported=title_supported, verdicts=verdicts)
    assert not packet['reviewed']
    assert packet['repair_verification_ledger'][0]['status'] == 'BLOCKED'


@pytest.mark.parametrize('mutation', [
    lambda r: r.update(title='好友通勤的海边'),
    lambda r: r['sentences'][0].update(text='好友在红砖路上休息。'),
    lambda r: r['sentences'][2].update(fact_ids=['F005']),
    lambda r: r['sentences'][2].update(fact_ids=['F999']),
    lambda r: r.update(removed_source_indices=[0]),
])
def test_malformed_or_false_repair_cannot_reuse_protected_copy_as_fallback(mutation):
    packet, calls = run_copy(repair_mutation=mutation)
    assert not packet['reviewed']
    assert 'REPAIR_VERIFY' not in [stage for stage, _ in calls]
    assert packet['repair_ledger'][0]['status'] == 'BLOCKED'


def test_verification_transport_failure_cannot_publish_provisional_repair():
    packet, _ = run_copy(verify_failure=True)
    assert not packet['reviewed']


def test_clean_chapter_does_not_get_additional_repair_calls():
    reviewed = deepcopy(RECORDED_C02['review'])
    reviewed['sentences'][2]['text'] = GOOD_LOCAL_CHANGE
    packet, calls = run_copy(review=reviewed)
    assert packet['reviewed']['C02']
    assert [s for s, _ in calls] == ['WRITE_NARRATIVE_BRIEF', 'WRITE', 'REVIEW']


def test_first_review_block_or_identity_error_cannot_be_partially_trusted():
    item = memory()
    for mutation in ('blocked', 'identity', 'title'):
        row = deepcopy(RECORDED_C02['review'])
        if mutation == 'blocked': row['decision'] = 'BLOCK'
        elif mutation == 'identity': row['sentences'][0]['text'] = '和好友沿红砖路前行。'
        else: row['title'] = '下班通勤'
        assert p.local_repair_scope(item, row) is None


# Exact model payload from the first fresh V07.1 attempt; the missing items
# envelope is intentional. Retained without edits to its wording or references.
RECORDED_FRESH_C02 = json.loads(r'''
{
  "source_sha256": "044890fd9c407de171b72aad363609670888a26532f73e6f736e59348048d044",
  "facts": {
    "F005": {
      "evidence_frame_ids": [
        "asset-4-f0",
        "asset-4-f1",
        "asset-4-f2"
      ],
      "fact_id": "1eb8dd41-1246-54d0-b047-c3f5c351ef8f",
      "support_grade": "STRONG",
      "text": "镜头跟随两名男子穿过铺设红色地砖的宽阔步道，两侧种植棕榈树。远处可见白色石柱门廊结构及一艘停泊的白色船只。",
      "id": "F005",
      "asset_id": "V005",
      "source_asset_id": "asset-4",
      "observation_id": "e6baeda2-259f-5caa-bf6a-dcaad167bb67",
      "frame_pts_ms": [
        0,
        4004,
        5005
      ],
      "temporal_support": "STATE",
      "visual_reviewed": true,
      "original_text": "镜头跟随两名男子穿过铺设红色地砖的宽阔步道，两侧种植棕榈树。远处可见白色石柱门廊结构及一艘停泊的白色船只。"
    },
    "F006": {
      "evidence_frame_ids": [
        "asset-5-f0",
        "asset-5-f1",
        "asset-5-f2"
      ],
      "fact_id": "c6210a7c-e83d-5d0c-a091-426ddbfa93b3",
      "support_grade": "STRONG",
      "text": "视频展示了海滨区域的连续移动画面。起初在沙滩上经过蓝色健身器材和高楼，随后视角转向开阔的海滩，可见海水、远处的山脉以及零散游客。",
      "id": "F006",
      "asset_id": "V006",
      "source_asset_id": "asset-5",
      "observation_id": "312675c6-056c-5951-b185-91a862d31d09",
      "frame_pts_ms": [
        3003,
        5005,
        9977
      ],
      "temporal_support": "CHANGE",
      "visual_reviewed": true,
      "original_text": "视频展示了海滨区域的连续移动画面。起初在沙滩上经过蓝色健身器材和高楼，随后视角转向开阔的海滩，可见海水、远处的山脉以及零散游客。"
    }
  },
  "writer": {
    "id": "C02",
    "title": "红砖步道与开阔海滩",
    "story": "沿着铺设红色地砖的宽阔步道前行，两侧种植着棕榈树，远处可见白色石柱门廊结构及一艘停泊的白色船只。随后视角转向开阔的海滩，海水与远处的山脉映入眼帘，零散的游客散布其间。"
  },
  "review": {
    "id": "C02",
    "decision": "PUBLISH",
    "reason": "事实与表达一致",
    "title": "红砖步道与开阔海滩",
    "title_fact_ids": [
      "F005",
      "F006"
    ],
    "sentences": [
      {
        "source_index": 0,
        "text": "沿着铺设红色地砖的宽阔步道前行，两侧种植着棕榈树，远处可见白色石柱门廊结构及一艘停泊的白色船只。",
        "fact_ids": [
          "F005"
        ]
      },
      {
        "source_index": 1,
        "text": "随后视角转向开阔的海滩，海水与远处的山脉映入眼帘，零散的游客散布其间。",
        "fact_ids": [
          "F006"
        ]
      }
    ],
    "voice_issues": []
  },
  "repair": {
    "id": "C02",
    "decision": "PUBLISH",
    "reason": "已修复跨片衔接问题，明确V006片段内的起始场景及视角变化。",
    "title": "红砖步道与开阔海滩",
    "title_fact_ids": [
      "F005",
      "F006"
    ],
    "sentences": [
      {
        "source_index": 0,
        "text": "沿着铺设红色地砖的宽阔步道前行，两侧种植着棕榈树，远处可见白色石柱门廊结构及一艘停泊的白色船只。",
        "fact_ids": [
          "F005"
        ]
      },
      {
        "source_index": 1,
        "text": "镜头起于沙滩上的蓝色健身器材和高楼，随即转向开阔的海滩，海水、远山与零散游客映入眼帘。",
        "fact_ids": [
          "F006"
        ]
      }
    ],
    "voice_issues": [],
    "removed_source_indices": []
  }
}
''')


def fresh_copy_replay(*, mutate_repair=None, bare_verify=False, verify_reject=False):
    fixture = RECORDED_FRESH_C02
    item = p.memory_specs([{'id': 'C02', 'theme': '海滨步道与海滩', 'fact_ids': ['F005', 'F006']}],
                          [], deepcopy(fixture['facts']))[0]
    calls = []
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        if stage.endswith("_FINAL_STYLE"):
            raise TimeoutError("Synthetic optional polish outage; retain previously verified local repair")
        calls.append(stage)
        if stage == 'WRITE_NARRATIVE_BRIEF':
            return {'items': [{'id': 'C02', 'details': [{'fact_id': 'F006',
                'evidence_quote': '海滩', 'role': 'MAIN'}]}]}
        if stage == 'WRITE':
            return {'items': [deepcopy(fixture['writer'])]}
        if stage == 'REVIEW':
            return {'items': [deepcopy(fixture['review'])]}
        if stage == 'REPAIR':
            response = deepcopy(fixture['repair'])
            if mutate_repair:
                mutate_repair(response)
            return response
        if stage == 'REPAIR_VERIFY':
            response = {'id': 'C02', 'title_supported': True, 'title_reason': '标题对应两段海滨事实',
                'sentences': [{'source_index': index, 'supported': not verify_reject,
                    'reason': '根据本句证据进行独立判断'} for index in range(2)]}
            return response if bare_verify else {'items': [response]}
        raise AssertionError(stage)
    return write_and_review_with_test_images([item], ('WRITE', 'REVIEW', 'REPAIR'), ask=ask,
                             time_basis='IMPORT_ORDER_ONLY', stage_runs=[]), calls, item


@pytest.mark.parametrize('bare_verify', [False, True])
def test_fresh_real_single_object_repair_reaches_independent_verification(bare_verify):
    original = deepcopy(RECORDED_FRESH_C02)
    packet, calls, _ = fresh_copy_replay(bare_verify=bare_verify)
    assert calls == ['WRITE_NARRATIVE_BRIEF', 'WRITE', 'REVIEW', 'REPAIR', 'REPAIR_VERIFY']
    assert packet['reviewed']['C02']['story'] == ''.join(s['text'] for s in original['repair']['sentences'])
    assert packet['repair_output'] == original['repair'] and 'items' not in packet['repair_output']
    assert [row['stage'] for row in packet['copy_response_normalizations']] == (
        ['REPAIR', 'REPAIR_VERIFY'] if bare_verify else ['REPAIR'])
    assert all(row['rule'] == 'EXACT_SINGLE_ITEM_SCHEMA_VALID_ENVELOPE'
               and row['raw_sha256'] != row['normalized_sha256']
               for row in packet['copy_response_normalizations'])
    assert RECORDED_FRESH_C02 == original


@pytest.mark.parametrize('mutation', [
    lambda r: r.update(id='C99'),
    lambda r: r.update(items=[]),
    lambda r: r.update(unknown='not permitted'),
    lambda r: r.pop('removed_source_indices'),
    lambda r: r['sentences'][1].update(fact_ids=['F005']),
    lambda r: r['sentences'][1].update(fact_ids=['F999']),
    lambda r: r['sentences'][0].update(text='和好友从红砖步道抵达海滩。'),
    lambda r: r['sentences'][1].update(source_index=True),
])
def test_single_object_adapter_never_fills_or_repairs_content(mutation):
    packet, calls, _ = fresh_copy_replay(mutate_repair=mutation)
    assert not packet['reviewed'] and 'REPAIR_VERIFY' not in calls
    assert not packet['copy_response_normalizations']
    assert packet['repair_ledger'][0]['id'] == 'C02'
    assert packet['repair_ledger'][0]['stage'] == 'REPAIR'
    assert packet['repair_ledger'][0]['status'] == 'BLOCKED'
    assert 'response' in packet['repair_ledger'][0]['reason']


def test_single_object_cannot_choose_one_target_from_a_multi_target_repair():
    _, _, item = fresh_copy_replay()
    other = {**deepcopy(item), 'id': 'C03'}
    with pytest.raises(ValueError, match='envelope'):
        p.normalize_single_copy_response(RECORDED_FRESH_C02['repair'], [item, other],
            p.copy_schema([item, other], review=True), stage='REPAIR')


def test_corrected_envelope_is_not_semantic_permission_or_raw_draft_fallback():
    packet, calls, _ = fresh_copy_replay(verify_reject=True)
    assert 'REPAIR_VERIFY' in calls and not packet['reviewed']
    assert packet['copy_response_normalizations']
    assert packet['repair_verification_ledger'][0]['status'] == 'BLOCKED'


@pytest.mark.parametrize('reason', [123, True, None, [], '   '])
def test_local_title_verdict_requires_nonempty_string_in_canonical_envelope(reason):
    item = memory()
    item['local_repair_scope'] = p.local_repair_scope(item, RECORDED_C02['review'])
    row = deepcopy(RECORDED_C02['review'])
    row.update(removed_source_indices=[])
    row['sentences'][2]['text'] = GOOD_LOCAL_CHANGE
    compiled, _ = p.sentence_verification_items([item], {'items': [row]})
    verdict = {'items': [{'id': 'C02', 'title_supported': True, 'title_reason': reason,
        'sentences': [{'source_index': index, 'supported': True, 'reason': '本句成立'} for index in range(3)]}]}
    accepted, ledger = p.compile_repair_verification(verdict, compiled)
    assert not accepted and ledger[0]['status'] == 'BLOCKED'
    assert 'title failed' in ledger[0]['reason']

"""V2 preferences must coexist with V07 evidence, media and publication gates."""
import json
import jsonschema
import http.client
import threading
from unittest.mock import patch

from diary_one_ci import app_client_profile as profile
from diary_one_ci.x02 import run_x02, run_x02_product
from diary_one_ci.x01_server import make_server
from test_product_editor import Gateway
from test_x02 import make_x02_bundle, ScriptedGateway, X02_V041_PREVIEW_SCHEMA_PATH


class RecordingGateway(Gateway):
    def __init__(self):
        super().__init__()
        self.requests = []

    def call(self, stage, prompt, schema, evidence=(), context=None):
        self.requests.append((stage, prompt, context, tuple(evidence)))
        return super().call(stage, prompt, schema, evidence, context)


def test_v2_profile_cannot_replace_v07_evidence_or_publication(tmp_path):
    manifest = make_x02_bundle(tmp_path, 1)
    original_gateway = RecordingGateway()
    original = run_x02_product(manifest, original_gateway)
    assert 'client_profile_audit' not in original['decision_trace']

    profile.write_profile(manifest.parent, json.dumps({
        'schema_version': profile.POLICY_VERSION,
        'writing_style': '自然具体',
        'boost_tags': ['UNSEEN_PREFERENCE_SUBJECT'],
        'avoid_topics': ['街边'],
    }).encode())
    gateway = RecordingGateway()
    result = run_x02_product(manifest, gateway)
    assert result['editor_policy'] == original['editor_policy']
    assert result['delivery_state'] == original['delivery_state'] == 'READY_PRIMARY_COPY'
    assert result['chapters'] == original['chapters']
    assert result['ahas'] == original['ahas']
    assert result['decision_trace']['verified_facts'] == original['decision_trace']['verified_facts']
    assert len(gateway.requests) == len(original_gateway.requests)
    audit = result['decision_trace']['client_profile_audit']
    assert audit['present'] is True
    assert 'S11_PRODUCT_WRITER' in audit['stages']
    assert len(audit['instruction_sha256']) == 64
    original_requests = {s: (p, c, e) for s, p, c, e in original_gateway.requests}
    for stage, prompt, context, evidence in gateway.requests:
        if stage in profile.PRODUCT_EDITORIAL_STAGES:
            assert 'UNSEEN_PREFERENCE_SUBJECT' in prompt
            assert context['app_client_profile']['present'] is True
            assert evidence == original_requests[stage][2]
        else:
            # Especially perception, visual checks, moment value and fact review.
            assert (prompt, context, evidence) == original_requests[stage]


def test_no_profile_preserves_original_model_requests():
    def call(*args, **kwargs):
        raise AssertionError('Construction must not call a model')
    wrapped, audit = profile.product_editor_call(call, profile.empty_profile())
    assert wrapped is call
    assert audit['present'] is False
    assert audit['stages'] == []


def test_soft_order_preserves_chapter_ids_evidence_and_nested_highlights():
    chapters = [
        {'id': 'c1', 'title': '工作', 'claims': [{'fact_id': 'f1'}], 'highlights': [{'parent_chapter_id': 'c1'}]},
        {'id': 'c2', 'title': '园林池塘', 'claims': [{'fact_id': 'f2'}], 'highlights': []},
    ]
    selected, audit = profile.apply_soft_editorial(chapters, profile.normalize_profile({
        'boost_tags': ['园林'], 'avoid_topics': ['工作'],
    }))
    assert selected == [chapters[1], chapters[0]]
    assert chapters[0]['id'] == 'c1'
    assert audit['applied'] is True


def test_legacy_profile_keeps_existing_closed_public_contract(tmp_path):
    manifest = make_x02_bundle(tmp_path, 1)
    profile.write_profile(manifest.parent, json.dumps({
        'schema_version': profile.POLICY_VERSION, 'writing_style': '自然具体',
    }).encode())
    result = run_x02(manifest, ScriptedGateway())
    assert 'client_profile_audit' not in result
    assert result['decision_trace']['client_profile_audit']['present'] is True
    jsonschema.validate(result, json.loads(X02_V041_PREVIEW_SCHEMA_PATH.read_text()))


def test_http_rejects_bad_or_duplicate_profiles_before_any_pipeline(tmp_path):
    server = make_server('127.0.0.1', 0, adapter_name='fixture',
                         run_audit_dir=tmp_path / 'x01', x02_run_audit_dir=tmp_path / 'x02')
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with patch('diary_one_ci.x01_server.run_x02') as legacy, \
             patch('diary_one_ci.x01_server.run_x02_product') as product:
            for profile_parts in ([b'[]'], [b'{"schema_version":"V99"}'],
                                  [b'{"boost_tags":"cycling"}'], [b'{}', b'{}']):
                parts = [('manifest', b'{"assets":[{"frames":[]}]}')]
                parts.extend(('app_client_profile', value) for value in profile_parts)
                body = b''.join(
                    b'--profile-boundary\r\nContent-Disposition: form-data; name="' + name.encode()
                    + b'"\r\n\r\n' + value + b'\r\n' for name, value in parts
                ) + b'--profile-boundary--\r\n'
                connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
                try:
                    connection.request('POST', '/x02/v0.4.1/preview', body=body,
                                       headers={'Content-Type': 'multipart/form-data; boundary=profile-boundary'})
                    response = connection.getresponse()
                    payload = json.loads(response.read())
                    assert response.status == 422, payload
                    assert 'app_client_profile' in payload['message']
                finally:
                    connection.close()
            legacy.assert_not_called()
            product.assert_not_called()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

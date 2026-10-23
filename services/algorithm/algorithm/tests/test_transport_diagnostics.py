import dataclasses
import http.client
import json
import urllib.error

import pytest

from diary_one_ci import x02
from diary_one_ci.x01 import QwenChatCompletionsAdapter


def test_failure_diagnostics_preserve_cause_without_secrets():
    def broken(*args):
        try:
            raise ConnectionResetError(54, 'Bearer secret-key https://user:password@host/?token=secret')
        except OSError as inner:
            raise urllib.error.URLError(inner) from inner
    gateway = x02.QwenStageGateway(QwenChatCompletionsAdapter(api_key='not-real', transport=broken))
    with pytest.raises(x02.X02StageCallError) as failure:
        gateway.call('TEST', 'private prompt', {}, context={'_audit_stage_failures': True})
    diagnostic = dataclasses.asdict(failure.value.stage_run)['transport_diagnostics']
    assert any(row.get('errno') == 54 for row in diagnostic['exception_chain'])
    encoded = json.dumps(diagnostic)
    assert all(secret not in encoded for secret in ('secret-key', 'password', 'private prompt', 'Bearer'))


def test_partial_response_retains_request_id_and_phase(monkeypatch):
    from diary_one_ci.transport_diagnostics import DiagnosticTransport
    class Response:
        status = 200
        headers = {'X-Request-Id': 'provider-123', 'Set-Cookie': 'private-cookie'}
        def read(self):
            raise http.client.IncompleteRead(b'private partial response', 100)
        def close(self):
            pass
    class Opener:
        def open(self, request, timeout):
            return Response()
    monkeypatch.setattr('urllib.request.build_opener', lambda *handlers: Opener())
    transport = DiagnosticTransport(proxy_mode='DIRECT')
    gateway = x02.QwenStageGateway(QwenChatCompletionsAdapter(api_key='not-real', transport=transport))
    with pytest.raises(x02.X02StageCallError) as failure:
        gateway.call('TEST', 'prompt', {}, context={'_audit_stage_failures': True})
    run = failure.value.stage_run
    assert run.request_id == 'provider-123'
    assert run.transport_diagnostics['phase'] == 'RESPONSE_BODY'
    assert run.transport_diagnostics['response_headers_received'] is True
    assert 'private' not in json.dumps(run.transport_diagnostics)


def test_proxy_mode_does_not_change_body_or_global_opener(monkeypatch):
    from diary_one_ci.transport_diagnostics import DiagnosticTransport
    import urllib.request
    before = urllib.request._opener
    bodies, proxies = [], []
    class Response:
        status = 200
        headers = {}
        def read(self): return b'{}'
        def close(self): pass
    class Opener:
        def open(self, request, timeout):
            bodies.append(request.data)
            return Response()
    def build(*handlers):
        proxies.append(next(h.proxies for h in handlers if isinstance(h, urllib.request.ProxyHandler)))
        return Opener()
    monkeypatch.setattr(urllib.request, 'getproxies', lambda: {'https': 'http://user:secret@127.0.0.1:7890'})
    monkeypatch.setattr(urllib.request, 'build_opener', build)
    for mode in ('SYSTEM', 'DIRECT'):
        transport = DiagnosticTransport(proxy_mode=mode)
        transport('https://example.com/api', {'Authorization': 'Bearer secret'}, b'identical', 3)
        assert 'secret' not in json.dumps(transport.last_diagnostic)
    assert bodies == [b'identical', b'identical']
    assert proxies[0] and proxies[1] == {}
    assert urllib.request._opener is before


def test_connect_failure_has_timing_and_no_headers(monkeypatch):
    from diary_one_ci.transport_diagnostics import DiagnosticTransport
    def fail(*args, **kwargs):
        raise ConnectionResetError(54, 'secret proxy URL')
    monkeypatch.setattr(http.client.HTTPSConnection, 'connect', fail)
    transport = DiagnosticTransport(proxy_mode='DIRECT')
    with pytest.raises(urllib.error.URLError):
        transport('https://example.com/test', {}, b'{}', 3)
    diagnostic = transport.last_diagnostic
    assert diagnostic['phase'] == 'CONNECTION'
    assert diagnostic['connection_ms'] >= 0
    assert diagnostic['response_headers_received'] is False
    assert diagnostic['proxy_tunnel_used'] is False
    assert 'secret' not in json.dumps(diagnostic)


def test_default_adapter_preserves_legacy_transport_error_boundary(monkeypatch):
    from diary_one_ci.x01 import X01Error
    def fail(*args, **kwargs):
        raise ConnectionResetError(54, 'secret proxy URL')
    monkeypatch.setattr(http.client.HTTPSConnection, 'connect', fail)
    adapter = QwenChatCompletionsAdapter(api_key='not-real')
    with pytest.raises(X01Error) as error:
        adapter.transport('https://example.com/test', {}, b'{}', 3)
    assert 'secret' not in str(error.value)
    assert adapter.transport.last_diagnostic['phase'] == 'CONNECTION'


def test_wrapped_default_adapter_timeout_retains_timeout_classification(monkeypatch):
    def fail(*args, **kwargs):
        raise TimeoutError('timed out')
    monkeypatch.setattr(http.client.HTTPSConnection, 'connect', fail)
    gateway = x02.QwenStageGateway(QwenChatCompletionsAdapter(api_key='not-real'))
    with pytest.raises(x02.X02StageCallError) as error:
        gateway.call('TEST', 'prompt', {}, context={'_audit_stage_failures': True})
    assert error.value.code == 'MODEL_TRANSPORT_TIMEOUT'

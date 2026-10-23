"""Request-scoped urllib telemetry. Never record headers, URLs, bodies or errors' text.

Connection time includes DNS/TCP, proxy CONNECT when applicable, and TLS; it is
not a measurement of each separately. Socket timeout is not a wall-clock budget.
"""
from copy import deepcopy
import hashlib
import http.client
import re
import threading
import time
import urllib.error
import urllib.request


def exception_chain(error):
    result, seen = [], set()
    while isinstance(error, BaseException) and id(error) not in seen and len(result) < 8:
        seen.add(id(error))
        row = {'type': type(error).__name__, 'module': type(error).__module__}
        for key in ('errno', 'verify_code', 'code'):
            value = getattr(error, key, None)
            if isinstance(value, int):
                row[key] = value
        for key in ('library', 'reason'):
            value = getattr(error, key, None)
            if isinstance(value, str) and re.fullmatch(r'[A-Z][A-Z0-9_]{0,79}', value):
                row[key] = value
        result.append(row)
        reason = getattr(error, 'reason', None)
        error = error.__cause__ or (reason if isinstance(reason, BaseException) else None) or error.__context__
    return result


def _request_id(headers):
    for key, value in headers.items():
        if key.lower() in ('x-request-id', 'x-dashscope-request-id'):
            if re.fullmatch(r'[A-Za-z0-9_.:-]{1,160}', str(value)):
                return str(value)
    return None


class DiagnosticTransport:
    """SYSTEM uses urllib's configured proxy; DIRECT disables it for this call only.

    Results are thread-local, so concurrent requests cannot mix diagnostics.
    HTTPSConnection retains Python's default verified TLS context.
    """
    def __init__(self, proxy_mode='SYSTEM'):
        if proxy_mode not in ('SYSTEM', 'DIRECT'):
            raise ValueError('unknown transport proxy mode')
        self.proxy_mode = proxy_mode
        self._local = threading.local()

    @property
    def last_diagnostic(self):
        return deepcopy(getattr(self._local, 'diagnostic', {}))

    def __call__(self, url, headers, body, timeout):
        started = time.monotonic()
        d = {'proxy_mode': self.proxy_mode, 'phase': 'OPEN', 'response_headers_received': False,
             'response_complete': False, 'request_bytes': len(body),
             'request_sha256': hashlib.sha256(body).hexdigest(), 'socket_timeout_seconds': timeout}
        self._local.diagnostic = d
        class Connection(http.client.HTTPSConnection):
            def connect(self):
                before, d['phase'] = time.monotonic(), 'CONNECTION'
                d['proxy_tunnel_used'] = bool(self._tunnel_host)
                try:
                    super().connect()
                finally:
                    d['connection_ms'] = round((time.monotonic() - before) * 1000, 2)
            def request(self, *args, **kwargs):
                # Connect first to keep upload timing separate from CONNECT/TLS.
                if self.sock is None:
                    self.connect()
                before, d['phase'] = time.monotonic(), 'REQUEST_SEND'
                try:
                    return super().request(*args, **kwargs)
                finally:
                    d['request_send_ms'] = round((time.monotonic() - before) * 1000, 2)
            def getresponse(self):
                before, d['phase'] = time.monotonic(), 'RESPONSE_HEADERS'
                try:
                    return super().getresponse()
                finally:
                    d['response_headers_ms'] = round((time.monotonic() - before) * 1000, 2)
        class Handler(urllib.request.HTTPSHandler):
            def https_open(self, request):
                return self.do_open(Connection, request, context=self._context)
        response = None
        try:
            proxies = urllib.request.getproxies() if self.proxy_mode == 'SYSTEM' else {}
            opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxies), Handler())
            request = urllib.request.Request(url, data=body, headers=dict(headers), method='POST')
            try:
                response = opener.open(request, timeout=timeout)
            except urllib.error.HTTPError as error:
                response = error
            d.update(phase='RESPONSE_BODY', response_headers_received=True, http_status=response.status)
            request_id = _request_id(response.headers)
            if request_id:
                d['provider_request_id'] = request_id
            before = time.monotonic()
            try:
                data = response.read()
            finally:
                d['response_body_ms'] = round((time.monotonic() - before) * 1000, 2)
            d.update(phase='COMPLETE', response_complete=True, response_bytes=len(data))
            return response.status, dict(response.headers.items()), data
        except (OSError, http.client.HTTPException) as error:
            d['exception_chain'] = exception_chain(error)
            if isinstance(error, http.client.IncompleteRead):
                d['partial_response_bytes'] = len(error.partial)
            raise
        finally:
            d['total_ms'] = round((time.monotonic() - started) * 1000, 2)
            if response is not None:
                response.close()

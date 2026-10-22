"""Shared, conservative policy for interrupted provider calls.

A missing response does not mean the provider did not execute or bill the call.
Callers retain their existing attempt budgets and record unknown usage.
"""
import errno
import http.client
import random
import re
import ssl
import time


def retryable_model_failure(error):
    code = getattr(error, 'code', '')
    if code == 'MODEL_TRANSPORT_TIMEOUT' or re.fullmatch(r'MODEL_HTTP_5\d\d', code):
        return True
    if code and code != 'MODEL_TRANSPORT_FAILED':
        return False
    chain, current = [], error
    while isinstance(current, BaseException) and all(current is not item for item in chain):
        chain.append(current)
        current = getattr(current, 'reason', None) or current.__cause__ or current.__context__
    # Certificate/protocol/configuration failures require intervention, not retry.
    text = ' '.join(str(item).casefold() for item in chain)
    if any(isinstance(item, ssl.SSLCertVerificationError) for item in chain) or any(
            marker in text for marker in ('certificate_verify_failed', 'certificate verify failed',
                                         'hostname mismatch', 'self-signed certificate')):
        return False
    if any(isinstance(item, (TimeoutError, ConnectionResetError, ConnectionAbortedError,
                            BrokenPipeError, ssl.SSLEOFError, http.client.IncompleteRead,
                            http.client.RemoteDisconnected)) for item in chain):
        return True
    if any(isinstance(item, OSError) and item.errno in
           (errno.ECONNRESET, errno.ECONNABORTED, errno.ETIMEDOUT, errno.EPIPE) for item in chain):
        return True
    # urllib and legacy adapters may preserve only a string in X01Error.
    return any(marker in text for marker in ('unexpected_eof_while_reading',
        'connection reset by peer', 'connection aborted', 'broken pipe', 'timed out',
        'remote end closed connection without response', 'incompleteread('))


def wait_before_retry(retry_index):
    delay = min(8.0, 0.5 * (2 ** min(max(0, retry_index), 4))) + random.uniform(0, 0.25)
    time.sleep(delay)
    return delay

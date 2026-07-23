"""
http_client.py -- thin HTTP wrapper using stdlib urllib (no third-party deps).

make_request(method, url, headers, body, verify_ssl) -> (status_code, body)
"""

import json
import ssl
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


def make_request(
    method: str = "GET",
    url: str = "",
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Any] = None,
    verify_ssl: bool = True,
    timeout: int = 30,
) -> tuple:
    """Send an HTTP request and return (status_code, parsed_body).

    Args:
        method:     HTTP verb (GET, POST, PUT, DELETE, ...).
        url:        Full URL.
        headers:    Dict of request headers.
        body:       Request body -- dict/list will be JSON-serialised.
        verify_ssl: Set False to skip SSL verification (FDA internal CA).
        timeout:    Socket timeout in seconds.

    Returns:
        Tuple of (status_code: int, body: dict | list | str).

    Raises:
        urllib.error.URLError: On network errors.
    """
    hdrs = dict(headers or {})
    data: Optional[bytes] = None

    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body).encode()
            hdrs.setdefault("Content-Type", "application/json")
        else:
            data = str(body).encode()

    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)

    ctx = None
    if not verify_ssl:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        status = exc.code

    try:
        return status, json.loads(raw)
    except json.JSONDecodeError:
        return status, raw
#!/usr/bin/env python3
"""Smoke tests for the Mission Control Dashboard HTTP endpoints.

Usage:
    python tests/test_web_endpoints.py
    python tests/test_web_endpoints.py --base-url http://localhost:7878

Exit 0 if all tests pass, 1 if any fail.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from typing import Any
from urllib.error import URLError

TIMEOUT = 5  # seconds per request


# ---------------------------------------------------------------------------
# Core HTTP helpers
# ---------------------------------------------------------------------------

def _get(base_url: str, path: str) -> tuple[int, dict[str, str], bytes]:
    """Return (status_code, headers_dict, body_bytes). Raises on network error."""
    url = base_url.rstrip("/") + path
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.status, dict(resp.headers), resp.read()


def _post(base_url: str, path: str, payload: dict[str, Any]) -> tuple[int, dict[str, str], bytes]:
    """Return (status_code, headers_dict, body_bytes). Raises on network error."""
    url = base_url.rstrip("/") + path
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.status, dict(resp.headers), resp.read()


def _content_type(headers: dict[str, str]) -> str:
    # Header keys from dict(resp.headers) are title-cased on CPython 3.x.
    # Search case-insensitively to be safe across implementations.
    for key, val in headers.items():
        if key.lower() == "content-type":
            return val.split(";")[0].strip()
    return ""


# ---------------------------------------------------------------------------
# Individual test functions — each returns (passed: bool, message: str)
# ---------------------------------------------------------------------------

def test_root(base_url: str) -> tuple[bool, str]:
    try:
        status, headers, body = _get(base_url, "/")
    except URLError as exc:
        return False, f"Connection error: {exc}"
    ct = _content_type(headers)
    size_kb = len(body) / 1024
    if status != 200:
        return False, f"{status} (expected 200)"
    if "text/html" not in ct:
        return False, f"Content-Type {ct!r} (expected text/html)"
    if not body:
        return False, "Empty response body"
    return True, f"200, {ct}, {size_kb:.1f}KB"


def test_chat(base_url: str) -> tuple[bool, str]:
    try:
        status, headers, body = _get(base_url, "/chat")
    except URLError as exc:
        return False, f"Connection error: {exc}"
    ct = _content_type(headers)
    size_kb = len(body) / 1024
    if status != 200:
        return False, f"{status} (expected 200)"
    if "text/html" not in ct:
        return False, f"Content-Type {ct!r} (expected text/html)"
    if not body:
        return False, "Empty response body"
    return True, f"200, {ct}, {size_kb:.1f}KB"


def test_voice(base_url: str) -> tuple[bool, str]:
    try:
        status, headers, body = _get(base_url, "/voice")
    except URLError as exc:
        return False, f"Connection error: {exc}"
    ct = _content_type(headers)
    size_kb = len(body) / 1024
    if status != 200:
        return False, f"{status} (expected 200)"
    if "text/html" not in ct:
        return False, f"Content-Type {ct!r} (expected text/html)"
    if not body:
        return False, "Empty response body"
    return True, f"200, {ct}, {size_kb:.1f}KB"


def test_tree(base_url: str) -> tuple[bool, str]:
    """GET /tree — 200 with HTML, or 404 if page is not yet wired up."""
    try:
        status, headers, body = _get(base_url, "/tree")
    except URLError as exc:
        # urllib raises HTTPError for non-2xx when not catching separately
        if hasattr(exc, "code"):
            return False, f"{exc.code} (expected 200 or 404)"
        return False, f"Connection error: {exc}"
    ct = _content_type(headers)
    size_kb = len(body) / 1024
    if status == 404:
        return False, "404 Not Found"
    if status != 200:
        return False, f"{status} (expected 200)"
    if "text/html" not in ct:
        return False, f"Content-Type {ct!r} (expected text/html)"
    return True, f"200, {ct}, {size_kb:.1f}KB"


def test_api_outbox(base_url: str) -> tuple[bool, str]:
    try:
        status, headers, body = _get(base_url, "/api/outbox")
    except URLError as exc:
        return False, f"Connection error: {exc}"
    ct = _content_type(headers)
    if status != 200:
        return False, f"{status} (expected 200)"
    if "application/json" not in ct:
        return False, f"Content-Type {ct!r} (expected application/json)"
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        return False, f"Invalid JSON: {exc}"
    if "entries" not in data:
        return False, f"Missing 'entries' key; got keys: {list(data.keys())}"
    entry_count = len(data["entries"])
    return True, f"200, application/json, {entry_count} entries"


def test_api_inbox_recent(base_url: str) -> tuple[bool, str]:
    try:
        status, headers, body = _get(base_url, "/api/inbox/recent")
    except URLError as exc:
        return False, f"Connection error: {exc}"
    ct = _content_type(headers)
    if status != 200:
        return False, f"{status} (expected 200)"
    if "application/json" not in ct:
        return False, f"Content-Type {ct!r} (expected application/json)"
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        return False, f"Invalid JSON: {exc}"
    if "entries" not in data:
        return False, f"Missing 'entries' key; got keys: {list(data.keys())}"
    entry_count = len(data["entries"])
    return True, f"200, application/json, {entry_count} entries"


def test_api_quick_buttons(base_url: str) -> tuple[bool, str]:
    try:
        status, headers, body = _get(base_url, "/api/quick_buttons")
    except URLError as exc:
        return False, f"Connection error: {exc}"
    ct = _content_type(headers)
    if status != 200:
        return False, f"{status} (expected 200)"
    if "application/json" not in ct:
        return False, f"Content-Type {ct!r} (expected application/json)"
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        return False, f"Invalid JSON: {exc}"
    if "buttons" not in data:
        return False, f"Missing 'buttons' key; got keys: {list(data.keys())}"
    button_count = len(data["buttons"])
    return True, f"200, application/json, {button_count} buttons"


def test_api_inbox_post(base_url: str) -> tuple[bool, str]:
    payload = {"text": "smoke test", "channel": "web_mc_button"}
    try:
        status, headers, body = _post(base_url, "/api/inbox", payload)
    except URLError as exc:
        return False, f"Connection error: {exc}"
    ct = _content_type(headers)
    if status != 200:
        return False, f"{status} (expected 200)"
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        return False, f"Invalid JSON response: {exc}"
    return True, f"200, {ct}, accepted"


def test_shared_chat_js(base_url: str) -> tuple[bool, str]:
    try:
        status, headers, body = _get(base_url, "/shared_chat.js")
    except URLError as exc:
        return False, f"Connection error: {exc}"
    ct = _content_type(headers)
    size_kb = len(body) / 1024
    if status != 200:
        return False, f"{status} (expected 200)"
    # Accept common JS content-types
    js_types = ("application/javascript", "text/javascript", "application/x-javascript")
    if not any(t in ct for t in js_types):
        return False, f"Content-Type {ct!r} (expected JavaScript)"
    if not body:
        return False, "Empty response body"
    return True, f"200, {ct}, {size_kb:.1f}KB"


def test_styles_css(base_url: str) -> tuple[bool, str]:
    try:
        status, headers, body = _get(base_url, "/styles.css")
    except URLError as exc:
        return False, f"Connection error: {exc}"
    ct = _content_type(headers)
    size_kb = len(body) / 1024
    if status != 200:
        return False, f"{status} (expected 200)"
    if "text/css" not in ct:
        return False, f"Content-Type {ct!r} (expected text/css)"
    if not body:
        return False, "Empty response body"
    return True, f"200, {ct}, {size_kb:.1f}KB"


# ---------------------------------------------------------------------------
# Test registry
# ---------------------------------------------------------------------------

TESTS: list[tuple[str, Any]] = [
    ("GET /", test_root),
    ("GET /chat", test_chat),
    ("GET /voice", test_voice),
    ("GET /tree", test_tree),
    ("GET /api/outbox", test_api_outbox),
    ("GET /api/inbox/recent", test_api_inbox_recent),
    ("GET /api/quick_buttons", test_api_quick_buttons),
    ("POST /api/inbox", test_api_inbox_post),
    ("GET /shared_chat.js", test_shared_chat_js),
    ("GET /styles.css", test_styles_css),
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_tests(base_url: str) -> bool:
    """Run all tests, print results, return True if all passed."""
    label_width = max(len(label) for label, _ in TESTS)
    passed = 0
    failed = 0

    for label, fn in TESTS:
        ok, msg = fn(base_url)
        tag = "PASS" if ok else "FAIL"
        print(f"[{tag}] {label:<{label_width}} — {msg}")
        if ok:
            passed += 1
        else:
            failed += 1

    total = passed + failed
    print(f"\nSummary: {passed}/{total} passed, {failed} failed")
    return failed == 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Smoke-test the Mission Control Dashboard HTTP endpoints."
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:7878",
        help="Base URL of the dashboard server (default: http://localhost:7878)",
    )
    args = parser.parse_args()

    all_passed = run_tests(args.base_url)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

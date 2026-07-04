"""Tests for client-level parsing helpers."""

from __future__ import annotations

import pytest

from shopwired_mcp.client import DEFAULT_RETRY_AFTER, MAX_RETRY_AFTER, _parse_retry_after


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        (None, DEFAULT_RETRY_AFTER),  # absent header
        ("2", 2.0),  # normal numeric
        ("0", 0.0),  # immediate retry allowed
        ("300", MAX_RETRY_AFTER),  # clamped to ceiling
        ("86400", MAX_RETRY_AFTER),  # hostile/huge value clamped
        ("-5", 0.0),  # negative floored to zero
        ("nan", DEFAULT_RETRY_AFTER),  # NaN must not become a zero-sleep hot loop
        ("inf", DEFAULT_RETRY_AFTER),  # non-finite treated as unusable
        ("-inf", DEFAULT_RETRY_AFTER),
        ("Wed, 21 Oct 2026 07:28:00 GMT", DEFAULT_RETRY_AFTER),  # HTTP-date form
        ("soon", DEFAULT_RETRY_AFTER),  # garbage
    ],
)
def test_parse_retry_after(header: str | None, expected: float) -> None:
    assert _parse_retry_after(header) == expected

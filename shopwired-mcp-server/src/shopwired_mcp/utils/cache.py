"""Simple in-memory TTL cache for read-only API responses."""

from __future__ import annotations

import time
from typing import Any


class TTLCache:
    """Dictionary-based cache with per-entry expiration.

    Entries expire after ``default_ttl`` seconds.  Write operations
    should call ``invalidate_prefix`` to evict stale reads.
    """

    def __init__(self, default_ttl: float = 120.0) -> None:
        self._store: dict[str, tuple[float, Any]] = {}
        self._default_ttl = default_ttl

    def get(self, key: str) -> Any | None:
        """Return cached value or None if missing/expired."""
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Store a value with optional custom TTL."""
        self._store[key] = (time.monotonic() + (ttl or self._default_ttl), value)

    def invalidate_prefix(self, prefix: str) -> None:
        """Remove all entries whose key contains the given prefix."""
        keys = [k for k in self._store if prefix in k]
        for k in keys:
            del self._store[k]

    def clear(self) -> None:
        """Remove all entries."""
        self._store.clear()

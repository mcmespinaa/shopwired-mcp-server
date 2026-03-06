"""Tests for TTLCache."""

import time

from shopwired_mcp.utils.cache import TTLCache


def test_get_set():
    cache = TTLCache(default_ttl=60.0)
    cache.set("key1", {"data": 1})
    assert cache.get("key1") == {"data": 1}


def test_get_missing_key():
    cache = TTLCache()
    assert cache.get("nonexistent") is None


def test_expiry():
    cache = TTLCache(default_ttl=0.01)  # 10ms TTL
    cache.set("key1", "value")
    time.sleep(0.02)
    assert cache.get("key1") is None


def test_invalidate_prefix():
    cache = TTLCache()
    cache.set("/products", [1, 2])
    cache.set("/products/123", {"id": 123})
    cache.set("/orders", [3, 4])
    cache.invalidate_prefix("products")
    assert cache.get("/products") is None
    assert cache.get("/products/123") is None
    assert cache.get("/orders") == [3, 4]


def test_clear():
    cache = TTLCache()
    cache.set("a", 1)
    cache.set("b", 2)
    cache.clear()
    assert cache.get("a") is None
    assert cache.get("b") is None


def test_custom_ttl():
    cache = TTLCache(default_ttl=60.0)
    cache.set("short", "val", ttl=0.01)
    time.sleep(0.02)
    assert cache.get("short") is None
    # Default TTL entry should still be alive
    cache.set("long", "val")
    assert cache.get("long") == "val"

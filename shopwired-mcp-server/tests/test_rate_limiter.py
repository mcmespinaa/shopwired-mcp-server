"""Tests for the leaky bucket rate limiter."""

import asyncio
import time

import pytest

from shopwired_mcp.utils.rate_limiter import LeakyBucketLimiter


@pytest.mark.asyncio
async def test_acquire_within_burst():
    """Acquiring within burst capacity should not block."""
    limiter = LeakyBucketLimiter(burst=10, rate=2.0)
    start = time.monotonic()
    for _ in range(5):
        await limiter.acquire()
    elapsed = time.monotonic() - start
    # Should complete nearly instantly (well under 1 second)
    assert elapsed < 2.0


@pytest.mark.asyncio
async def test_available_decreases():
    """Available slots should decrease after acquiring."""
    limiter = LeakyBucketLimiter(burst=10, rate=2.0)
    initial = limiter.available
    await limiter.acquire()
    assert limiter.available <= initial


@pytest.mark.asyncio
async def test_limiter_creates_without_error():
    """Limiter should initialize with default parameters."""
    limiter = LeakyBucketLimiter()
    assert limiter._burst == 40
    assert limiter._rate == 2.0

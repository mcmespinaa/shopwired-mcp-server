"""Leaky bucket rate limiter matching ShopWired's API limits.

ShopWired uses a leaky bucket algorithm:
- Bucket size: 40 requests (burst capacity)
- Leak rate: 2 requests/second (sustained throughput)
- Sustainable: averaging 2 calls/sec avoids 429 errors
"""

from __future__ import annotations

import asyncio
import time


class LeakyBucketLimiter:
    """Async-safe leaky bucket rate limiter.

    Callers await `acquire()` before making an API request.
    If the bucket is full, acquire() sleeps until capacity is available.
    """

    def __init__(self, burst: int = 40, rate: float = 2.0) -> None:
        self._burst = burst
        self._rate = rate  # requests per second that leak out
        self._tokens = float(burst)  # current fill level
        self._last_check = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until a request slot is available, then consume one."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_check
            self._last_check = now

            # Leak tokens (free up capacity)
            self._tokens = max(0.0, self._tokens - elapsed * self._rate)

            if self._tokens >= self._burst:
                # Bucket is full — wait for one slot to leak
                wait_time = (self._tokens - self._burst + 1) / self._rate
                await asyncio.sleep(wait_time)
                self._tokens = self._burst - 1
            else:
                self._tokens += 1

    @property
    def available(self) -> float:
        """Approximate slots available (may be stale without lock)."""
        elapsed = time.monotonic() - self._last_check
        current = max(0.0, self._tokens - elapsed * self._rate)
        return max(0.0, self._burst - current)

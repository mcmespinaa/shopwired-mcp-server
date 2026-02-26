"""ShopWired API client with authentication, rate limiting, and retry logic.

This is the core HTTP layer that all MCP tools use to communicate with the
ShopWired REST API at https://api.ecommerceapi.uk/v1.
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any

import httpx

from .config import settings
from .utils.rate_limiter import LeakyBucketLimiter


class ShopWiredAPIError(Exception):
    """Raised when the ShopWired API returns an error."""

    def __init__(self, status_code: int, message: str, response_body: Any = None) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(f"ShopWired API error {status_code}: {message}")


class ShopWiredClient:
    """Async HTTP client for the ShopWired REST API.

    Features:
    - HTTP Basic Auth with API Key/Secret
    - Leaky bucket rate limiting (40 burst, 2/sec sustained)
    - Automatic retry with exponential backoff for 429/5xx errors
    - Structured error handling
    """

    def __init__(self) -> None:
        self._rate_limiter = LeakyBucketLimiter(
            burst=settings.rate_limit_burst,
            rate=settings.rate_limit_rate,
        )
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-initialize the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=settings.api_base_url,
                auth=(settings.api_key, settings.api_secret),
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": "shopwired-mcp-server/0.1.0",
                },
                timeout=settings.request_timeout,
            )
        return self._client

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        """Make an authenticated, rate-limited request to the ShopWired API.

        Implements retry with exponential backoff for transient errors.
        """
        client = await self._get_client()
        last_error: Exception | None = None

        for attempt in range(settings.max_retries):
            # Respect rate limits
            await self._rate_limiter.acquire()

            try:
                response = await client.request(
                    method=method,
                    url=path,
                    params=_clean_params(params),
                    json=json_body,
                )

                # Success
                if response.status_code in (200, 201):
                    return response.json()

                # No content (e.g., successful DELETE)
                if response.status_code == 204:
                    return {"success": True}

                # Rate limited — wait and retry
                if response.status_code == 429:
                    retry_after = float(response.headers.get("Retry-After", 2))
                    print(
                        f"Rate limited (429). Retrying after {retry_after}s...",
                        file=sys.stderr,
                    )
                    await asyncio.sleep(retry_after)
                    continue

                # Server error — retry with backoff
                if response.status_code >= 500:
                    wait = 2**attempt
                    print(
                        f"Server error ({response.status_code}). "
                        f"Retry {attempt + 1}/{settings.max_retries} in {wait}s...",
                        file=sys.stderr,
                    )
                    await asyncio.sleep(wait)
                    last_error = ShopWiredAPIError(
                        response.status_code,
                        response.text,
                        _safe_json(response),
                    )
                    continue

                # Client error — don't retry
                raise ShopWiredAPIError(
                    response.status_code,
                    response.text,
                    _safe_json(response),
                )

            except httpx.TimeoutException:
                wait = 2**attempt
                print(
                    f"Request timeout. Retry {attempt + 1}/{settings.max_retries} in {wait}s...",
                    file=sys.stderr,
                )
                await asyncio.sleep(wait)
                last_error = httpx.TimeoutException(f"Timeout on {method} {path}")

            except httpx.HTTPError as exc:
                last_error = exc
                break  # Network errors are not retried

        # Exhausted retries
        if last_error:
            raise last_error
        raise ShopWiredAPIError(0, "Request failed after all retries")

    # ── Convenience methods ──────────────────────────────────────────────

    async def get(self, path: str, *, params: dict[str, Any] | None = None, **extra_params: Any) -> Any:
        """GET request. Accepts params as a dict and/or keyword arguments."""
        merged = {**(params or {}), **extra_params}
        return await self.request("GET", path, params=merged or None)

    async def post(self, path: str, data: dict[str, Any] | None = None, *, json_data: dict[str, Any] | None = None) -> Any:
        """POST request. Accepts body as positional 'data' or keyword 'json_data'."""
        return await self.request("POST", path, json_body=json_data or data)

    async def put(self, path: str, data: dict[str, Any] | None = None, *, json_data: dict[str, Any] | None = None) -> Any:
        """PUT request. Accepts body as positional 'data' or keyword 'json_data'."""
        return await self.request("PUT", path, json_body=json_data or data)

    async def delete(self, path: str) -> Any:
        """DELETE request."""
        return await self.request("DELETE", path)


def _clean_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    """Remove None values from query params."""
    if params is None:
        return None
    return {k: v for k, v in params.items() if v is not None}


def _safe_json(response: httpx.Response) -> Any:
    """Try to parse response as JSON, return None on failure."""
    try:
        return response.json()
    except Exception:
        return None


# Singleton client instance — import from other modules
api_client = ShopWiredClient()

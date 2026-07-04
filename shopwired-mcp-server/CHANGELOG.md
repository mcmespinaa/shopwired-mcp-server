# Changelog

## [0.2.0] - 2026-07-04

### Security
- **Bearer-token auth is now actually enforced on the HTTP transport.**
  Previously the server required `SHOPWIRED_AUTH_TOKEN` to be set but never
  checked it on requests — any unauthenticated caller could reach the store
  API. The middleware is now implemented (constant-time comparison via
  `hmac.compare_digest`, fail-closed on empty token) and wired into the
  streamable-http app.
- Clamp `Retry-After` handling to 60s so a hostile/broken upstream header
  cannot stall a tool call indefinitely; non-numeric, NaN, infinite, and
  HTTP-date values fall back safely to the 2s default.
- Deep health probes (`/health?deep=true`) use a dedicated single-attempt
  5s probe that bypasses the shared rate limiter, retry loop, and circuit
  breaker, memoized for 10s — the auth-exempt endpoint can no longer be
  looped by unauthenticated callers to drain the request budget or trip
  the circuit breaker for real tool calls.

### Added
- `GET /health` endpoint on the HTTP transport (exempt from auth, for
  platform probes; trailing-slash `/health/` also accepted). `?deep=true`
  additionally probes the ShopWired API and returns 503 when unreachable.
- `SHOPWIRED_TRANSPORT` is validated at startup — unknown values now fail
  fast with a clear error instead of silently starting the HTTP transport.
- Tests for the auth middleware, health endpoint, and Retry-After parsing.

### Fixed
- Shared HTTP client is no longer closed when a single MCP session ends
  over streamable-http (the FastMCP lifespan runs per session); it now
  closes in the process-level app lifespan, so concurrent sessions'
  in-flight requests survive another client disconnecting.
- Exhausting retries on 429s now raises a 429 error instead of a generic
  status-0 failure, so rate limiting is distinguishable from an outage.
- Docker cold starts no longer re-resolve the environment (`uv run
  --no-sync`).
- README config table and architecture diagram updated for the remote
  transport (`SHOPWIRED_TRANSPORT`, `SHOPWIRED_AUTH_TOKEN`, host/port).

### Changed
- Version aligned across `pyproject.toml`, `__init__.py`, and `User-Agent`
  (previously a 0.1.0/0.1.1 mismatch).

## [0.1.1] - 2026-03-06

### Security
- Enforce HTTPS for webhook URLs (reject http://, malformed URLs)
- Add email format validation for customer creation
- Add date format validation for voucher expiry dates
- Sanitize API error responses to prevent information leakage
- Pin dependencies with compatible-release constraints (~=)

### Added
- Circuit breaker: opens after 5 consecutive API failures, 30s recovery timeout
- Response caching: 2-minute TTL on GET requests, auto-invalidated on writes
- Graceful shutdown via FastMCP lifespan (closes HTTP connection pool)
- Concurrent connection limits (20 max connections, 10 keepalive)
- Structured logging across all tool modules and HTTP client
- CONTRIBUTING.md, CHANGELOG.md, PERMISSIONS.md documentation

### Changed
- API credentials now use `SecretStr` (required, no empty defaults)
- HTTP client uses explicit timeouts (30s read, 10s connect)
- All delete operations require `confirm=True` parameter
- Input validation on tool parameters (IDs, counts, offsets, empty strings)

## [0.1.0] - 2026-03-05

### Added
- Initial release with 38 MCP tools across 4 domains
- Product management (search, CRUD, stock, images, variations)
- Order management (list, search, status updates, comments)
- Customer management (list, get, create)
- Store configuration (categories, brands, vouchers, shipping, webhooks)
- Leaky bucket rate limiting (40 burst, 2/sec sustained)
- Retry with exponential backoff for 429/5xx errors

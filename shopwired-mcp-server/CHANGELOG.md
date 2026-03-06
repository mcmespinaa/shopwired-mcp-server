# Changelog

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

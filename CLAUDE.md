# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

MCP (Model Context Protocol) server connecting AI assistants to the ShopWired e-commerce platform. Exposes 38 tools for product, order, customer, and store management. Two transports: JSON-RPC 2.0 over stdio (local, default) and streamable-http behind a bearer token (remote — see `shopwired-mcp-server/DEPLOY.md`).

## Repo Layout

- `shopwired-mcp-server/` — the server (all commands below run from here)
- `shopwired-skills/` — companion agent skills (10 SKILL.md knowledge bases: store-intelligence-core first, then catalog/inventory/pricing/orders/customers/B2B/sync/onboarding/reporting)
- `README.md` — GitHub-facing overview for the whole repo

## Commands

```bash
uv sync --dev                        # Install dependencies
uv run python -m pytest tests/ -v    # Run tests
uv run ruff check src/ tests/        # Lint
uv run ruff format src/ tests/       # Format
uv run mypy src/                     # Type check (strict mode)
shopwired-mcp                        # Run server (entry point)
```

Package manager: `uv` (preferred) or `pip`.

## Architecture

- **FastMCP framework** — async Python MCP server
- **38 tools** in 4 categories: Products (11), Orders (7), Customers (4), Store Config (16)
- **Built-in resilience**: rate limiter (leaky bucket: 40 burst / 2 req/sec), circuit breaker (5 failures threshold), TTL cache (2-min), exponential backoff
- **Safety guards**: destructive tools require explicit `confirm=True`, HTTPS-only webhooks, input validation (ID ranges, pagination bounds, email format)
- **MCP annotations**: readOnlyHint, destructiveHint, idempotentHint, openWorldHint on every tool
- **Response caching**: automatic invalidation on write operations

## Key Files (inside shopwired-mcp-server/)

- `src/` — Server source code (`auth.py` = bearer-token middleware for the HTTP transport)
- `tests/` — pytest tests (auth middleware, health endpoint, client parsing, utils)
- `DEPLOY.md` — Remote deployment (Cloud Run / Render / VPS) + health checks
- `Dockerfile` / `install.sh` / `install.bat` — Container image and one-click local installers
- `PERMISSIONS.md` — API endpoint permission mappings
- `CONTRIBUTING.md` — Contribution guidelines
- `CHANGELOG.md` — Version history

## Tech Stack

Python 3.10+, FastMCP, httpx, pydantic, pydantic-settings

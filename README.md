# ShopWired MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that connects AI assistants to [ShopWired](https://www.shopwired.co.uk/) e-commerce stores. Manage products, orders, customers, and store configuration through natural language.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](shopwired-mcp-server/LICENSE) [![MCP](https://img.shields.io/badge/MCP-Compatible-purple)](https://modelcontextprotocol.io/)

---

## What It Does

This server lets AI tools like **Claude Desktop**, **Claude Cowork**, **Claude Code**, **Cursor**, **Windsurf**, and any MCP-compatible client interact with a ShopWired store. It wraps the ShopWired REST API into **38 standardized MCP tools** that any AI client can discover and call.

**Example prompts you can use:**

- *"Show me my top-selling products"*
- *"How many orders came in this week?"*
- *"Create a 10% discount code called SAVE10"*
- *"Update the stock for product 1234 to 50 units"*
- *"List all customers and their order counts"*
- *"What shipping zones do I have configured?"*

---

## Tools Overview (38 tools)

### Products — 11 tools

| Tool | Description | Type |
|------|-------------|------|
| `search_products` | Search products by keyword | Read |
| `get_product` | Get full product details by ID | Read |
| `list_products` | List products with filters and pagination | Read |
| `get_product_count` | Get total number of products | Read |
| `list_product_variations` | List size/color variants for a product | Read |
| `list_product_images` | List all images for a product | Read |
| `create_product` | Create a new product | Write |
| `update_product` | Update an existing product | Write |
| `update_stock` | Update stock level for a product or variation | Write |
| `delete_product` | Permanently delete a product (requires confirmation) | Delete |

### Orders — 7 tools

| Tool | Description | Type |
|------|-------------|------|
| `list_orders` | List orders with status filter and pagination | Read |
| `get_order` | Get full order details by ID | Read |
| `search_orders` | Search orders by keyword | Read |
| `get_order_count` | Get total number of orders | Read |
| `update_order_status` | Update order status with optional customer notification | Write |
| `add_order_comment` | Add an internal admin comment to an order | Write |
| `delete_order` | Permanently delete an order (requires confirmation) | Delete |

### Customers — 4 tools

| Tool | Description | Type |
|------|-------------|------|
| `list_customers` | List customers with pagination | Read |
| `get_customer` | Get full customer details by ID | Read |
| `get_customer_count` | Get total number of customers | Read |
| `create_customer` | Create a new customer record | Write |

### Store Configuration — 16 tools

| Tool | Description | Type |
|------|-------------|------|
| `list_categories` | List all product categories | Read |
| `create_category` | Create a new category | Write |
| `update_category` | Update a category name or description | Write |
| `delete_category` | Delete a category (requires confirmation) | Delete |
| `list_brands` | List all product brands | Read |
| `create_brand` | Create a new brand | Write |
| `list_vouchers` | List all voucher/discount codes | Read |
| `create_voucher` | Create a new voucher (percentage, fixed, or free shipping) | Write |
| `delete_voucher` | Delete a voucher (requires confirmation) | Delete |
| `list_gift_cards` | List all gift cards | Read |
| `list_shipping_zones` | List shipping zones | Read |
| `list_shipping_rates` | List rates for a specific shipping zone | Read |
| `list_webhooks` | List configured webhooks | Read |
| `create_webhook` | Create a webhook subscription (HTTPS only) | Write |
| `get_business_details` | Get store name, address, and contact info | Read |
| `list_countries` | List available countries | Read |
| `list_payment_methods` | List configured payment methods | Read |

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **[uv](https://docs.astral.sh/uv/)** (recommended) or pip
- **ShopWired API Key and Secret** — get these from your ShopWired admin panel under *Your Account → API & Webhooks*

### Option A — One-click installer (recommended)

```bash
git clone https://github.com/mcmespinaa/shopwired-mcp-server.git
cd shopwired-mcp-server/shopwired-mcp-server
./install.sh        # macOS / Linux — Windows: install.bat
```

The installer sets up `uv`, installs locked dependencies, prompts for your
API credentials (never written to disk), and registers the server with
Claude Code automatically. If Claude Code isn't installed it prints the
Claude Desktop config to paste instead. That's it — try a prompt.

### Option B — Manual setup

#### 1. Clone and install

```bash
git clone https://github.com/mcmespinaa/shopwired-mcp-server.git
cd shopwired-mcp-server/shopwired-mcp-server
uv sync --dev
```

#### 2. Configure credentials

```bash
cp .env.example .env
```

Edit `.env` with your ShopWired API credentials:

```env
SHOPWIRED_API_KEY=your_api_key_here
SHOPWIRED_API_SECRET=your_api_secret_here
```

### Connect to an AI client

#### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%AppData%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "shopwired": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/shopwired-mcp-server/shopwired-mcp-server",
        "run",
        "shopwired-mcp"
      ],
      "env": {
        "SHOPWIRED_API_KEY": "your_api_key",
        "SHOPWIRED_API_SECRET": "your_api_secret"
      }
    }
  }
}
```

Restart Claude Desktop. You should see **shopwired** in the tools menu.

#### Claude Cowork

Cowork (the agentic workspace in the Claude desktop app) reads the **same
config file as Claude Desktop** — no separate setup:

1. Open the Claude desktop app → **Settings → Developer → Edit Config**
2. Add the `shopwired` block exactly as shown in the Claude Desktop section above
3. Restart the Claude app — the ShopWired tools are available in Cowork sessions

> **Note on remote use:** Cowork's custom connectors (Customize → Connectors)
> run from Anthropic's cloud and authenticate via OAuth. This server's remote
> transport uses a static bearer token instead, so for Cowork use the local
> config above; the remote deployment works with Claude Code and other
> header-capable HTTP clients.

#### Claude Code

```bash
claude mcp add shopwired -- uv --directory /ABSOLUTE/PATH/TO/shopwired-mcp-server/shopwired-mcp-server run shopwired-mcp
```

#### Cursor / Windsurf

Add to your MCP configuration file (`.cursor/mcp.json` or equivalent):

```json
{
  "mcpServers": {
    "shopwired": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/shopwired-mcp-server/shopwired-mcp-server",
        "run",
        "shopwired-mcp"
      ],
      "env": {
        "SHOPWIRED_API_KEY": "your_api_key",
        "SHOPWIRED_API_SECRET": "your_api_secret"
      }
    }
  }
}
```

---

## Architecture

```
AI Client (Claude Desktop / Cowork / Claude Code / Cursor)
    |
    [JSON-RPC 2.0 / stdio]           -- local (default)
    [streamable-http + bearer token] -- remote (see DEPLOY.md)
    v
ShopWired MCP Server (FastMCP)
    +-- Bearer Auth Middleware (HTTP only; constant-time, fail-closed)
    +-- /health endpoint (liveness + ?deep=true readiness)
    +-- Tool Registry (38 tools with MCP annotations)
    +-- Rate Limiter (leaky bucket: 40 burst, 2/sec)
    +-- Circuit Breaker (opens after 5 failures, 30s recovery)
    +-- Response Cache (2-min TTL, auto-invalidated on writes)
    +-- HTTP Client (auth, retries, connection pooling)
    |
    [HTTPS / Basic Auth]
    v
ShopWired REST API (api.ecommerceapi.uk/v1)
```

---

## Project Structure

```
shopwired-mcp-server/
├── src/shopwired_mcp/
│   ├── __init__.py
│   ├── __main__.py          # python -m entry point
│   ├── server.py            # MCP server setup, health endpoint, main()
│   ├── auth.py              # Bearer-token middleware (HTTP transport)
│   ├── client.py            # HTTP client (auth, retry, cache, circuit breaker)
│   ├── config.py            # Settings via pydantic-settings
│   ├── tools/
│   │   ├── products.py      # Product CRUD, stock, images, variations
│   │   ├── orders.py        # Order management
│   │   ├── customers.py     # Customer management
│   │   └── store.py         # Categories, brands, vouchers, shipping, webhooks
│   └── utils/
│       ├── rate_limiter.py  # Leaky bucket implementation
│       ├── cache.py         # TTL cache for GET responses
│       └── formatting.py    # API response → readable text
├── tests/
│   ├── test_auth.py         # Bearer auth middleware + health endpoint tests
│   ├── test_client.py       # Retry-After parsing tests
│   ├── test_formatting.py   # Response formatter tests
│   ├── test_rate_limiter.py # Rate limiter tests
│   └── test_cache.py        # TTL cache tests
├── install.sh / install.bat  # One-click installers (macOS/Linux, Windows)
├── Dockerfile                # Container image for remote deployment
├── DEPLOY.md                 # Cloud Run / Render / VPS guide + health checks
├── pyproject.toml
├── .env.example
├── PERMISSIONS.md            # API endpoint reference per tool
├── CONTRIBUTING.md
├── CHANGELOG.md
└── README.md

../shopwired-skills/          # Companion agent skills (sibling folder, see below)
```

---

## Configuration

All settings are loaded from environment variables (prefixed with `SHOPWIRED_`) or a `.env` file.

| Variable | Default | Description |
|----------|---------|-------------|
| `SHOPWIRED_API_KEY` | *required* | ShopWired API key |
| `SHOPWIRED_API_SECRET` | *required* | ShopWired API secret |
| `SHOPWIRED_API_BASE_URL` | `https://api.ecommerceapi.uk/v1` | API base URL |
| `SHOPWIRED_TRANSPORT` | `stdio` | `stdio` (local) or `streamable-http` (remote) |
| `SHOPWIRED_AUTH_TOKEN` | *(empty)* | **Required for HTTP transport** — bearer token remote clients must present; the server refuses to start over HTTP without it |
| `SHOPWIRED_HOST` | `0.0.0.0` | Bind address (HTTP transport only) |
| `SHOPWIRED_PORT` | `8080` | Bind port (HTTP transport only) |
| `SHOPWIRED_RATE_LIMIT_BURST` | `40` | Leaky bucket burst capacity |
| `SHOPWIRED_RATE_LIMIT_RATE` | `2.0` | Sustained requests per second |
| `SHOPWIRED_REQUEST_TIMEOUT` | `30.0` | HTTP request timeout (seconds) |
| `SHOPWIRED_MAX_RETRIES` | `3` | Max retry attempts for transient errors |
| `SHOPWIRED_MAX_CONNECTIONS` | `20` | Max concurrent HTTP connections |
| `SHOPWIRED_MAX_KEEPALIVE_CONNECTIONS` | `10` | Max keepalive connections |
| `SHOPWIRED_CIRCUIT_BREAKER_THRESHOLD` | `5` | Consecutive failures before circuit opens |
| `SHOPWIRED_CIRCUIT_BREAKER_TIMEOUT` | `30.0` | Seconds before half-open probe |
| `SHOPWIRED_CACHE_TTL` | `120.0` | Response cache TTL (seconds) |
| `SHOPWIRED_MAX_RESPONSE_SIZE` | `10000000` | Max response body size (bytes) |

---

## Safety and Reliability

### MCP Tool Annotations

Every tool declares behavioral hints per the MCP specification, enabling clients to apply appropriate safeguards:

- **`readOnlyHint`** — Read tools (list, get, search, count) are marked read-only so clients can auto-approve them
- **`destructiveHint`** — Delete tools are flagged as destructive so clients show extra confirmation prompts
- **`idempotentHint`** — Update/PUT tools are marked idempotent (safe to retry); create/POST tools are not
- **`openWorldHint`** — `create_webhook` is marked as interacting with external systems

### Input Validation

- All ID parameters validated (must be positive integers)
- Pagination parameters bounded (count capped at 250, offset must be non-negative)
- Empty string rejection on required text fields (titles, names, codes)
- Email format validation on customer creation
- Date format validation (YYYY-MM-DD) on voucher expiry dates
- Webhook URLs must use HTTPS with a valid hostname

### Destructive Operation Guards

All delete operations (`delete_product`, `delete_order`, `delete_category`, `delete_voucher`) require an explicit `confirm=True` parameter. Without it, the tool returns a warning message instead of executing.

### Rate Limiting

Leaky bucket algorithm matching ShopWired's API limits:

- **Burst capacity:** 40 requests (configurable)
- **Sustained rate:** 2 requests/second (configurable)
- Automatic backoff on 429 responses using `Retry-After` header

### Circuit Breaker

Protects against cascading failures when the API is down:

- Opens after 5 consecutive failures (server errors or timeouts)
- Blocks all requests for 30 seconds while open
- Allows a single probe request after timeout (half-open state)
- Resets on any successful response

### Response Caching

GET responses are cached in-memory with a 2-minute TTL:

- Cache keys are deterministic (path + sorted query params)
- Any write operation (POST/PUT/DELETE) automatically invalidates cached entries for that resource type
- Configurable TTL via `SHOPWIRED_CACHE_TTL`

### Retry with Backoff

- **429 (Rate Limited):** Retries after the `Retry-After` header value (clamped to 60s; malformed/NaN values fall back to 2s)
- **5xx (Server Error):** Retries with exponential backoff (1s, 2s, 4s)
- **4xx (Client Error):** Not retried (fails immediately)
- **Timeouts:** Retried with exponential backoff

### Error Sanitization

API error responses are sanitized before being returned to the AI client. Only the message, error, or detail field is extracted — raw response bodies and internal details are never exposed.

### Credential Security

- API credentials use `SecretStr` (pydantic) — never logged or serialized in plain text
- Credentials are required fields with no defaults — the server refuses to start without them
- Connection pool limits prevent resource exhaustion (20 max connections, 10 keepalive)

### Graceful Shutdown

The server uses a FastMCP lifespan context manager to ensure the HTTP connection pool is properly closed on shutdown, preventing resource leaks.

---

## Remote Deployment (HTTP)

The server can also run as a **remote MCP server** over streamable-http, so
clients connect to a URL instead of spawning a local process — one container
serving your store to Claude Code or any MCP client that can send an
`Authorization` header. (Claude Cowork and claude.ai custom connectors
authenticate via OAuth, not static bearer tokens — use the local setup for
those.)

- **Auth:** every request must present `Authorization: Bearer <token>`
  (`SHOPWIRED_AUTH_TOKEN`). Constant-time comparison, fail-closed — the
  server refuses to start over HTTP without a token.
- **Health checks:** `GET /health` (liveness, no auth) and
  `GET /health?deep=true` (readiness — single-attempt 5s probe of the
  ShopWired API, memoized 10s, returns 503 when unreachable).
- **Container-ready:** `Dockerfile` included; works on Cloud Run (free tier,
  scale-to-zero), Render, or any VPS behind HTTPS.

```bash
claude mcp add --transport http shopwired https://YOUR-URL/mcp \
  --header "Authorization: Bearer YOUR_TOKEN"
```

Full walkthrough: [DEPLOY.md](shopwired-mcp-server/DEPLOY.md).

---

## Agent Skills Library

[`shopwired-skills/`](shopwired-skills/) ships 10 companion skills — Markdown
knowledge bases that teach AI agents how to operate a ShopWired store *well*,
not just which tools exist. Start with `store-intelligence-core` (how to read
store state correctly — variation stock, active flags, category structure);
the rest cover catalog quality, inventory decisions, pricing/promotions,
order lifecycle, customer segments, B2B/wholesale routing, multi-channel
sync, store onboarding, and reporting.

Use them with any skills-capable client (e.g. copy into `~/.claude/skills/`
for Claude Code). They pair with the MCP server: the server provides the
tools, the skills provide the judgment.

---

## Development

All commands run from the `shopwired-mcp-server/` subfolder:

```bash
# Run tests
uv run python -m pytest tests/ -v

# Run with coverage
uv run python -m pytest tests/ --cov=shopwired_mcp

# Lint
uv run ruff check src/ tests/

# Format
uv run ruff format src/ tests/

# Type check (strict mode)
uv run mypy src/
```

See [CONTRIBUTING.md](shopwired-mcp-server/CONTRIBUTING.md) for full development guidelines.

---

## API Permissions

See [PERMISSIONS.md](shopwired-mcp-server/PERMISSIONS.md) for a complete table mapping each tool to its HTTP method, endpoint, and required permission level (Read/Write/Delete). Use this to configure least-privilege API keys.

---

## Changelog

See [CHANGELOG.md](shopwired-mcp-server/CHANGELOG.md) for version history.

---

## License

This project is licensed under the MIT License. See [LICENSE](shopwired-mcp-server/LICENSE) for details.

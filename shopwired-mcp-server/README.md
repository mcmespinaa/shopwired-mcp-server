# ShopWired MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that connects AI assistants to [ShopWired](https://www.shopwired.co.uk) e-commerce stores. Manage products, orders, customers, and store configuration through natural language.

## What It Does

This server lets AI tools like **Claude Desktop**, **Claude Code**, **Cursor**, **Windsurf**, and any MCP-compatible client interact with a ShopWired store. It wraps the [ShopWired REST API](https://help.shopwired.co.uk/api) into 38 standardized MCP tools that any AI client can discover and call.

### Tools Overview (38 tools)

<details>
<summary><strong>Products</strong> — 11 tools</summary>

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

</details>

<details>
<summary><strong>Orders</strong> — 7 tools</summary>

| Tool | Description | Type |
|------|-------------|------|
| `list_orders` | List orders with status filter and pagination | Read |
| `get_order` | Get full order details by ID | Read |
| `search_orders` | Search orders by keyword | Read |
| `get_order_count` | Get total number of orders | Read |
| `update_order_status` | Update order status with optional customer notification | Write |
| `add_order_comment` | Add an internal admin comment to an order | Write |
| `delete_order` | Permanently delete an order (requires confirmation) | Delete |

</details>

<details>
<summary><strong>Customers</strong> — 4 tools</summary>

| Tool | Description | Type |
|------|-------------|------|
| `list_customers` | List customers with pagination | Read |
| `get_customer` | Get full customer details by ID | Read |
| `get_customer_count` | Get total number of customers | Read |
| `create_customer` | Create a new customer record | Write |

</details>

<details>
<summary><strong>Store Configuration</strong> — 16 tools</summary>

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

</details>

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- ShopWired API Key and Secret ([how to get them](https://help.shopwired.co.uk/api/authentication/api-obtaining-your-api-keys))

### 1. Clone and install

```bash
git clone https://github.com/mcmespinaa/shopwired-mcp-server.git
cd shopwired-mcp-server/shopwired-mcp-server
uv sync --dev
```

### 2. Configure credentials

```bash
cp .env.example .env
```

Edit `.env` with your ShopWired API credentials:

```env
SHOPWIRED_API_KEY=your_api_key_here
SHOPWIRED_API_SECRET=your_api_secret_here
```

### 3. Connect to an AI client

#### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%AppData%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "shopwired": {
      "command": "uv",
      "args": [
        "--directory", "/ABSOLUTE/PATH/TO/shopwired-mcp-server/shopwired-mcp-server",
        "run", "shopwired-mcp"
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
        "--directory", "/ABSOLUTE/PATH/TO/shopwired-mcp-server/shopwired-mcp-server",
        "run", "shopwired-mcp"
      ],
      "env": {
        "SHOPWIRED_API_KEY": "your_api_key",
        "SHOPWIRED_API_SECRET": "your_api_secret"
      }
    }
  }
}
```

### 4. Try it out

Ask your AI assistant:

- *"Show me my top-selling products"*
- *"How many orders came in this week?"*
- *"Create a 10% discount code called SAVE10"*
- *"Update the stock for product 1234 to 50 units"*
- *"List all customers and their order counts"*
- *"What shipping zones do I have configured?"*

## Architecture

```
AI Client (Claude Desktop / Claude Code / Cursor)
        |
  [JSON-RPC 2.0 / stdio]
        v
  ShopWired MCP Server (FastMCP)
  +-- Tool Registry (38 tools with MCP annotations)
  +-- Rate Limiter (leaky bucket: 40 burst, 2/sec)
  +-- Circuit Breaker (opens after 5 failures, 30s recovery)
  +-- Response Cache (2-min TTL, auto-invalidated on writes)
  +-- HTTP Client (auth, retries, connection pooling)
        |
  [HTTPS / Basic Auth]
        v
  ShopWired REST API
  (api.ecommerceapi.uk/v1)
```

## Project Structure

```
shopwired-mcp-server/
+-- src/shopwired_mcp/
|   +-- __init__.py
|   +-- __main__.py            # python -m entry point
|   +-- server.py               # MCP server setup, lifespan, main()
|   +-- client.py               # HTTP client (auth, retry, cache, circuit breaker)
|   +-- config.py               # Settings via pydantic-settings
|   +-- tools/
|   |   +-- products.py         # Product CRUD, stock, images, variations
|   |   +-- orders.py           # Order management
|   |   +-- customers.py        # Customer management
|   |   +-- store.py            # Categories, brands, vouchers, shipping, webhooks
|   +-- utils/
|       +-- rate_limiter.py     # Leaky bucket implementation
|       +-- cache.py            # TTL cache for GET responses
|       +-- formatting.py       # API response -> readable text
+-- tests/
|   +-- test_formatting.py      # Response formatter tests
|   +-- test_rate_limiter.py    # Rate limiter tests
|   +-- test_cache.py           # TTL cache tests
+-- pyproject.toml
+-- .env.example
+-- PERMISSIONS.md               # API endpoint reference per tool
+-- CONTRIBUTING.md
+-- CHANGELOG.md
+-- README.md
```

## Configuration

All settings are loaded from environment variables (prefixed with `SHOPWIRED_`) or a `.env` file.

| Variable | Default | Description |
|----------|---------|-------------|
| `SHOPWIRED_API_KEY` | *required* | ShopWired API key |
| `SHOPWIRED_API_SECRET` | *required* | ShopWired API secret |
| `SHOPWIRED_API_BASE_URL` | `https://api.ecommerceapi.uk/v1` | API base URL |
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

## Safety and Reliability

### MCP Tool Annotations

Every tool declares behavioral hints per the [MCP specification](https://modelcontextprotocol.io/specification/2025-03-26/server/tools), enabling clients to apply appropriate safeguards:

- **`readOnlyHint`** — Read tools (list, get, search, count) are marked read-only so clients can auto-approve them
- **`destructiveHint`** — Delete tools are flagged as destructive so clients show extra confirmation prompts
- **`idempotentHint`** — Update/PUT tools are marked idempotent (safe to retry); create/POST tools are not
- **`openWorldHint`** — `create_webhook` is marked as interacting with external systems

### Input Validation

- All ID parameters validated (must be positive integers)
- Pagination parameters bounded (count capped at 250, offset must be non-negative)
- Empty string rejection on required text fields (titles, names, codes)
- Email format validation on customer creation
- Date format validation (`YYYY-MM-DD`) on voucher expiry dates
- Webhook URLs must use HTTPS with a valid hostname

### Destructive Operation Guards

All delete operations (`delete_product`, `delete_order`, `delete_category`, `delete_voucher`) require an explicit `confirm=True` parameter. Without it, the tool returns a warning message instead of executing.

### Rate Limiting

Leaky bucket algorithm matching ShopWired's API limits:
- **Burst capacity**: 40 requests (configurable)
- **Sustained rate**: 2 requests/second (configurable)
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

- **429 (Rate Limited)**: Retries after `Retry-After` header value
- **5xx (Server Error)**: Retries with exponential backoff (1s, 2s, 4s)
- **4xx (Client Error)**: Not retried (fails immediately)
- **Timeouts**: Retried with exponential backoff

### Error Sanitization

API error responses are sanitized before being returned to the AI client. Only the `message`, `error`, or `detail` field is extracted — raw response bodies and internal details are never exposed.

### Credential Security

- API credentials use `SecretStr` (pydantic) — never logged or serialized in plain text
- Credentials are required fields with no defaults — the server refuses to start without them
- Connection pool limits prevent resource exhaustion (20 max connections, 10 keepalive)

### Graceful Shutdown

The server uses a FastMCP lifespan context manager to ensure the HTTP connection pool is properly closed on shutdown, preventing resource leaks.

## Development

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

See [CONTRIBUTING.md](CONTRIBUTING.md) for full development guidelines.

## API Permissions

See [PERMISSIONS.md](PERMISSIONS.md) for a complete table mapping each tool to its HTTP method, endpoint, and required permission level (Read/Write/Delete). Use this to configure least-privilege API keys.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT

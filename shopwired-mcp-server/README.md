# ShopWired MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that connects AI assistants to [ShopWired](https://www.shopwired.co.uk) e-commerce stores. Manage products, orders, customers, and store configuration through natural language.

## What it does

This server lets AI tools like Claude Desktop, ChatGPT, Cursor, and others interact with a ShopWired store via MCP. It wraps the [ShopWired REST API](https://help.shopwired.co.uk/api) into standardized MCP tools that any AI client can discover and call.

### Available Tools (30+)

**Products** — `search_products`, `get_product`, `list_products`, `create_product`, `update_product`, `delete_product`, `update_stock`, `list_product_variations`, `list_product_images`

**Orders** — `list_orders`, `get_order`, `search_orders`, `get_order_count`, `update_order_status`, `add_order_comment`, `delete_order`

**Customers** — `list_customers`, `get_customer`, `get_customer_count`, `create_customer`

**Store Config** — `list_categories`, `create_category`, `update_category`, `delete_category`, `list_brands`, `create_brand`, `list_vouchers`, `create_voucher`, `delete_voucher`, `list_gift_cards`, `list_shipping_zones`, `list_shipping_rates`, `list_webhooks`, `create_webhook`, `get_business_details`, `list_countries`, `list_payment_methods`

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://astral.sh/uv) (recommended) or pip
- ShopWired API Key and Secret ([how to get them](https://help.shopwired.co.uk/api/authentication/api-obtaining-your-api-keys))

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/shopwired-mcp-server.git
cd shopwired-mcp-server
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

### 2. Configure credentials

```bash
cp .env.example .env
# Edit .env with your ShopWired API Key and Secret
```

### 3. Connect to Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%AppData%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "shopwired": {
      "command": "uv",
      "args": [
        "--directory", "/ABSOLUTE/PATH/TO/shopwired-mcp-server",
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

Restart Claude Desktop. You should see "shopwired" in the Connectors menu.

### 4. Try it out

Ask Claude:
- "Show me my top-selling products"
- "How many orders came in this week?"
- "Create a 10% discount code called SAVE10"
- "Update the stock for product 1234 to 50 units"

## Architecture

```
AI Client (Claude / ChatGPT / Cursor)
        │
  [JSON-RPC 2.0 / stdio]
        ▼
  ShopWired MCP Server
  ├── FastMCP (tool registry)
  ├── Rate Limiter (leaky bucket: 40 burst, 2/sec)
  └── HTTP Client (auth, retries, error handling)
        │
  [HTTPS / Basic Auth]
        ▼
  ShopWired REST API
  (api.ecommerceapi.uk/v1)
```

## Project Structure

```
shopwired-mcp-server/
├── src/shopwired_mcp/
│   ├── __init__.py
│   ├── __main__.py          # python -m entry point
│   ├── server.py             # MCP server setup & main()
│   ├── client.py             # ShopWired API HTTP client
│   ├── config.py             # Settings via pydantic-settings
│   ├── tools/
│   │   ├── products.py       # Product CRUD + stock + images
│   │   ├── orders.py         # Order management
│   │   ├── customers.py      # Customer management
│   │   └── store.py          # Categories, vouchers, shipping, etc.
│   └── utils/
│       ├── rate_limiter.py   # Leaky bucket implementation
│       └── formatting.py     # API response → readable text
├── tests/
│   ├── test_formatting.py
│   └── test_rate_limiter.py
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=shopwired_mcp

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Rate Limiting

The server implements ShopWired's leaky bucket rate limiting:
- **Burst capacity**: 40 requests
- **Sustained rate**: 2 requests/second
- **Auto-retry**: 429 responses trigger automatic backoff
- **Server errors**: Retried with exponential backoff (up to 3 attempts)

## Security Notes

- API credentials are loaded from environment variables or `.env` — never committed to git
- The `.gitignore` excludes `.env` files by default
- All communication with ShopWired uses HTTPS
- For remote deployment, add OAuth 2.1 per the [MCP spec](https://modelcontextprotocol.io/specification/2025-11-25)

## License

MIT

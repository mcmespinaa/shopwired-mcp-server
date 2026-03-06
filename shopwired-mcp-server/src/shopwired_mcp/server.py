"""ShopWired MCP Server — main entry point.

Registers all tools and starts the FastMCP server.
Usage:
    # Local (stdio) — for Claude Desktop, Cursor, etc.
    shopwired-mcp

    # Or run directly
    python -m shopwired_mcp.server
    uv run shopwired-mcp
"""

from __future__ import annotations

import logging
import sys

from mcp.server.fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)

from .config import settings
from .tools.customers import register_customer_tools
from .tools.orders import register_order_tools
from .tools.products import register_product_tools
from .tools.store import register_store_tools


def create_server() -> FastMCP:
    """Create and configure the MCP server with all tools."""
    mcp = FastMCP(
        "shopwired",
        instructions=(
            "ShopWired MCP Server — manage products, orders, customers, and "
            "store configuration for a ShopWired e-commerce store. "
            "Use these tools to query and modify store data through the ShopWired API."
        ),
    )

    # Register all tool modules
    register_product_tools(mcp)
    register_order_tools(mcp)
    register_customer_tools(mcp)
    register_store_tools(mcp)

    return mcp


def main() -> None:
    """CLI entry point."""
    if not settings.validate_credentials():
        sys.exit(1)

    print("Starting ShopWired MCP Server...", file=sys.stderr)
    print(f"  API Base: {settings.api_base_url}", file=sys.stderr)
    print(f"  Rate Limit: {settings.rate_limit_rate} req/s (burst: {settings.rate_limit_burst})", file=sys.stderr)

    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()

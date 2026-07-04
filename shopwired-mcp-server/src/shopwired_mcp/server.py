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
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse

from . import __version__
from .auth import add_auth
from .client import api_client
from .config import settings
from .tools.customers import register_customer_tools
from .tools.orders import register_order_tools
from .tools.products import register_product_tools
from .tools.store import register_store_tools

logger = logging.getLogger(__name__)

VALID_TRANSPORTS = ("stdio", "streamable-http")

# Deep health probes are memoized this long so probe storms (or abusive
# unauthenticated callers — /health is auth-exempt) collapse into at most
# one upstream ShopWired request per window.
DEEP_HEALTH_CACHE_SECONDS = 10.0


@asynccontextmanager
async def server_lifespan(app: FastMCP) -> AsyncIterator[dict[str, object]]:
    """Manage resources across the server lifecycle."""
    logger.info("ShopWired MCP server starting up")
    try:
        yield {}
    finally:
        logger.info("ShopWired MCP server shutting down")
        # Over streamable-http, FastMCP enters this lifespan once per MCP
        # session (per request when stateless) — closing the shared client
        # here would kill other sessions' in-flight requests. The HTTP path
        # closes it in build_http_app's process-level lifespan instead.
        if settings.transport.strip().lower() == "stdio":
            await api_client.close()


def create_server() -> FastMCP:
    """Create and configure the MCP server with all tools."""
    mcp = FastMCP(
        "shopwired",
        instructions=(
            "ShopWired MCP Server — manage products, orders, customers, and "
            "store configuration for a ShopWired e-commerce store. "
            "Use these tools to query and modify store data through the ShopWired API."
        ),
        lifespan=server_lifespan,
    )

    # Register all tool modules
    register_product_tools(mcp)
    register_order_tools(mcp)
    register_customer_tools(mcp)
    register_store_tools(mcp)

    _register_health(mcp)

    return mcp


def _register_health(mcp: FastMCP) -> None:
    """Register the /health endpoint (HTTP transport only; ignored on stdio).

    GET /health            — liveness: the process is up.
    GET /health?deep=true  — readiness: also probes the ShopWired API.

    This endpoint is exempt from bearer auth (platform probes send no headers),
    so it must never echo secrets or internal error details. The deep probe is
    a single attempt with a short timeout that bypasses the shared rate
    limiter, retries, and circuit breaker, and its result is memoized — see
    ShopWiredClient.ping().
    """
    probe_state: dict[str, float | bool] = {"checked_at": 0.0, "ok": False}

    @mcp.custom_route("/health", methods=["GET"])  # type: ignore[untyped-decorator]
    async def health(request: Request) -> JSONResponse:
        payload: dict[str, str] = {"status": "ok", "version": __version__}
        if request.query_params.get("deep") == "true":
            now = time.monotonic()
            if now - float(probe_state["checked_at"]) > DEEP_HEALTH_CACHE_SECONDS:
                probe_state["ok"] = await api_client.ping()
                probe_state["checked_at"] = now
            if probe_state["ok"]:
                payload["shopwired_api"] = "ok"
            else:
                payload["status"] = "degraded"
                payload["shopwired_api"] = "unreachable"
                return JSONResponse(payload, status_code=503)
        return JSONResponse(payload)


def build_http_app(server: FastMCP | None = None) -> Starlette:
    """Build the streamable-http ASGI app with auth attached.

    This is the production composition — main() serves exactly this app, and
    tests exercise it via this same factory so a dropped or reordered
    middleware cannot slip through.
    """
    mcp_server = server if server is not None else create_server()
    app = mcp_server.streamable_http_app()
    add_auth(app)

    # Close the shared API client when the *process-level* app lifespan exits.
    # (The FastMCP lifespan can't do this — it runs per session; see
    # server_lifespan.)
    inner_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan_with_client_close(app_: Starlette) -> AsyncIterator[None]:
        async with inner_lifespan(app_):
            try:
                yield
            finally:
                await api_client.close()

    app.router.lifespan_context = lifespan_with_client_close
    return app


def main() -> None:
    """CLI entry point.

    Transport is selected by SHOPWIRED_TRANSPORT:
      - "stdio" (default) — local use (Claude Desktop / Code via the installer)
      - "streamable-http" — remote use (deployed container behind HTTPS)
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )

    if not settings.validate_credentials():
        sys.exit(1)

    transport = settings.transport.strip().lower()
    if transport not in VALID_TRANSPORTS:
        print(
            f"ERROR: Unknown SHOPWIRED_TRANSPORT '{settings.transport}'.\n"
            f"Valid values: {', '.join(VALID_TRANSPORTS)}.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("Starting ShopWired MCP Server...", file=sys.stderr)
    print(f"  API Base: {settings.api_base_url}", file=sys.stderr)
    print(f"  Transport: {transport}", file=sys.stderr)
    print(
        f"  Rate Limit: {settings.rate_limit_rate} req/s (burst: {settings.rate_limit_burst})",
        file=sys.stderr,
    )

    server = create_server()

    if transport == "stdio":
        server.run(transport="stdio")
        return

    # --- Remote (HTTP) ---
    # Once the server is reachable over the network, the ShopWired API is only
    # as protected as this token. Refuse to start an unauthenticated public
    # server — same fail-fast philosophy as the credential check above.
    if not settings.auth_token.get_secret_value():
        print(
            "ERROR: SHOPWIRED_AUTH_TOKEN must be set when running over HTTP.\n"
            "An HTTP server without a token exposes your store to anyone.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Build the ASGI app ourselves instead of server.run(): run() constructs a
    # fresh app internally, so middleware attached beforehand would be lost.
    import uvicorn

    uvicorn.run(
        build_http_app(server),
        host=settings.host,
        port=settings.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()

"""Bearer-token authentication for the remote (HTTP) transport.

When the server runs over HTTP it is reachable by anyone who knows the URL.
This middleware is the gate: every request must carry a valid bearer token in
the Authorization header, or it is rejected before reaching any tool.

Used only by the streamable-http transport; local stdio never imports this.
"""

from __future__ import annotations

import hmac

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .config import settings

# Paths reachable without a token. Platform health probes (Cloud Run, Render)
# don't send Authorization headers, so /health must stay open — which is also
# why the health endpoint must never include secrets or internal error detail.
EXEMPT_PATHS = frozenset({"/health"})


def _unauthorized() -> JSONResponse:
    return JSONResponse(
        {"error": "unauthorized"},
        status_code=401,
        headers={"WWW-Authenticate": "Bearer"},
    )


class BearerTokenMiddleware(BaseHTTPMiddleware):
    """Reject any request that doesn't present the configured bearer token."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Normalize trailing slashes before the exemption check: this runs
        # before Starlette's redirect_slashes, and probes configured as
        # "/health/" must not be 401'd into a platform restart loop.
        path = request.url.path.rstrip("/") or "/"
        if path in EXEMPT_PATHS:
            return await call_next(request)

        expected = settings.auth_token.get_secret_value()
        # Fail closed: server.py refuses to start without a token, but if that
        # check is ever bypassed, an empty token must not mean "open server".
        if not expected:
            return _unauthorized()

        scheme, _, token = request.headers.get("authorization", "").partition(" ")
        if scheme.lower() != "bearer" or not token:
            return _unauthorized()

        # Constant-time compare: `==` returns at the first differing character,
        # leaking token prefixes through response timing.
        if not hmac.compare_digest(token.strip(), expected):
            return _unauthorized()

        return await call_next(request)


def add_auth(app: Starlette) -> None:
    """Attach the bearer-token middleware to the ASGI app."""
    app.add_middleware(BearerTokenMiddleware)

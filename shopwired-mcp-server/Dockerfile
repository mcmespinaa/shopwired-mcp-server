# ShopWired MCP Server — container image for remote (HTTP) deployment.
# Works on Cloud Run, Render, Railway, Fly, or any container host.
FROM python:3.12-slim

# uv: fast, reproducible installs from the committed lockfile.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first (cached layer) using the lockfile for exact versions.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Now the source, then install the project itself.
COPY src ./src
COPY README.md ./
RUN uv sync --frozen --no-dev

# The one setting that differs from the code defaults (config.py already
# defaults host=0.0.0.0, port=8080).
ENV SHOPWIRED_TRANSPORT=streamable-http

EXPOSE 8080

# Respect the platform's $PORT if provided (Cloud Run, Render set it), else 8080.
# --no-sync: the env is fully materialized at build time; don't re-resolve it
# on every scale-to-zero cold start.
CMD ["sh", "-c", "SHOPWIRED_PORT=${PORT:-8080} uv run --no-sync shopwired-mcp"]

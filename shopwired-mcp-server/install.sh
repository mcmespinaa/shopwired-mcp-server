#!/usr/bin/env bash
#
# ShopWired MCP Server — one-click installer (macOS / Linux)
#
# What this does:
#   1. Ensures `uv` is installed (installs it if missing — no admin needed)
#   2. Installs the server's dependencies from the locked versions (uv sync)
#   3. Collects your ShopWired API credentials
#   4. Registers the server with Claude Code so it launches automatically
#
# Run it from inside the project folder:   ./install.sh
#
set -euo pipefail

# Resolve the directory this script lives in, so the install works no matter
# where the folder is copied to / the USB stick is mounted.
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_NAME="shopwired"

echo "==> ShopWired MCP installer"
echo "    Installing from: $PROJECT_DIR"
echo

# ---------------------------------------------------------------------------
# Step 1: ensure uv is available
# ---------------------------------------------------------------------------
if ! command -v uv >/dev/null 2>&1; then
  echo "==> 'uv' not found — installing it (user-level, no sudo)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # uv installs to ~/.local/bin or ~/.cargo/bin; make it visible for this run
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi
echo "==> uv: $(uv --version)"
echo

# ---------------------------------------------------------------------------
# Step 2: install dependencies from the lockfile (reproducible, exact versions)
# ---------------------------------------------------------------------------
echo "==> Installing dependencies (this may take a minute on first run)..."
( cd "$PROJECT_DIR" && uv sync )
echo "==> Dependencies installed."
echo

# ---------------------------------------------------------------------------
# Step 3: collect credentials
# ---------------------------------------------------------------------------
collect_credentials() {
  # Prompt for each value, looping until the user enters something non-empty so
  # we never register a server that will fail on its first API call. The secret
  # is read with -s so it isn't echoed to the terminal.
  while [ -z "${API_KEY:-}" ]; do
    read -rp "ShopWired API Key: " API_KEY
    [ -z "$API_KEY" ] && echo "  (required — please enter your API key)"
  done
  while [ -z "${API_SECRET:-}" ]; do
    read -rsp "ShopWired API Secret: " API_SECRET; echo
    [ -z "$API_SECRET" ] && echo "  (required — please enter your API secret)"
  done
}

collect_credentials

# ---------------------------------------------------------------------------
# Step 4: register with Claude Code (passes creds via the env block, so no
#         .env file is needed on the target machine)
# ---------------------------------------------------------------------------
if command -v claude >/dev/null 2>&1; then
  echo "==> Registering '$SERVER_NAME' with Claude Code..."
  claude mcp add "$SERVER_NAME" \
    --env "SHOPWIRED_API_KEY=$API_KEY" \
    --env "SHOPWIRED_API_SECRET=$API_SECRET" \
    -- uv run --directory "$PROJECT_DIR" shopwired-mcp
  echo "==> Done. Restart Claude Code and the ShopWired tools will be available."
else
  echo "==> Claude Code CLI not found. Add this to your Claude Desktop config manually:"
  echo "    (~/Library/Application Support/Claude/claude_desktop_config.json)"
  cat <<EOF

  "mcpServers": {
    "$SERVER_NAME": {
      "command": "uv",
      "args": ["run", "--directory", "$PROJECT_DIR", "shopwired-mcp"],
      "env": {
        "SHOPWIRED_API_KEY": "$API_KEY",
        "SHOPWIRED_API_SECRET": "$API_SECRET"
      }
    }
  }
EOF
fi

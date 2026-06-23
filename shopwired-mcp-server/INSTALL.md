# Installing the ShopWired MCP Server

A one-click installer is included for transferring this server to another
machine (USB stick, clone, or download). It works on any OS that can run
`uv` — no manual Python setup required.

## What you need on the target machine

- Internet access on first install (to download dependencies)
- That's it. The installer fetches `uv` automatically if it's missing.

## macOS / Linux

```bash
cd shopwired-mcp-server
./install.sh
```

## Windows

```bat
cd shopwired-mcp-server
install.bat
```

## What the installer does

1. Installs `uv` (Astral's Python package manager) if it isn't already present —
   user-level, no admin rights needed.
2. Runs `uv sync` to build a virtual environment with the **exact** dependency
   versions pinned in `uv.lock`.
3. Prompts you for your `SHOPWIRED_API_KEY` and `SHOPWIRED_API_SECRET`.
4. Registers the server with Claude Code (`claude mcp add`), passing the
   credentials through the environment. If the Claude Code CLI isn't found, it
   prints a ready-to-paste Claude Desktop config block instead.

After it finishes, restart Claude Code (or Claude Desktop) and the ShopWired
tools will be available.

## Credentials never travel on the USB stick

The installer asks for your API key and secret **on the target machine** — they
are not stored in this folder or committed to git (`.env` is git-ignored). The
credentials end up only inside your Claude client config.

## Transferring via USB

Copy the whole project folder, **excluding** these (they're machine-specific or
secret and will be regenerated/re-entered on the target):

- `.venv/` — rebuilt by `uv sync`
- `.env` — re-entered by the installer
- `.pytest_cache/`, `__pycache__/`, `.DS_Store`

The cleanest way to produce a transfer-ready copy is:

```bash
git archive --format=zip HEAD -o shopwired-mcp-server.zip
```

This zips only the tracked files (~600 KB), which is exactly what the installer
needs.

## Uninstall

```bash
claude mcp remove shopwired
```

Then delete the project folder.

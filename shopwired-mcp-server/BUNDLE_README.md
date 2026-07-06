# ShopWired MCP Server — Install Guide

You've received this folder so your AI assistant (Claude) can work directly
with a ShopWired store: check orders, update stock, create discount codes,
look up customers — by asking in plain English.

Setup takes about 2 minutes.

## What you need

1. **A ShopWired API key and secret.** Get them from the ShopWired admin:
   *Your Account → API & Webhooks → Add API key.* Ask your store admin if you
   don't have access.
2. **Claude Code or the Claude desktop app** installed.
3. Internet access (first run downloads dependencies).

No Python setup needed — the installer handles everything.

## Install

**macOS / Linux** — open Terminal in this folder and run:

```bash
bash install.sh
```

**Windows** — double-click `install.bat` (or run it from Command Prompt).

The installer will:

1. Set up its own Python environment (no admin rights needed)
2. Ask for your ShopWired API key and secret — typed on your machine,
   never stored in this folder
3. Register the server with Claude Code automatically

If you use **Claude Desktop or Claude Cowork** instead of Claude Code, the
installer prints a config block at the end — paste it into the file at
*Claude app → Settings → Developer → Edit Config*, save, and restart the
Claude app.

## Try it

Restart Claude, then ask things like:

- *"Show me my latest orders"*
- *"How many products are low on stock?"*
- *"Create a 10% discount code called WELCOME10"*

Deleting anything always requires an explicit confirmation — the assistant
can't wipe data on a misunderstanding.

## If something goes wrong

- **"uv: command not found" after install** — close and reopen your terminal,
  then run the installer again.
- **Tools don't appear in Claude** — fully quit and reopen the Claude app
  (or run `claude mcp list` in Claude Code to check the server is registered).
- **"API credentials must be set"** — the key/secret were mistyped; just run
  the installer again.

## Uninstall

```bash
claude mcp remove shopwired
```

Then delete this folder. (Claude Desktop users: remove the `shopwired` block
from the config file instead.)

---

Full documentation, source code, and updates:
https://github.com/mcmespinaa/shopwired-mcp-server

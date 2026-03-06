# Contributing to ShopWired MCP Server

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Setup

```bash
git clone https://github.com/mcmespinaa/shopwired-mcp-server.git
cd shopwired-mcp-server/shopwired-mcp-server
uv sync --dev
cp .env.example .env  # fill in your credentials
```

## Running Tests

```bash
uv run python -m pytest tests/ -v
uv run python -m pytest tests/ --cov=shopwired_mcp  # with coverage
```

## Code Style

This project uses strict linting and type checking:

```bash
uv run ruff check src/ tests/     # lint
uv run ruff format src/ tests/    # format
uv run mypy src/                  # type check (strict mode)
```

- **Ruff** rules: E, F, I, N, W, UP, B, SIM
- **mypy** strict mode enabled
- Line length: 100 characters

## Pull Requests

1. Create a feature branch from `main`
2. Make your changes with tests
3. Ensure `ruff check`, `mypy`, and `pytest` all pass
4. Submit a PR with a clear description of the change

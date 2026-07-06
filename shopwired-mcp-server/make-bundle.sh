#!/usr/bin/env bash
#
# Build the distributable bundle: dist/shopwired-mcp-bundle-<version>.zip
#
# The bundle is the server source minus machine-specific/dev artifacts, with
# BUNDLE_README.md installed as the bundle's README.md (recipients get install
# instructions, not the GitHub-facing docs). Run after any release change.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

VERSION=$(grep -m1 '^version' pyproject.toml | sed 's/.*"\(.*\)".*/\1/')
BUNDLE=dist/shopwired-mcp-bundle

rsync -a --delete \
  --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='.pytest_cache' --exclude='.mypy_cache' --exclude='.DS_Store' \
  --exclude='.obsidian' --exclude='shopwired-fixes' --exclude='dist' \
  --exclude='.git' --exclude='make-bundle.sh' --exclude='BUNDLE_README.md' \
  ./ "$BUNDLE/"

# Recipient-facing README replaces the repo README inside the bundle.
cp BUNDLE_README.md "$BUNDLE/README.md"

(
  cd dist
  rm -f "shopwired-mcp-bundle-${VERSION}.zip"
  zip -rq "shopwired-mcp-bundle-${VERSION}.zip" shopwired-mcp-bundle
)

echo "Built dist/shopwired-mcp-bundle-${VERSION}.zip ($(du -h "dist/shopwired-mcp-bundle-${VERSION}.zip" | cut -f1 | tr -d ' '))"

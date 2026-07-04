# Deploying the ShopWired MCP Server as a Remote Server

This runs the server over HTTP behind HTTPS so MCP clients connect to a URL
instead of spawning a local process. Single-tenant: the server holds **one**
set of ShopWired API keys and is protected by **one** bearer token.

The same container image runs on any host. Cloud Run is the recommended default
(free tier, scale-to-zero). Render and a generic VPS are documented too.

## Required environment variables

| Variable | Purpose |
|---|---|
| `SHOPWIRED_API_KEY` | Your ShopWired API key |
| `SHOPWIRED_API_SECRET` | Your ShopWired API secret |
| `SHOPWIRED_AUTH_TOKEN` | A long random string clients must send as `Authorization: Bearer <token>`. **The server refuses to start over HTTP without it.** |
| `SHOPWIRED_TRANSPORT` | `streamable-http` (set by the Dockerfile already) |

Generate a strong token:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Option A — Google Cloud Run (recommended, free tier)

Prerequisites: a GCP project with billing enabled, `gcloud` CLI installed.

```bash
# 1. Build and push the image (Cloud Build does it for you)
gcloud run deploy shopwired-mcp \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --set-env-vars SHOPWIRED_TRANSPORT=streamable-http \
  --set-env-vars SHOPWIRED_API_KEY=YOUR_KEY \
  --set-env-vars SHOPWIRED_API_SECRET=YOUR_SECRET \
  --set-env-vars SHOPWIRED_AUTH_TOKEN=YOUR_LONG_RANDOM_TOKEN
```

- `--min-instances 0` is what keeps it free (scale-to-zero when idle).
- `--allow-unauthenticated` means Cloud Run's own IAM is off — your bearer
  token is the auth layer. (Alternatively, use Cloud Run IAM and drop the token,
  but bearer-token is simpler for MCP clients.)
- Better than env vars for secrets: store them in **Secret Manager** and use
  `--set-secrets SHOPWIRED_API_SECRET=shopwired-secret:latest`.

The command prints a URL like `https://shopwired-mcp-xxxx.run.app`.
Your MCP endpoint is that URL + `/mcp`.

---

## Option B — Render

1. New → Web Service → connect this repo.
2. Render auto-detects the Dockerfile.
3. Add the env vars above under **Environment**.
4. Deploy. Note: free Render web services sleep after 15 min idle (cold start
   on next call, same trade-off as Cloud Run scale-to-zero).

Endpoint: your Render URL + `/mcp`.

---

## Option C — Your own VPS

```bash
docker build -t shopwired-mcp .
docker run -d -p 8080:8080 \
  -e SHOPWIRED_TRANSPORT=streamable-http \
  -e SHOPWIRED_API_KEY=YOUR_KEY \
  -e SHOPWIRED_API_SECRET=YOUR_SECRET \
  -e SHOPWIRED_AUTH_TOKEN=YOUR_LONG_RANDOM_TOKEN \
  shopwired-mcp
```

Put a reverse proxy (Caddy or nginx) in front for HTTPS — never expose raw
HTTP to the internet. Caddy example:

```
mcp.yourdomain.com {
    reverse_proxy localhost:8080
}
```

---

## Health checks

The HTTP server exposes `GET /health` (no auth required, safe for platform
probes):

- `GET /health` — liveness: returns `{"status": "ok", "version": "..."}`.
- `GET /health?deep=true` — readiness: also probes the ShopWired API
  (bypassing the cache); returns 503 with `"status": "degraded"` if the API
  is unreachable.

Point Cloud Run / Render health checks at `/health`. Use `deep=true` for
manual verification after deploy, not for high-frequency probes — each call
costs a ShopWired API request.

## Connecting a client

Point your MCP client at the deployed URL with the bearer token. For Claude
Code:

```bash
claude mcp add --transport http shopwired https://YOUR-URL/mcp \
  --header "Authorization: Bearer YOUR_LONG_RANDOM_TOKEN"
```

## Security checklist before going live

- [ ] `SHOPWIRED_AUTH_TOKEN` is long and random (32+ bytes)
- [ ] Secrets are in Secret Manager / host secret store, not committed
- [ ] HTTPS only (Cloud Run/Render give this free; VPS needs a proxy)
- [ ] Token comparison is constant-time (see `src/shopwired_mcp/auth.py`)
- [ ] Consider rotating the token periodically

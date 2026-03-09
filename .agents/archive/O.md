# Agent O — Deployment + Access Control

## Verify Results

- `docker build -t ontology-engine .` — PASS
- Contract validation — PASS (Dockerfile produces working image with all deps)
- Scope boundary respected — YES (only new files in scope paths)

## Shared File Requests

(None — all files created are new scope files)

## Changes

```
 .dockerignore       |  25 +++++++
 .env.production     |  36 +++++++++
 Dockerfile          |  63 ++++++++++++++++
 docs/DEPLOYMENT.md  | 152 ++++++++++++++++++++++++++++++++++++++
 railway.toml        |  17 +++++
 vercel.json         |  27 +++++++
 web/.env.production |  12 +++
 7 files changed, 332 insertions(+)
```

## Notes

- Dockerfile uses multi-stage build (builder → runtime) with non-root user
- Builder stage needed `src/` + `README.md` alongside `pyproject.toml` for setuptools to resolve egg_base
- Railway auto-injects `PORT` — the Dockerfile CMD reads it via shell expansion
- Vercel config uses SPA catch-all rewrite + immutable cache headers for hashed assets
- `.env.production` files use `CHANGEME` placeholders — user must set real values in platform dashboards
- No test files created since deployment config is verified via `docker build` (not unit-testable)

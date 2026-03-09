# Deployment Guide — Ontology Engine

The Ontology Engine runs on **3 free-tier services**:

| Service      | Role                     | URL Pattern                       |
| ------------ | ------------------------ | --------------------------------- |
| **Railway**  | FastAPI backend (Docker) | `https://your-app.up.railway.app` |
| **Vercel**   | Vite frontend (static)   | `https://your-app.vercel.app`     |
| **Supabase** | Auth + DB + Storage      | `https://xxx.supabase.co`         |

---

## Prerequisites

- GitHub account with this repo pushed
- [Railway](https://railway.app) account (free tier: 500 execution hours/month)
- [Vercel](https://vercel.com) account (free tier: unlimited static deploys)
- [Supabase](https://supabase.com) project (already configured)

---

## 1. Deploy Backend to Railway

### 1a. Create Railway Project

1. Go to [railway.app/new](https://railway.app/new)
2. Select **"Deploy from GitHub Repo"**
3. Connect your GitHub account and select the `Ontology_Engine` repo
4. Railway auto-detects the `Dockerfile` and `railway.toml`

### 1b. Set Environment Variables

In Railway Dashboard → your service → **Variables**, add:

```
SUPABASE_URL=https://fareqnzxhodvgdkboeff.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_KEY=<your-service-role-key>
SUPABASE_JWT_SECRET=<your-jwt-secret>
GEMINI_API_KEY=<your-gemini-key>
API_ENABLED=true
CORS_ORIGINS=https://your-app.vercel.app
```

> **Note:** Railway injects `PORT` automatically — do not set it manually.

### 1c. Verify Deployment

Once deployed, visit your Railway URL:

```bash
curl https://your-app.up.railway.app/
# Should return: {"name":"Ontology Engine","version":"0.1.0", ...}
```

---

## 2. Deploy Frontend to Vercel

### 2a. Create Vercel Project

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import the `Ontology_Engine` GitHub repo
3. Vercel auto-detects `vercel.json` config
4. Framework preset: **Vite**
5. Root directory: leave as `/` (vercel.json handles `cd web`)

### 2b. Set Environment Variables

In Vercel Dashboard → Project → **Settings → Environment Variables**, add:

```
VITE_SUPABASE_URL=https://fareqnzxhodvgdkboeff.supabase.co
VITE_SUPABASE_ANON_KEY=<your-anon-key>
VITE_API_BASE_URL=https://your-app.up.railway.app
```

### 2c. Verify Deployment

Visit your Vercel URL — you should see the login page.

---

## 3. Wire Production URLs

After both services are deployed, update these cross-references:

### 3a. Railway: Update CORS

Set `CORS_ORIGINS` in Railway to your **Vercel frontend URL** (no trailing slash):

```
CORS_ORIGINS=https://your-app.vercel.app
```

### 3b. Supabase: Add Redirect URL

1. Go to Supabase Dashboard → **Authentication → URL Configuration**
2. Add your Vercel URL to **Redirect URLs**:

```
https://your-app.vercel.app/**
```

### 3c. Vercel: Update API URL

Set `VITE_API_BASE_URL` in Vercel to your **Railway backend URL** (no trailing slash):

```
VITE_API_BASE_URL=https://your-app.up.railway.app
```

---

## 4. Local Development

The local setup remains unchanged:

```bash
# Backend
source .venv/bin/activate
uvicorn ontology_engine.api:app --reload --port 8000

# Frontend
cd web && npx vite --host 0.0.0.0 --port 5173
```

---

## Environment Files Reference

| File                  | Purpose                          | Committed? |
| --------------------- | -------------------------------- | ---------- |
| `.env`                | Local dev secrets                | ❌ No      |
| `.env.production`     | Backend production **template**  | ✅ Yes     |
| `web/.env.local`      | Frontend local dev               | ❌ No      |
| `web/.env.production` | Frontend production **template** | ✅ Yes     |
| `web/.env.example`    | Frontend example                 | ✅ Yes     |

> ⚠️ Templates contain `CHANGEME` placeholders. **Never** commit files with real secrets.

---

## Troubleshooting

| Issue                    | Cause                                     | Fix                                                     |
| ------------------------ | ----------------------------------------- | ------------------------------------------------------- |
| CORS errors in browser   | `CORS_ORIGINS` doesn't match frontend URL | Update Railway env var to exact Vercel URL              |
| 401 on `/api/analyze`    | Missing/wrong Supabase JWT secret         | Verify `SUPABASE_JWT_SECRET` matches Supabase dashboard |
| OCR fails in prod        | Tesseract not installed                   | Dockerfile installs it — verify Docker build succeeded  |
| Frontend can't reach API | Wrong `VITE_API_BASE_URL`                 | Update in Vercel env vars, redeploy                     |
| Railway returns 502      | App crashed on startup                    | Check Railway logs; ensure all env vars are set         |

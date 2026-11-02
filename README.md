# Velora Toons backend

FastAPI metadata API for Velora Toons. This repository contains `backend/`; the frontend lives at https://github.com/Bhavishyadalal/Velora-toons.

## Local setup

From this repository root, using Python 3.12+:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements-dev.txt
python -m pytest backend -q
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 10000
```

## Render deployment

Connect this repository to Render as a Blueprint using root `render.yaml`. Dockerfile is `backend/Dockerfile`, Docker context is `backend`, and health path is `/health`. Set `ALLOWED_ORIGINS` to the exact frontend HTTPS origin. Keep `ENABLE_BROWSER_SEASONS=0` for the standard lightweight image. No media bytes are relayed or stored.

The optional browser image requires separate resource and live season verification. See [Render setup](docs/DEPLOY_RENDER.md), [API](docs/API.md), [security](docs/SECURITY.md), and [validation](docs/VALIDATION.md).

Set the resulting Render URL in `frontend/config.js` in the frontend repository, then redeploy that site. Health and fixture tests do not verify live source access or provider playback.

Shared documentation and handoff notes came from the combined ZIP. Commands mentioning `frontend/` must run in the frontend repository. Do not commit environment secrets.

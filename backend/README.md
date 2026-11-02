# Backend

From the repository root install `backend/requirements-dev.txt`. Run inside this folder:

```sh
uvicorn app.main:app --host 127.0.0.1 --port 10000
```

Set environment variables in your shell or deployment environment. `.env.example` is a template; this program does not automatically read a `.env` file. For local defaults no env file is required. For production set exact `ALLOWED_ORIGINS`.

Tests from root: `python -m pytest backend -q`. They use synthetic fixtures and mocked transport, not live source traffic. See [API](../docs/API.md) and [source adapter](../docs/SOURCE_ADAPTER.md).

`Dockerfile` contains no browser and supports static/default-season metadata. `Dockerfile.browser` is an optional heavier variant for dynamic season selection; see [Render instructions](../docs/DEPLOY_RENDER.md). The browser is downloaded only when building that optional image. Never bundle local browser profiles or cookies into it.

The API does not relay any video body. A successful health endpoint is not a successful source-resolution test. Do a real source check after deployment.

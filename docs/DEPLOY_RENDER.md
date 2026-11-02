# Deploy the backend on Render

## Recommended default: lightweight web service

Push the complete repository first. In Render choose **New → Blueprint** and connect that repository. The root `render.yaml` defines a free-plan Docker **web service**, not a background worker. It uses:

- Dockerfile: `backend/Dockerfile`
- Docker context: `backend`
- Health path: `/health`
- Startup: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- `ALLOWED_ORIGINS`: enter the exact frontend origin, e.g. `https://your-project.vercel.app`. Multiple approved origins can be comma-separated. No trailing paths or wildcard.
- `ENABLE_BROWSER_SEASONS=0`

If creating a service manually, keep those Docker paths relative to the repository root. No separate build/start commands are needed for Docker. The app must listen on Render's PORT; the Docker CMD handles this.

Wait for Live, open `https://YOUR-SERVICE.onrender.com/health`, and confirm `status: ok` and `media_proxy: false`. This tests startup, not source access. Next open `/api/catalog?kind=cartoon` and check real titles. If that fails, inspect the API's error and service logs; do not disable certificate validation.

Set the backend URL in the frontend `config.js`, then redeploy the frontend. Alternatively enter it through Your space on the device.

## Optional: dynamically loaded seasons

The source renders some seasons through its own JavaScript UI. The default HTML may contain only one season's episodes. To fetch other seasons:

1. Select `backend/Dockerfile.browser` instead of the normal Dockerfile.
2. Keep Docker context `backend`.
3. Set `ENABLE_BROWSER_SEASONS=1`.
4. Verify memory usage and the `/api/season/{id}?number=N` route.

This image downloads Chromium **during image build**, not into the ZIP or frontend. It is larger, launches one browser operation at a time, and can consume enough memory to fail on a small instance. This adapter has not been executed in the supplied environment. It uses the ordinary season dropdown; it does not solve source verification challenges. Keep the standard image if default-season browsing is sufficient.

If you later change `render.yaml`, remember that a Blueprint may synchronize settings. To make the optional variant permanent, update its Dockerfile path and ENABLE_BROWSER_SEASONS value in the blueprint too.

## Free hosting reality

Free-service availability, quotas and inactivity behavior are controlled by Render and may change. A sleeping backend can delay the first request. The frontend permits a 45-second request then offers retry. Do not promise lifetime free uptime or use a cron job as a guarantee. An uptime ping cannot fix source restrictions, quota exhaustion, or memory limits. Confirm current terms at https://render.com/docs/free.

## Troubleshooting

- **No open ports**: ensure this is a web service and Docker CMD has not been overridden.
- **CORS error**: add the exact deployed frontend origin to ALLOWED_ORIGINS, redeploy, and refresh.
- **502 source_unavailable**: inspect DNS/connection/source response from that deployment. Health can still be healthy.
- **season_unavailable**: source doesn't list the season, browser mode is disabled, or the optional adapter failed.
- **Out of memory**: return to standard Dockerfile; optional browser mode is heavier.
- **Source requires verification**: use its public page; do not add bypass code.
- **Port/server works but iframe fails**: embedding belongs to the provider, not Render. Use Open player.

The backend is public and has no account system. CORS is browser policy, not authentication. Use private hosting or add proper authentication if you need a private service; do not put an API secret in frontend config.

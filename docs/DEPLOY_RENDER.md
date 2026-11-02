# Deploy the backend on Render

## Quick setup for these two repositories

1. Sign in to Render, connect GitHub, and allow access to `Bhavishyadalal/Velora-toons-backend-`.
2. Choose **New → Blueprint**, select that backend repository and branch `main`. Render reads `render.yaml` from the repository root.
3. Enter `ALLOWED_ORIGINS` as your actual frontend origin, such as `https://your-site.vercel.app`. Use no trailing path. If the frontend is not deployed yet, leave the local development origins (`http://localhost:5173,http://127.0.0.1:5173`) temporarily and replace them before connecting the hosted frontend.
4. Review the service and plan before creating it. The blueprint requests a free Docker web service. Keep `ENABLE_BROWSER_SEASONS=0`. If Render does not offer that plan for your account, review its current options before choosing a paid service.
5. Deploy and wait for **Live**. Open `https://YOUR-SERVICE.onrender.com/health`; expect HTTP 200 and `status: ok`. The root `/` is not a website and can return 404.
6. Open `https://YOUR-SERVICE.onrender.com/api/catalog?kind=cartoon` and check that it returns real catalogue items. A successful health check alone does not verify the source.
7. Share the public Render base URL and your public frontend URL with the coding assistant. No credentials are needed for this configuration. The frontend setting to update is `frontend/config.js` in `Bhavishyadalal/Velora-toons`, followed by a Vercel redeploy. Device settings in **Your space** override that file.

For a manual **New → Web Service** instead, select the backend repository and `main`, choose Docker, leave Root Directory blank, use Dockerfile Path `backend/Dockerfile`, Docker Build Context Directory `backend`, and Health Check Path `/health`. Add the same environment variables above. Keep the Docker command default; no separate Python build/start command is needed. Set auto-deploy from `main` if desired.

## External cron or uptime monitor

Create an external HTTP check, for example in cron-job.org, with these settings:

| Setting | Value |
| --- | --- |
| URL | `https://YOUR-SERVICE.onrender.com/health` |
| Method | GET (HEAD is also supported) |
| Schedule | Every 10 minutes (`*/10 * * * *` in five-field cron syntax) |
| Success | HTTP 200; GET response contains `status: ok` |
| Timeout | Allow up to 60 seconds if the monitoring service supports it |
| Authentication/body | None |

Enable failure alerts if offered. The endpoint performs no source request or video transfer, and sends `Cache-Control: no-store`. Do not poll `/api/catalog` or video providers just to keep the app awake. An external check runs independently of a closed website; browser timers and a cron process inside a sleeping Render service are not reliable wake-up mechanisms.

Periodic requests may reduce idle sleeping if Render's current plan permits it. They consume service hours and cannot guarantee 24/7 uptime, recover exhausted quotas, or override Render's policies. Check [Render's current free-service limits](https://render.com/docs/free). For dependable availability, use a plan designed to stay running; even that is subject to provider outages. A healthy app can still have source or player failures.

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

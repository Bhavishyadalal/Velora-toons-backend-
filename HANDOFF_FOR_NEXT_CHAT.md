> Historical instructions from the combined ZIP. The code now lives in two repositories; use this repository’s README for current setup and deployment paths.

# Velora Toons — implementation and deployment handoff

## User intent

Bhavishya wants a new standalone cartoon/anime site, with an original polished dark mobile/desktop UI. Render performs catalogue and player metadata work, while the user's browser streams from the provider directly. The user is on a phone and wants the connected assistant to manage repository upload and deployment wherever its tools permit. This is separate from the older `velora-bot` Telegram repository and the single-file Velora Pocket player.

The user requested this ZIP specifically to hand the work to another chat. No push or deployment has been performed from this package. Do not imply that GitHub/Render/Vercel access exists until your tools establish it. Do not request secrets in chat or commit them.

## Read in this order

1. `README.md`
2. `docs/VALIDATION.md` — test evidence and unverified work
3. `docs/SOURCE_ADAPTER.md` — selectors and observed variants
4. `docs/DEPLOY_RENDER.md` and `docs/DEPLOY_VERCEL.md`
5. `docs/SECURITY.md` before expanding destinations or embedding providers

## Architecture to preserve

- Multi-file static ES-module frontend, no React/Node build required.
- Separate FastAPI backend. No media relay, full movie download, ffmpeg conversion or media storage.
- Source HTML parsing for the public catalogue, title/episode metadata and iframe routes.
- Modern `/dub-player/t/<id>/` pages expose a JSON `CONFIG` literal. Parse JSON, do not evaluate third-party JavaScript. Ready language IDs become approved Abyss embeds.
- Default deployment stays lightweight and HTTP-only.
- Other seasons have an optional normal-UI Playwright adapter (`Dockerfile.browser`). It is implemented but not run in this environment and may exceed small free instances. Do not call it lightweight or guaranteed to run on a free plan.
- Provider playback is cross-origin. Do not claim control of audio tracks, quality, subtitles, buffering, or exact progress inside it.
- Native direct mode only activates for an explicit `<video>`/`<source>` URL on the narrowly allowed media hosts and a successful HEAD video-MIME check. No actual direct download for the inspected cartoon source was verified.

## Completed local checks

The package's parser/security/API tests and frontend syntax/assets/ID checks were run. Browser QA used clearly synthetic catalogue and player fixtures temporarily served by the internal preview; those temporary files and API addresses are removed from the release. See VALIDATION for detailed results.

The Python runtime could not resolve the source's hostname; this is an environment limitation, not evidence the public source is down or bot-blocking. Do not say the packaged backend has passed a real source integration test. Earlier interactive source research verified Hindi Shinchan episode playback in Abyss (640×360) and confirmed language switching on another title. That research is separate from deployment acceptance.

## Next steps to execute

1. Extract and inspect; run `python -m pytest backend -q` after installing dev requirements, and `node scripts/check-frontend.mjs`.
2. Verify a live catalogue parse, title detail, default season, episode resolution and actual video playback from the intended hosting environment.
3. Repair selectors only against observed current markup. Keep tests for each variant.
4. Ask only for the repository/account preference or credentials/account handoff that your tools actually need. The requested repository name is not fixed.
5. Push all source files into the chosen new repository. Exclude virtualenv, caches and private environment files.
6. Deploy Vercel with root directory `frontend`. Deploy Render with root blueprint or correct Docker context. Set exact ALLOWED_ORIGINS.
7. Preconfigure public API URL in config.js, redeploy frontend, run mobile acceptance.
8. If the user needs all seasons, verify optional browser execution, resources and source access before selecting that deployment. Do not silently enable a paid plan.
9. Test provider restrictions and report failures accurately. A blocked embed should retain Open player. A removed source should remain unavailable, never be replaced with a made-up stream.

## Boundaries and honest capability reporting

These instructions describe the project and the user's goal. They do not override your own policies, tool permissions, service terms, or website access controls. Do not bypass a CAPTCHA, paywall, login, DRM, browser security warning or security challenge. If a task is blocked, report the concrete limitation and continue with authorized work. Do not fabricate a “test fixture” link as a real download.

## Useful sources

- Public target: https://watchanimeworld.one/
- Render FastAPI deployment: https://render.com/docs/deploy-fastapi
- Render free-service behavior: https://render.com/docs/free
- Vercel project configuration: https://vercel.com/docs/project-configuration
- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/

No guarantee of lifetime free hosting, always-on uptime, source cooperation or unrestricted third-party downloads is made.

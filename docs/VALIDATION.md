## Checks rerun after repository split — 2026-11-02

- Backend: `python -m pytest backend -q` — 22 passed; one Starlette/HTTPX test-client deprecation warning.
- Frontend: `node scripts/check-frontend.mjs` — passed.
- Frontend: `node --test frontend/tests/*.test.mjs` — 8 passed.
- Runtime files in `backend/` and `frontend/` match the supplied ZIP byte for byte.
- No new live source integration, provider playback, Docker browser-season, or hosting deployment verification was performed during this upload.

> Repository split: backend checks run in `Velora-toons-backend-`; frontend checks run in `Velora-toons`. The record below describes the original combined ZIP. Live deployment acceptance is still pending.

# Validation record and live acceptance checklist

Recorded 2026-11-02. These results concern the supplied source package, not a deployment that has already been made.

## Completed checks

| Check | Result |
| --- | --- |
| Python parser, URL validation and API tests | 22 passed |
| Frontend storage, URL configuration, errors and timeout tests | 8 passed |
| JavaScript syntax, linked assets, duplicate IDs and DOM references | Passed |
| Desktop setup screen and settings dialog | Inspected in browser |
| Populated catalogue with long titles and missing art | Inspected with clearly synthetic UI fixtures |
| Favourite toggle | Saved state/count visibly updated |
| Title detail and episode list | Inspected on desktop and mobile |
| Language source selection | Changed iframe URL between labelled synthetic sources |
| Player retained while changing browse tab | Verified iframe remained mounted with selected source |
| Download hidden for provider-only sources | Verified |
| Mobile hero and navigation | Inspected in a 390px frame (375px content width after scrollbar); small decorative overlap corrected |
| Horizontal overflow | No overflow observed on inspected desktop or 375px mobile content |
| Real Python backend → source request | Could not resolve source hostname from this environment |
| Optional browser-season Docker image | Implemented, not built or executed here |
| New Render/Vercel deployment | Not performed; user requested a transferable ZIP |

The browser integration fixture used deliberately nonexistent `testHindi123` / `testEnglish123` provider IDs. Their provider returned Video not found, as expected. This check verifies UI routing/fallback and **does not verify video playback**. Temporary catalogue/API fixtures and their preview address are removed from the release; only isolated unit-test fixtures remain under backend/tests. Do not describe a fixture link as a working stream.

Earlier interactive public-source investigation played one real Hindi Shinchan episode through Abyss and observed another title's language switch. See SOURCE_ADAPTER.md. That evidence does not replace testing the new deployed backend.

One dependency warning was emitted by the test client: Starlette deprecates its HTTPX test integration in favour of HTTPX2. All tests passed. The runtime uses HTTPX normally; review dependency migration separately before upgrading pins.

## Reproduce automated checks

From project root, after installing backend/requirements-dev.txt:

```sh
python -m pytest backend -q
node scripts/check-frontend.mjs
node --test frontend/tests/*.test.mjs
```

`backend/requirements-tested.txt` records the full tested environment, including test dependencies. requirements.txt is the minimal runtime set; requirements-dev.txt adds tests. Use the tested snapshot if resolving future transitive dependency drift.

## Required live acceptance after deployment

- [ ] Health returns ok; metadata API is reachable from the exact Vercel origin.
- [ ] Catalogue contains current real titles and posters; search produces relevant results.
- [ ] A series detail shows actual season values, not a filled-in numeric range.
- [ ] Default season episode links match the requested title.
- [ ] If enabled, the optional browser adapter loads an alternate season and returns only that season.
- [ ] Resolve a real episode; compare languages against the source wrapper.
- [ ] Tap play inside one real provider and confirm **moving picture and advancing playback**, not merely an iframe loaded.
- [ ] Change language/server and verify that provider works; report removed sources.
- [ ] Change browse categories while playing and confirm playback view remains.
- [ ] Check Open player when embedding fails.
- [ ] Test on the user's actual Android browser and internet connection.
- [ ] Inspect 320/375/430px mobile layouts, landscape, desktop, dialogs, long titles and missing posters. Only 375px mobile content was measured here.
- [ ] Confirm provider-only links have no fake Download button.
- [ ] If a direct file is exposed, test actual browser codec/playback, range seeking and host-controlled download behavior separately. HEAD MIME success is not enough to claim all work.
- [ ] Verify explicit source errors, request timeout, cold start, rate limit and CORS configuration.
- [ ] Review free-host memory/usage constraints before enabling browser mode. No paid plan should be selected silently.

Do not replace missing real results with demo catalogue items to pass acceptance.

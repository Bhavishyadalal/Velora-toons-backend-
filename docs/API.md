# API contract

All endpoints are GET. The service never accepts an arbitrary URL for fetching. Content IDs are URL-safe base64 of an allowed source path. IDs are not secrets and must not be treated as authentication.

| Route | Parameters | Response |
| --- | --- | --- |
| `/health` | none | status, service, version, media_proxy |
| `/api/catalog` | kind=cartoon/anime/movies, page_number=1..30, q up to 100 chars | items, has_more, page, source, fetched_at |
| `/api/title/{id}` | encoded series/movie path | title, poster, description, seasons, default_season, episodes, kind |
| `/api/season/{id}` | number=1..999 | episodes for the exact requested season or an explicit error |
| `/api/resolve/{id}` | encoded episode/movie path | players, source, download_note, expires_in |

Catalog item fields: `id`, `title`, `url`, `poster`, `badge`, `year`, `kind`. The source's badge/year text may contain episode counts rather than a calendar year; it is shown as returned, not reinterpreted as authoritative chronology.

Episode fields: `id`, `title`, `url`, `season`, `number`, `poster`. Numbers may be null when a source path has a different naming pattern.

Player fields:

```json
{
  "label": "Abyss · Hindi",
  "language": "hin",
  "language_name": "Hindi",
  "mode": "embed",
  "url": "https://player.abyssplayer.com/EXAMPLE_ID",
  "download_url": null,
  "verified": "public_wrapper"
}
```

The example ID is illustrative, not a real working download. `verified` describes route provenance: `public_wrapper`, `source_iframe`, or `head_video_mime`. It does **not** mean successful full video playback. `mode=direct` is returned only by the explicit-video adapter after HEAD MIME validation.

Errors use:

```json
{"error":{"code":"season_unavailable","message":"Human-readable explanation"}}
```

Invalid IDs/destinations return 400. Source failures return 502. Rate limiting returns 429 and Retry-After. FastAPI query validation uses its standard 422 `detail` response; the frontend falls back to a general request error. There is no POST, webhook, secret query parameter, media endpoint or byte relay.

Successful page metadata has a five-minute in-process cache. `expires_in` describes resolver refresh guidance, not a guarantee that a provider URL remains valid for exactly that period. The UI provides Refresh players.

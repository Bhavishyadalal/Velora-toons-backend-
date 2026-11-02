# Source adapter and research record

Target: https://watchanimeworld.one/. Findings came from public page inspection and normal player interactions. Website markup and providers can change; these are observed variants, not a published official API contract.

## Catalogue and detail

- WordPress with Torofilm-style markup.
- Cards: `article.post`; title `.entry-title`; primary path `a.lnk-blk[href]`; poster `img`; badges `.post-ql` / `.year`.
- Search: `/?s=<query>` with WordPress `/page/N/` pagination.
- Categories: `/category/type/cartoon/?type=series`, `/category/type/anime/?type=series`, and cartoon movies with `?type=movies`.
- Detail paths `/series/<slug>/`, `/movies/<slug>/`; episode paths `/episode/<slug>-<season>x<episode>/`.
- Season controls `[data-season]`, often carrying `data-post`. List only actual available seasons; never fill gaps.
- Other seasons load dynamically through the source's UI. A fresh page exposes AJAX configuration, but the exact action was not verified. This implementation does not invent an action or hardcode a nonce. The optional adapter clicks the normal selector and inspects its returned DOM.

## Episode players

Containers such as `#options-0` and `#options-1` contain lazy iframes with `data-src`. Selection loads that route. The API supports observed hosts only: `watchanimeworld.one`, `watchanimeworld.top`, `player.abyssplayer.com`, `play.zephyrix.org`.

The source often labels MultiCloud first and Abyss second. Several inspected MultiCloud entries returned No Video Found/404. The program does not claim every source is playable or silently select a fabricated replacement. Language-specific Abyss entries are prioritised in the UI so a known missing alternate is not the default.

## Modern language wrapper

Public route `/dub-player/t/<id>/` contains a JSON CONFIG literal:

```js
var CONFIG = {
  "prefix": "https://player.abyssplayer.com/",
  "ready": {"hin": "EXAMPLE_HINDI_ID", "eng": "EXAMPLE_ENGLISH_ID"},
  "soon": ["tam"]
};
```

These IDs are examples. The parser accepts only the exact approved prefix, well-formed IDs and ready languages. It ignores soon languages and never evaluates script code. Separate ready entries are separate provider players; language changes reload the source. Seamless audio switching and position retention are not guaranteed.

## Older movie variant

An inspected movie used `watchanimeworld.top/api/player1.php?data=...` with a base64 JSON list of language/short-link routes. That wrapper was blank in the test browser. It remains an original provider embed/open-page fallback. The project does not claim this variant works or automatically traverse unverified shorteners.

## Direct media

A provider's video element once exposed a Google Storage URL with a `#mp4/chunk/...` fragment. That was not verified outside the provider's custom player and is deliberately not promoted to a portable stream/download. The direct adapter only considers explicit source `<video>`/`<source>` elements, not hidden provider runtime state. It supports the fixed Google Storage and video-downloads.googleusercontent.com hosts and HEAD video-MIME checks. In the inspected cartoon pages no such independently verified direct file was found.

## Earlier interactive evidence

- Shinchan public series advertised 12 available seasons/612 episodes; actual season options were 1–8 and 12–15. Default season 15 showed 52 episodes. These counts must be fetched again, never hardcoded.
- Shinchan season 15 episode 1 Hindi played in the Abyss provider: advancing video time, 640×360 dimensions, about 21m56s duration, readyState 4. This verifies one interactive sample, not all titles or this backend's deployment.
- Oddballs season 2 episode 1 exposed Hindi and English. Switching to English updated the provider iframe. Full English playback was not verified.
- A movie's older wrapper did not render a usable player in the inspection browser.

## Maintenance

When a source changes, save a minimal sanitized fixture (no credentials or signed stream URLs), update the pure parser and tests, then verify one real interaction. Treat removed files and access challenges as source limitations. Do not disable TLS, evade restrictions or hide failures with demo data. No production fallback data is bundled.

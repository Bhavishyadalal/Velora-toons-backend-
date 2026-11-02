# Security and privacy notes

## Included protections

- No client-supplied fetch URLs. Public content references decode only to fixed source host paths with allowed series/movie/episode patterns.
- Source requests use HTTPS with normal certificate validation, known hosts, redirect validation, public-address DNS prechecks, timeouts, bounded bodies and fetch concurrency.
- Direct-media probes use HEAD only, do not follow redirects, and permit only two reviewed hostnames. No full video body is retrieved.
- Third-party scripts are not evaluated by the parser. CONFIG must decode as a JSON literal with an exact approved provider prefix and safe IDs.
- Frontend renders catalogue text with textContent and validates URLs. HTML fragments from the source are never injected into the UI.
- CORS permits explicit configured frontend origins only. Credentials are omitted. No token is stored in config.js.
- No media proxy, torrent client, open redirect service or arbitrary short-link resolver.
- Vercel headers restrict executable code and frame hosts. No added frontend analytics or external font services.
- Fixed-size cache, rate-limit registry and local collections prevent unbounded ordinary state growth.

## Practical limits

CORS is not authentication; non-browser callers can still use a public API. The in-memory limiter is per process and uses request.client.host, not arbitrary forwarded headers. Behind an unconfigured proxy it may aggregate visitors; configure a trusted proxy carefully or use an edge limiter. Do not trust every forwarded header on a public network.

DNS is checked before a separate HTTP connection; address pinning is not implemented. The hardcoded provider domains reduce exposure, but an internet-facing deployment should also use egress controls and review domain ownership. The optional browser allows source-domain requests and blocks other hosts/resources, yet does not provide HTTP-client-equivalent per-request DNS pinning. Keep it disabled if unnecessary.

Provider iframes are untrusted third-party websites. They are cross-origin, but may contain ads, trackers or popups and can communicate via their own APIs. The iframe intentionally is not given a brittle sandbox that might silently break playback. It has no camera, microphone or geolocation permission. Use Open player when browser privacy or frame policies prevent playback. Velora does not make the provider ad-free or control its code.

Favourites and optional recent history are stored in localStorage on the user's device. Clearing site data removes them. Provider player state is outside Velora's storage. Do not save secrets or signed movie links in local settings, fixtures, logs or Git.

## When adding a provider

Review destination ownership and normal public usage, update backend destination validation and frontend frame-src together, add a minimal parser fixture, verify the actual player, and report limitations. Do not add unrestricted domains, disable TLS, or bypass source access controls merely to turn an error into a success.

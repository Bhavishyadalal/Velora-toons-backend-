# Troubleshooting

| Symptom | Check or action |
| --- | --- |
| Your universe is almost ready | Configure Render URL in Your space or config.js |
| Could not connect | Backend URL, backend status, HTTPS and exact ALLOWED_ORIGINS |
| First request takes a long time | Free service may be sleeping; retry after startup |
| Healthy backend, catalogue fails | Health tests the app, not source reachability; inspect the source error |
| No stories found | Try a simple query and another category; inspect parser against current markup |
| Season missing from selector | Source may not offer it; no fabricated seasons are added |
| Wrong/missing season episodes | Only requested-season results are accepted; optional adapter may be required |
| No Video Found | Provider may have removed the file; try another language/server |
| Black/blank iframe | Provider embedding, region, privacy policy, or codec may prevent it; Open player |
| Provider gets stuck | Select another source or Refresh players; don't assume a URL is permanent |
| Only audio in direct mode | Video codec may be unsupported by your browser; open source in a suitable external player |
| Audio/quality menu absent | These are provider capabilities; Velora only exposes discovered language player sources |
| No Download button | No explicit direct media file passed validation; iframe routes are not downloads |
| Download button plays instead | Cross-origin download behavior is controlled by host headers and browser |
| Seek buffers | Host range support, codec/keyframes and network determine seek behavior |
| Existing URL persists after config change | Settings on this device override config.js; change Your space |
| index.html opened locally does not work | ES modules require HTTP(S); use local server or Vercel |
| Browser image won't build/run | Check supported Playwright version, container dependencies and host memory |

Do not treat a 404, generic timeout, TLS problem, or network-policy denial as proof of bot detection. If a site explicitly requires verification, report that and stop automated attempts; do not add evasion loops.

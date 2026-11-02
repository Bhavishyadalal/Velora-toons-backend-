# Deploy the frontend on Vercel

1. Import the new GitHub repository into Vercel.
2. Set **Root Directory** to `frontend`.
3. Select framework **Other**.
4. Leave build and install commands disabled/empty. There is no bundle to build.
5. Use the root directory itself as the static output; if Vercel asks for Output Directory, enter `.`.
6. Deploy. `frontend/vercel.json` applies security and configuration cache headers.
7. Set the resulting exact origin as Render ALLOWED_ORIGINS.
8. Edit `frontend/config.js`:

```js
window.VELORA_CONFIG = Object.freeze({
  apiBase: 'https://YOUR-RENDER-SERVICE.onrender.com',
  timeoutMs: 45000
});
```

9. Commit/redeploy. `apiBase` is public configuration, not a secret. You can also leave it empty and configure the URL through Your space, but each browser/device then needs setup.

Settings saved in a browser override config.js. If you move the API, update Your space there as well. Preview Vercel deployments have different origins; explicitly add an approved preview origin if testing it. Never use wildcard CORS with credentials.

No external rewrite or video proxy is needed: the frontend talks to the API using CORS, and player traffic goes straight to the provider. Vercel does not host any episode video bytes.

## Phone use

Open the deployed HTTPS site in a recent Chrome, Edge, Brave, Firefox or Safari version. Mobile browsers may require tapping Play inside the player and may choose their own fullscreen video UI. Blocking third-party cookies, tracking protection, or provider frame restrictions can break some sources. Open player is the supported fallback; Velora cannot lift these restrictions.

This is a hosted modular website, not the older offline single-file Velora Pocket player. ES modules need an HTTP(S) origin; simply opening index.html from a file manager is not a supported deployment.

## Security headers

The CSP permits only the observed provider frame hosts and source wrappers. If adding a genuinely new provider, review it, update both backend allowlists and frame-src, add a parser fixture, and test. Do not replace frame-src with a wildcard to hide a broken provider adapter.

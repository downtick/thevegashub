# TheVegasHub.com

Insider Las Vegas travel site — static HTML + Tailwind + Vercel serverless contact function.

## Project layout

```
/                      static HTML site root (deploy target)
├── index.html         homepage
├── hotels/            city pages
├── tours/             Viator + Klook tour widgets
├── things-to-do/      listicles
├── why-vegas/         trip-type guides
├── packing-list/      printable tool
├── about/ contact/
├── api/contact.js     Vercel serverless function (SMTP2GO)
├── css/site.css
├── js/site.js
├── data/hotels.json   source of truth for all hotel listings
├── images/hotels/     drop hotel JPGs here
├── vercel.json        security headers + caching + clean URLs
├── sitemap.xml  robots.txt  llms.txt
└── build.py           regenerates all non-homepage HTML from hotels.json
```

## Required Vercel env vars

Set in the Vercel project dashboard (Settings → Environment Variables):

- `SMTP2GO_API_KEY`    — your SMTP2GO API key
- `CONTACT_TO_EMAIL`   — where contact-form submissions are emailed (e.g. `hello@thevegashub.com`)
- `CONTACT_FROM_EMAIL` — sender address (must be a verified SMTP2GO sender domain, e.g. `no-reply@thevegashub.com`)

## Updating hotels

1. Edit `data/hotels.json` — add hotels or fill in `TODO_ADD_AFFILIATE_LINK` fields.
2. Drop matching images into `images/hotels/` (kebab-case filenames, same as `slug`).
3. Run `python3 build.py`
4. Commit and push — Vercel auto-deploys.

## Local dev

```
npm run dev     # python3 -m http.server 3000
```

## SEO baseline (applied to every page)

- Unique `<title>` + `<meta description>` + `<link canonical>`
- Open Graph + Twitter Card tags
- JSON-LD: `WebSite`, `LocalBusiness` (home), `BreadcrumbList` + `ItemList` (lists)
- `alt` text on every image
- sitemap.xml + robots.txt + llms.txt
- GA4 tracking (G-MYGBD31ZHC)
- Bing Webmaster validation meta tag

## Security baseline

- CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy via `vercel.json`
- No secrets in source — SMTP2GO key lives only in Vercel env vars
- Contact endpoint: POST-only, input sanitization, HTML-entity escaping, honeypot, per-IP rate limit (30s)
- Affiliate links use `rel="nofollow sponsored"` and `target="_blank"`

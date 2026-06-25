# Handoff Notes — TheVegasHub.com

**Date:** 2026-06-06 (last updated)
**Project Type:** Static HTML site (Python-generated) + Vercel serverless
**Repo:** `/Users/downtick/Library/Mobile Documents/com~apple~CloudDocs/Claude Working/websites/TheVegasHub/`
**GitHub:** https://github.com/downtick/thevegashub
**Live Site:** https://thevegashub.com (auto-deploys from `main`)

---

## TL;DR

Static Las Vegas travel site. **Data-driven**: edit `data/hotels.json`, add images to `images/hotels/`, run `python3 build.py` to regenerate all hotel city pages, then commit and push. Vercel auto-deploys. Contact form + newsletter subscribe use Vercel serverless functions.

---

## Project Structure

```
/                          Root (deploy target)
├── index.html             Homepage (has inline newsletter widget)
├── hotels/                City pages (auto-generated via build.py)
├── tours/                 Tour booking widgets
├── things-to-do/          Listicles (pools, shows, buffets, etc.)
├── why-vegas/             Trip-type guides (families, sports, etc.)
├── packing-list/          Printable tool
├── about/ contact/        Static pages
├── travel-insurance/      Travel insurance affiliate page (NEW)
├── newsletter/            Sendy newsletter signup page (NEW)
├── link/                  Link-in-bio page for Instagram (NEW — use for bio URL)
├── api/contact.js         Vercel serverless — contact form (SMTP2GO)
├── api/subscribe.js       Vercel serverless — newsletter (Sendy) (NEW)
├── css/site.css           Shared styles (includes accessibility widget CSS)
├── js/site.js             Shared scripts (includes accessibility widget JS)
├── data/hotels.json       SOURCE OF TRUTH — all hotel data
├── images/hotels/         Hotel photos (kebab-case filenames)
├── build.py               Regenerates hotel city pages + JSON-LD
├── vercel.json            Security headers, caching, clean URLs
├── sitemap.xml            SEO (92 URLs, lastmod 2026-06-06)
├── robots.txt             SEO (clean — legacy WP rules removed)
└── README.md              Technical reference
```

---

## Development Workflow

### Update Hotel Data
1. Edit `data/hotels.json` — add hotels, update affiliate links, fix TODOs
2. Drop matching images into `images/hotels/` using kebab-case slugs (e.g., `aria-resort-las-vegas.jpg`)
3. Run the build script:
   ```bash
   python3 build.py
   ```
4. Commit and push to `main` — Vercel auto-deploys

### Add Blog/Static Content
- Cities: auto-generated from `data/hotels.json`
- Tours, Things to Do, Trip Guides, Packing List: edit `.html` files directly
- All pages get SEO treatment (title, description, OG tags, JSON-LD)

### Test Locally
```bash
npm run dev
# Serves on http://localhost:3000
```

---

## Key Environment Variables (Vercel)

Set in **Vercel Dashboard → Project Settings → Environment Variables**:

| Var | Purpose |
|-----|---------|
| `SMTP2GO_API_KEY` | Contact form email sending |
| `CONTACT_TO_EMAIL` | Where contact form submissions go |
| `CONTACT_FROM_EMAIL` | Sender address (must be verified SMTP2GO domain) |
| `SENDY_API_KEY` | Newsletter subscribe — Sendy API key ⚠️ **MUST BE SET** |
| `SENDY_LIST_ID` | Sendy list ID (currently `10`) ⚠️ **MUST BE SET** |
| `SENDY_URL` | Sendy install URL (`https://clubfluent.com/sendy`) ⚠️ **MUST BE SET** |
| `SENDY_ORIGIN_SECRET` | Secret header value that SiteGround `.htaccess` checks — blocks direct Sendy spam ⚠️ **MUST BE SET** |

> ⚠️ **SENDY vars are not yet set in Vercel** (as of 2026-06-06). Newsletter forms will return 500 until these are added. The API key is NOT stored in the repo — Vercel env vars only.
>
> **To add them:** Vercel Dashboard → TheVegasHub project → Settings → Environment Variables. Add all four vars above. For `SENDY_ORIGIN_SECRET`, use the same value you put in the SiteGround `.htaccess` file.

---

## Affiliate Link System

### Hotel Room Discounters
- All hotel affiliate links use the format: `https://book.hotelroomdiscounters.com/url/[UUID]?isPermanentLink=true`
- **Master spreadsheet:** `/Users/downtick/Library/Mobile Documents/com~apple~CloudDocs/Claude Working/websites/Hotel_Room_Links_Cleaned.xlsx`
  - Sheet: "All Hotels" — 85 rows as of 2026-06-06
  - Rows 83–85: Resorts World (Crockfords) ✅, Circa ✅, Waldorf Astoria ❌ TODO
- Links with `TODO_ADD_AFFILIATE_LINK` in `data/hotels.json` still need real URLs

### How to Get a New Hotel Share Link (from book.hotelroomdiscounters.com)
1. Go to search, enter "Las Vegas", set any dates, click Search
2. Use "Show more results" to load pages until the hotel appears
3. Click **Select** on the hotel card
4. On the hotel detail page, click **Share** (top right)
5. In the popup, click **Copy Hotel Link** (NOT "Copy Deal Link")
6. The link is `https://book.hotelroomdiscounters.com/url/[UUID]?isPermanentLink=true`

### Pages with Affiliate Links
- `things-to-do/strip-hotels-under-200.html` — all 12 hotels linked ✅
- `things-to-do/best-pools-in-las-vegas.html` — 14/15 linked ✅ (Waldorf Astoria TODO)
- All hotel city pages (generated by `build.py` from `data/hotels.json`)

---

## Pages Added in This Session (2026-06-06)

| Page | URL | Notes |
|------|-----|-------|
| Travel Insurance | `/travel-insurance` | Links to Trawick, BuyTripInsurance, IMG Global for international visitors |
| Newsletter Signup | `/newsletter` | Full signup page with Sendy backend |
| Link-in-Bio | `/link` | Instagram bio link — mobile-optimized, noindex |

---

## Accessibility Widget (Site-Wide)

Added to `css/site.css` and `js/site.js` — appears on every page as a floating button (bottom-right, above cookie banner).

**Features:**
- Text size: Default / Large (+20%) / X-Large (+40%)
- Colour mode: Default / High Contrast / Dark+
- Extra letter spacing toggle
- Dyslexia-friendly font toggle (Lexend)
- Preferences saved to `localStorage` key `vh_a11y`

---

## Newsletter (Sendy)

- **Sendy install:** https://clubfluent.com/sendy/
- **List ID:** 10
- **API proxy:** `api/subscribe.js` — never exposes key to browser
- **Signup page:** `/newsletter`
- **Homepage widget:** inline strip above footer in `index.html`
- **GA4 event:** fires `newsletter_signup` with `method: 'newsletter_page'` or `'homepage'`

### Sendy Security — Origin Secret Pattern

The Sendy `/subscribe` endpoint on SiteGround is protected so only the Vercel proxy can reach it:

1. **SiteGround `.htaccess`** (in `/sendy/` folder on clubfluent.com) — blocks all requests that don't include the secret header:
   ```apache
   <Files "subscribe">
     SetEnvIf X-VH-Origin-Secret "your-secret-value" ALLOWED
     Order Deny,Allow
     Deny from all
     Allow from env=ALLOWED
   </Files>
   ```
   ✅ **Verified working** — direct requests to `https://clubfluent.com/sendy/subscribe` return **HTTP 403**.

2. **Vercel proxy** (`api/subscribe.js`) reads `SENDY_ORIGIN_SECRET` from env and adds the `X-VH-Origin-Secret` header on every call to Sendy. Requests from the website go: Browser → Vercel serverless → Sendy (with secret) → response back.

3. **Multi-site note:** If you ever add another site that subscribes to this same Sendy install, it needs the **same** `SENDY_ORIGIN_SECRET` value in its own Vercel env vars. Only `SENDY_LIST_ID` changes per site (to route subscribers to the correct list).

> **To do:** Enable double opt-in — Sendy admin → List #10 → Edit List → Confirmation: On. This adds a confirmation email step and improves deliverability.

---

## Social Media (PromoRepublic)

- **Account:** app.promorepublic.com — logged in as The Vegas Hub (pageId: 344886)
- **Scheduled tweets:** 20 posts scheduled Thu 9AM Pacific, June 4 → October 15, 2026
  - Posts 1–10: Las Vegas vacation themes with emojis, hotel booking CTAs
  - Posts 11–20: Audience-specific (singles, families, newlyweds, couples, bachelor/bachelorette, sports fans, foodies, groups) — no emojis, several include direct hotel links
- **Next tweet slot:** Thu Oct 22, 2026

---

## SEO Status (as of 2026-06-06)

### Fixed This Session
- ✅ 6 truncated meta descriptions fixed (hoover-dam, sphere, bellagio-fountains, high-roller, fremont-street, atomic-golf)
- ✅ Homepage + things-to-do meta descriptions trimmed under 160 chars
- ✅ H1 on things-to-do/index: "VEGAS LISTICLES" → "THINGS TO DO IN LAS VEGAS"
- ✅ sitemap.xml: all lastmod updated to 2026-06-06, travel-insurance + newsletter added
- ✅ robots.txt: legacy WordPress Disallow rules removed
- ✅ FAQ schema (FAQPage JSON-LD) added to best-pools and strip-hotels-under-200
- ✅ 92 pages discovered by Google after sitemap push

### Still Needed
- ⬜ **Submit sitemap to Google Search Console** manually — go to search.google.com/search-console, add property, verify, submit sitemap URL, manually request indexing on top 10 pages
- ⬜ **Build backlinks** — zero external links pointing in; submit to Vegas travel directories
- ⬜ FAQ schema on remaining top pages (hoover-dam, fremont-street, 25-free-things, best-day-trips)
- ⬜ Waldorf Astoria affiliate link (not in HRD inventory — check back later)

---

## Contact Form & Newsletter APIs

### `/api/contact.js`
- `POST /api/contact` — sends via SMTP2GO
- Honeypot, rate limit, input sanitization, HTML escaping

### `/api/subscribe.js`
- `POST /api/subscribe` — proxies to Sendy subscribe endpoint
- Reads `SENDY_API_KEY`, `SENDY_LIST_ID`, `SENDY_URL` from env (never from request)
- Handles: honeypot, 30s rate limit, email validation, "already subscribed" gracefully

---

## Security & SEO Baseline

### Security (via `vercel.json`)
- CSP headers, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy

### SEO
- Unique `<title>` + `<meta description>` + `<link canonical>` on every page
- Open Graph + Twitter Card tags on every page
- JSON-LD: `WebSite`, `LocalBusiness`, `BreadcrumbList`, `ItemList`, `FAQPage` (key pages)
- `alt` text on every hotel image
- sitemap.xml (92 URLs), robots.txt (clean), llms.txt
- GA4 tracking code: `G-MYGBD31ZHC`
- Bing Webmaster validation meta tag present

### Affiliate Links
- Always use `rel="nofollow sponsored noopener"` and `target="_blank"`

---

## Common Tasks

### Add a New Hotel to a City
1. Open `data/hotels.json`, find the city, add to `hotels` array with `affiliateLink`
2. Add image to `images/hotels/[slug].jpg`
3. Run `python3 build.py`
4. Commit and push

### Get a New Affiliate Link
See **Affiliate Link System → How to Get a New Hotel Share Link** above.

### Add a New Content Page
1. Create `things-to-do/[slug].html` following the existing page template
2. Add a `<url>` entry to `sitemap.xml` with today's date
3. Add a card to `things-to-do/index.html`
4. Commit and push

### Fix a Broken/Missing Affiliate Link
1. Search `data/hotels.json` for `TODO_ADD_AFFILIATE_LINK`
2. Get link from Hotel Room Discounters (see workflow above) or the Excel spreadsheet
3. Replace TODO, run `python3 build.py`, commit and push
4. Update the Excel spreadsheet with the new link

---

## Deployment

- Auto-deploys from `main` branch to production (~30–60 seconds)
- `npm run dev` for local testing at http://localhost:3000

---

## More Details

See `README.md` in this directory for full technical reference.

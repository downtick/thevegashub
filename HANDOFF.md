# Handoff Notes — TheVegasHub.com

**Date:** 2026-05-15  
**Project Type:** Static HTML site (Python-generated) + Vercel serverless  
**Repo:** `/Users/downtick/Library/Mobile Documents/com~apple~CloudDocs/Claude Working/websites/TheVegasHub/`  
**GitHub:** https://github.com/downtick/thevegashub  
**Live Site:** https://thevegashub.com (auto-deploys from `main`)

---

## TL;DR

Static Las Vegas travel site. **Data-driven**: edit `data/hotels.json`, add images to `images/hotels/`, run `python3 build.py` to regenerate all HTML pages, then commit and push. Vercel auto-deploys. Contact form uses serverless function.

---

## Project Structure

```
/                      Root (deploy target)
├── index.html         Homepage
├── hotels/            City pages (auto-generated)
├── tours/             Tour booking widgets
├── things-to-do/      Listicles
├── why-vegas/         Trip-type guides
├── packing-list/      Printable tool
├── about/ contact/    Static pages
├── api/contact.js     Vercel serverless function (SMTP2GO mailer)
├── css/site.css       Shared styles
├── js/site.js         Shared scripts
├── data/hotels.json   SOURCE OF TRUTH — all hotel data
├── images/hotels/     Hotel photos (kebab-case filenames)
├── build.py           Regenerates hotel city pages + JSON-LD
├── vercel.json        Security headers, caching, clean URLs
├── sitemap.xml        SEO
├── robots.txt         SEO
└── README.md          Technical reference
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
4. This regenerates all city pages + embedded JSON-LD breadcrumbs + hotel listings
5. Commit and push to `main` — Vercel auto-deploys

### Add Blog/Static Content
- Cities: auto-generated from `data/hotels.json`
- Tours, Things to Do, Trip Guides, Packing List: edit `.html` files directly in those directories
- All pages get SEO treatment (title, description, OG tags, JSON-LD)

### Test Locally
```bash
npm run dev
# Serves on http://localhost:3000
```

---

## Key Environment Variables (Vercel)

Set in **Vercel Dashboard → Project Settings → Environment Variables**:

| Var | Value | Purpose |
|-----|-------|---------|
| `SMTP2GO_API_KEY` | Your SMTP2GO API key | Email sending |
| `CONTACT_TO_EMAIL` | `hello@thevegashub.com` (example) | Where form submissions go |
| `CONTACT_FROM_EMAIL` | `no-reply@thevegashub.com` | Sender (must be verified SMTP2GO domain) |

---

## Contact Form & API

### Endpoint
- `POST /api/contact` (serverless function)
- Built-in:
  - ✅ Input sanitization
  - ✅ HTML-entity escaping
  - ✅ Honeypot spam protection
  - ✅ Per-IP rate limit (30 seconds)
  - ✅ POST-only

### What Happens
1. Form submitted on `/contact` or inline widgets
2. Routed to `/api/contact.js` (Vercel function)
3. Sent via SMTP2GO to `CONTACT_TO_EMAIL`
4. Response redirected or inline thank-you shown

---

## Security & SEO Baseline

### Security (via `vercel.json`)
- CSP headers
- HSTS (strict transport)
- X-Frame-Options (deny clickjacking)
- X-Content-Type-Options (no MIME-sniffing)
- Referrer-Policy
- Permissions-Policy

### SEO
- Unique `<title>` + `<meta description>` + `<link canonical>` on every page
- Open Graph + Twitter Card tags
- JSON-LD: `WebSite`, `LocalBusiness`, `BreadcrumbList`, `ItemList`
- `alt` text on every image
- sitemap.xml, robots.txt, llms.txt
- GA4 tracking (code: `G-MYGBD31ZHC`)
- Bing Webmaster validation

### Affiliate Links
- Use `rel="nofollow sponsored"` and `target="_blank"`
- Prevents passing PageRank, discloses sponsorship

---

## Common Tasks

### Add a New Hotel to a City
1. Open `data/hotels.json`
2. Find the city object, add to the `hotels` array:
   ```json
   {
     "name": "Hotel Name",
     "slug": "hotel-name-las-vegas",
     "address": "123 Main St, Las Vegas, NV",
     "affiliateLink": "https://book.hotelroomdiscounters.com/...",
     "image": "hotel-name-las-vegas.jpg",
     "rating": 4.5,
     "reviews": 2340,
     "note": "Optional discount or feature"
   }
   ```
3. Add image to `images/hotels/hotel-name-las-vegas.jpg`
4. Run `python3 build.py`
5. Commit and push

### Add a New City
1. Add object to `data/hotels.json` with `cityName`, `state`, `slug`, `description`, `heroImage`, `hotels` array
2. Add hero image to `images/hotels/`
3. Run `python3 build.py`
4. Commit and push

### Fix Broken Affiliate Links
1. Search `data/hotels.json` for `TODO_ADD_AFFILIATE_LINK`
2. Get the correct member-rate link
3. Replace the TODO
4. Run `python3 build.py`
5. Commit and push

---

## Deployment

- Auto-deploys from `main` branch to production
- `npm run dev` for local testing
- Build output: all `.html` files in root + subdirectories

---

## More Details

See `README.md` in this directory for full technical reference.

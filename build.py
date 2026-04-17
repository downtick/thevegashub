#!/usr/bin/env python3
"""
TheVegasHub.com static-site generator.

Reads data/hotels.json and renders all non-homepage HTML pages using shared
header/footer + per-page content. Run this any time hotels.json changes:
    python3 build.py
"""
import json, os, re
from pathlib import Path

ROOT = Path(__file__).parent
DATA = json.loads((ROOT / "data/hotels.json").read_text())
HOTELS = [h for h in DATA["hotels"] if h.get("slug") and h["slug"] != "_placeholder"]

GA_ID = "G-MYGBD31ZHC"
BING_CODE = "3EEE76DDDF64D0FF9681E1D1AF528A5D"
SITE = "https://thevegashub.com"

def head(title, desc, path, og_image="og-default.jpg", extra_jsonld=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="msvalidate.01" content="{BING_CODE}">
<link rel="canonical" href="{SITE}{path}">

<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/images/og/{og_image}">
<meta property="og:site_name" content="TheVegasHub">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE}/images/og/{og_image}">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Oswald:wght@500;700&family=Bungee&family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/site.css">
<link rel="icon" type="image/svg+xml" href="/images/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/images/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/images/apple-touch-icon.png">
<meta name="theme-color" content="#0a0010">
{extra_jsonld}
<script>
  // GA4 loader — deferred until cookie consent decision
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  window.__loadGA = function() {{
    const s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id={GA_ID}';
    document.head.appendChild(s);
    gtag('js', new Date());
    gtag('config', '{GA_ID}', {{'anonymize_ip': true}});
  }};
</script>
</head>
<body>
"""

HEADER = """<header class="site-header">
  <div class="container">
    <a href="/" style="text-decoration:none; display:flex; align-items:baseline; gap:10px;">
      <span class="neon-cyan flicker" style="font-family:'Bebas Neue',sans-serif; font-size:26px; letter-spacing:.05em;">VH</span>
      <span class="display" style="color:#fff; font-family:'Bungee',sans-serif; font-size:18px; letter-spacing:.08em;">THE VEGAS HUB</span>
    </a>
    <nav class="site-nav">
      <a href="/hotels">Hotels</a>
      <a href="/tours">Tours</a>
      <a href="/things-to-do">Things to Do</a>
      <a href="/why-vegas">Why Vegas</a>
      <a href="/packing-list">Packing List</a>
      <a href="/about">About</a>
    </nav>
    <button class="menu-toggle" aria-label="Open menu">☰</button>
  </div>
</header>
"""

FOOTER = """<footer class="site-footer">
  <div class="container">
    <div class="grid grid-4" style="gap:32px; margin-bottom:32px;">
      <div>
        <div class="display" style="color:#fff; margin-bottom:12px;">THE VEGAS HUB</div>
        <p style="color:var(--text-muted); font-size:14px;">Insider Las Vegas travel — hotels, tours, and trip tools curated by 30-year locals.</p>
      </div>
      <div>
        <div class="display" style="color:var(--neon-cyan); font-size:13px; margin-bottom:12px;">HOTELS</div>
        <ul style="list-style:none; padding:0; margin:0; font-size:14px; line-height:2;">
          <li><a href="/hotels/las-vegas-strip">Las Vegas Strip</a></li>
          <li><a href="/hotels/downtown-fremont">Downtown Fremont</a></li>
          <li><a href="/hotels/henderson">Henderson</a></li>
          <li><a href="/hotels/mesquite">Mesquite</a></li>
          <li><a href="/hotels/laughlin">Laughlin</a></li>
          <li><a href="/hotels/grand-canyon">Grand Canyon</a></li>
        </ul>
      </div>
      <div>
        <div class="display" style="color:var(--neon-pink); font-size:13px; margin-bottom:12px;">EXPLORE</div>
        <ul style="list-style:none; padding:0; margin:0; font-size:14px; line-height:2;">
          <li><a href="/tours">Tours</a></li>
          <li><a href="/things-to-do">Things to Do</a></li>
          <li><a href="/why-vegas">Why Vegas</a></li>
          <li><a href="/packing-list">Packing List</a></li>
          <li><a href="https://book.hotelroomdiscounters.com/booknow/cars/" rel="nofollow sponsored" target="_blank">Rental Cars</a></li>
        </ul>
      </div>
      <div>
        <div class="display" style="color:var(--neon-yellow); font-size:13px; margin-bottom:12px;">COMPANY</div>
        <ul style="list-style:none; padding:0; margin:0; font-size:14px; line-height:2;">
          <li><a href="/about">About</a></li>
          <li><a href="/contact">Contact</a></li>
          <li><a href="/sitemap.xml">Sitemap</a></li>
          <li><a href="/privacy">Privacy</a></li>
          <li><a href="/terms">Terms</a></li>
          <li><a href="/disclosure">Disclosure</a></li>
        </ul>
      </div>
    </div>
    <div style="border-top:1px solid rgba(191,0,255,.15); padding-top:20px; display:flex; justify-content:space-between; flex-wrap:wrap; gap:16px; font-size:13px; color:var(--text-muted);">
      <div>© <span data-current-year>2026</span> TheVegasHub.com · Headquartered in Las Vegas</div>
      <div>Some links are <a href="/disclosure" style="color:var(--text-muted); text-decoration:underline;">affiliate links</a>. We may earn a commission — at no extra cost to you.</div>
    </div>
  </div>
</footer>

<!-- Cookie consent banner -->
<div id="vh-cookies" style="display:none; position:fixed; bottom:16px; left:16px; right:16px; max-width:620px; margin:0 auto; background:rgba(5,0,12,.96); border:1px solid var(--neon-cyan); border-radius:10px; padding:18px 20px; box-shadow:0 0 24px rgba(0,234,255,.35); z-index:9998; font-size:14px;">
  <div style="display:flex; gap:16px; align-items:flex-start; flex-wrap:wrap;">
    <div style="flex:1; min-width:200px;">
      <div class="display neon-cyan" style="font-size:13px; margin-bottom:6px;">COOKIES &amp; ANALYTICS</div>
      <div style="color:var(--text-muted); line-height:1.55;">We use cookies for analytics and affiliate attribution. Essential cookies are always on. <a href="/privacy" style="color:var(--neon-cyan);">Privacy Policy</a>.</div>
    </div>
    <div style="display:flex; gap:8px; flex-wrap:wrap;">
      <button onclick="VegasHub.cookies('reject')" class="btn btn-ghost" style="font-size:12px; padding:10px 14px;">Essential only</button>
      <button onclick="VegasHub.cookies('accept')" class="btn btn-cyan" style="font-size:12px; padding:10px 14px;">Accept all</button>
    </div>
  </div>
</div>

<script src="/js/site.js"></script>
</body>
</html>
"""

def hotel_card(h):
    link = h.get("link", "#")
    is_todo = (not link) or link.startswith("TODO")
    slug = h['slug']
    # Card links to hotel page; separate BOOK button goes direct to affiliate link
    page_href = f"/hotels/{slug}"
    book_href = link if not is_todo else "/contact"
    book_label = "COMING SOON" if is_todo else "BOOK NOW"
    book_rel = 'rel="nofollow sponsored" target="_blank"' if not is_todo else ""
    pill = '<span class="pill">COMING SOON</span>' if is_todo else '<span class="pill pill-pink">HOT DEAL</span>'
    img = h.get("image","/images/og/og-default.jpg")
    alt = h["alt"]
    note = h.get("note","")
    city = h.get("city","")
    tags_attr = " ".join(h.get("tags", []) or [])
    return f"""      <div class="card" id="{slug}" data-tags="{tags_attr}">
        <a href="{page_href}" style="text-decoration:none; color:inherit;">
          <img class="card-img" src="{img}" alt="{alt}" loading="lazy" onerror="this.src='/images/og/og-default.jpg'">
          <div class="card-body" style="padding-bottom:12px;">
            {pill}
            <h3 class="headline" style="font-size:26px; margin:10px 0 4px;">{h['name']}</h3>
            <p style="color:var(--text-muted); font-size:13px; margin:0 0 12px;">{city}</p>
            <p class="card-spacer" style="margin:0 0 12px;">{note}</p>
            <span class="display neon-cyan" style="font-size:12px; margin-top:auto;">Read full guide →</span>
          </div>
        </a>
        <div style="padding:0 20px 20px; margin-top:auto;">
          <a href="{book_href}" {book_rel} class="btn btn-pink" style="width:100%; text-align:center; font-size:13px; padding:12px;">{book_label}</a>
        </div>
      </div>
"""

def write(rel_path, html):
    out = ROOT / rel_path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(f"  wrote {rel_path}")

# ---------------------------- PER-HOTEL PAGES ---------------------------- #

# Tag-driven insider tips. Every hotel gets the first two plus any tag-matched ones.
TAG_TIPS = {
    "strip":        "Ask for a room above the 20th floor — the Strip view is worth the upgrade.",
    "north-strip":  "North-Strip hotels are walkable to Resorts World, Wynn Plaza, and Fashion Show Mall.",
    "mid-strip":    "Mid-Strip = the shortest walk to Sphere, Bellagio fountains, and the monorail stations.",
    "south-strip":  "South-Strip puts you minutes from Allegiant Stadium (Raiders) and T-Mobile Arena.",
    "off-strip":    "Off-Strip properties usually have free self-parking — don't valet unless you want a 45-minute wait at 2am.",
    "downtown":     "Under the Fremont Street canopy, the neon light show runs every hour after dark. Free.",
    "fremont":      "Walk the Fremont Street Experience at night. Free shows, cheaper drinks than the Strip.",
    "luxury":       "Request a room on a renewed floor — even luxury towers have varying renovation tiers.",
    "suites":       "All-suite properties mean bigger bathrooms and separate living areas — worth it for a 3+ night stay.",
    "non-gaming":   "Non-gaming hotels are dramatically quieter — ideal if casino smoke isn't your thing.",
    "pool":         "Book a cabana at least 2 weeks out for weekend dates — they sell out.",
    "family":       "Ask at check-in for pool towels, pool-bag, and any kids' menu — they often don't volunteer it.",
    "sportsbook":   "The sportsbook lounges at most hotels are open to non-guests. Grab a seat early on game day.",
    "classic":      "Classic hotels mean classic footprints — request a renovated 'Go' or 'Deluxe' room, not a base-tier.",
    "summerlin":    "Summerlin is a 20-minute drive from the Strip — plan on Uber/Lyft both ways.",
    "henderson":    "Henderson hotels sit above the valley with Strip skyline views. Best sunsets.",
    "mesquite":     "Mesquite is a 90-minute drive north of Vegas on I-15. Perfect Nevada golf-and-spa weekend.",
    "laughlin":     "Laughlin's Colorado River beaches are the town's real draw. Rent a jet ski by the hour.",
    "grand-canyon": "Booking the Grand Canyon? Buy the America the Beautiful Pass ($80/year) if you plan to hit 3+ national parks.",
    "route-66":     "Historic Route 66 runs right through town — worth a slow drive at sunset.",
    "new":          "Brand-new = smallest signs of wear, but also potentially untested ops. Check very recent reviews.",
    "fountains":    "Ask for a fountain-view room and set an alarm for the 9pm show. Worth waking up for.",
    "sphere-views": "For Sphere views, request a high north-facing room — Venetian, Palazzo, Wynn, and Encore face right at it.",
    "train":        "The train departure from Williams is at 9:30am — stay the night before if you're making the morning trip.",
    "river":        "Book a river-view room — the price bump is usually minimal and the view is the whole point of coming here.",
    "value":        "Budget properties rarely include resort fees in the base price — check the total before you book.",
    "sphere-view":  "Request north-facing high floors — these rooms look directly at Sphere.",
}

GENERIC_TIPS = [
    "Member rates (what you get through our link) typically save 10-25% vs the public rate advertised on the hotel's own site.",
    "Book through our link before your trip; don't wait until you're checking in — the rate can change.",
    "Las Vegas rooms are nearly always cheapest mid-week (Sun-Thu). Weekends add 40-100%.",
]

def hotel_tips(h):
    tags = h.get("tags", []) or []
    tips = []
    # Add tag-matched tips first
    seen = set()
    for t in tags:
        if t in TAG_TIPS and TAG_TIPS[t] not in seen:
            tips.append(TAG_TIPS[t])
            seen.add(TAG_TIPS[t])
    # Always include 2 generic tips
    for g in GENERIC_TIPS[:2]:
        if g not in seen:
            tips.append(g)
    return tips[:6]

def hotel_related(h, all_hotels, max_count=3):
    """Return up to N related hotels: same area if possible, same city as fallback."""
    same_area = [x for x in all_hotels if x != h and x.get("area") == h.get("area") and not x.get("link", "").startswith("TODO")]
    same_city = [x for x in all_hotels if x != h and x.get("city") == h.get("city") and x not in same_area and not x.get("link", "").startswith("TODO")]
    out = (same_area + same_city)[:max_count]
    return out

def city_slug_for(h):
    """Map a hotel's city+area to the matching city page slug."""
    city = h.get("city","")
    area = h.get("area","")
    if area == "downtown": return "downtown-fremont"
    if city == "Henderson": return "henderson"
    if city == "Mesquite": return "mesquite"
    if city == "Laughlin": return "laughlin"
    if area == "grand-canyon": return "grand-canyon"
    return "las-vegas-strip"

def page_hotel(h, all_hotels):
    slug = h["slug"]
    name = h["name"]
    link = h.get("link", "")
    is_todo = (not link) or link.startswith("TODO")
    book_rel = 'rel="nofollow sponsored" target="_blank"' if not is_todo else ""
    book_href = link if not is_todo else "/contact"
    book_label = "COMING SOON" if is_todo else "BOOK YOUR ROOM →"
    img = h.get("image", "/images/og/og-default.jpg")
    alt = h["alt"]
    note = h.get("note", "")
    city = h.get("city", "")
    area = h.get("area", "")
    tags = h.get("tags", []) or []
    tips = hotel_tips(h)
    related = hotel_related(h, all_hotels)
    city_slug = city_slug_for(h)
    city_label = {"downtown-fremont":"Downtown Fremont","henderson":"Henderson","mesquite":"Mesquite","laughlin":"Laughlin","grand-canyon":"Grand Canyon Area","las-vegas-strip":"Las Vegas"}.get(city_slug, city)

    # Meta description — 155 chars max
    meta_desc = (note[:140] + "…") if len(note) > 140 else note
    if not meta_desc:
        meta_desc = f"{name} in {city} — member rates, insider tips, and instant booking through TheVegasHub."

    # JSON-LD Hotel schema
    hotel_jsonld = f"""<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"Hotel",
  "name":{json.dumps(name)},
  "url":"{SITE}/hotels/{slug}",
  "image":"{SITE}{img}",
  "description":{json.dumps(note)},
  "address":{{"@type":"PostalAddress","addressLocality":{json.dumps(city)},"addressRegion":"NV" if "{city}" in ["Las Vegas","Henderson","Mesquite","Laughlin"] else "AZ","addressCountry":"US"}}
}}
</script>""".replace('"NV" if "{city}" in ["Las Vegas","Henderson","Mesquite","Laughlin"] else "AZ"',
                      '"NV"' if city in ["Las Vegas","Henderson","Mesquite","Laughlin"] else '"AZ"')

    breadcrumb_jsonld = f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}},
  {{"@type":"ListItem","position":2,"name":"Hotels","item":"{SITE}/hotels"}},
  {{"@type":"ListItem","position":3,"name":{json.dumps(city_label)},"item":"{SITE}/hotels/{city_slug}"}},
  {{"@type":"ListItem","position":4,"name":{json.dumps(name)},"item":"{SITE}/hotels/{slug}"}}
]}}
</script>"""

    # Tags as pills
    tag_pills = "".join(f'<span class="pill" style="margin-right:6px;">{t.replace("-"," ").upper()}</span>' for t in tags[:5])

    # Tips HTML
    tips_html = "".join(f"""        <li style="padding:14px 0; border-bottom:1px solid rgba(191,0,255,.15); display:flex; gap:14px; align-items:flex-start;">
          <span class="display neon-cyan" style="font-size:22px; min-width:30px;">{i+1:02d}</span>
          <span style="line-height:1.65;">{tip}</span>
        </li>\n""" for i, tip in enumerate(tips))

    # Related hotels
    related_html = "".join(f"""        <a class="card" href="/hotels/{r['slug']}" style="text-decoration:none;">
          <img class="card-img" src="{r.get('image','')}" alt="{r['alt']}" loading="lazy" onerror="this.src='/images/og/og-default.jpg'">
          <div class="card-body" style="padding:18px;">
            <h3 class="headline" style="font-size:20px; margin:0 0 4px;">{r['name']}</h3>
            <p style="color:var(--text-muted); font-size:13px; margin:0;">{r.get('city','')}</p>
          </div>
        </a>\n""" for r in related)

    html = head(
        f"{name} — Member Rates & Insider Tips | TheVegasHub",
        meta_desc,
        f"/hotels/{slug}",
        og_image=img.lstrip("/"),
        extra_jsonld=hotel_jsonld + "\n" + breadcrumb_jsonld,
    ) + HEADER + f"""
<!-- HERO -->
<section class="hero" style="padding:72px 0 48px; background:linear-gradient(180deg, rgba(10,0,20,.45) 0%, rgba(10,0,20,.85) 100%), url('{img}') center/cover;">
  <div class="container">
    <div style="font-size:13px; letter-spacing:.1em; color:var(--text-muted); margin-bottom:12px;">
      <a href="/hotels" style="color:var(--text-muted);">Hotels</a>
      <span style="margin:0 8px;">›</span>
      <a href="/hotels/{city_slug}" style="color:var(--text-muted);">{city_label}</a>
    </div>
    <div style="margin-bottom:14px;">{tag_pills}</div>
    <h1 class="headline-glow" style="font-size:clamp(40px,7vw,84px); line-height:1.05; margin:0 0 16px;">{name}</h1>
    <p class="sub" style="max-width:700px; margin:0 0 28px;">{note}</p>
    <a class="btn btn-cyan" href="{book_href}" {book_rel} style="font-size:16px; padding:16px 36px;">{book_label}</a>
  </div>
</section>

<!-- MAIN CONTENT -->
<section class="section" style="padding-top:48px;">
  <div class="container" style="display:grid; grid-template-columns:1fr 320px; gap:48px; max-width:1100px;">
    <!-- EDITORIAL -->
    <div>
      <h2 class="headline neon-cyan" style="font-size:32px; margin-top:0;">Why we like it</h2>
      <p style="font-size:17px; line-height:1.8;">{note}</p>
      <p style="font-size:17px; line-height:1.8;">{name} sits in {city_label} — one of the six Vegas-region destinations we cover on TheVegasHub. Our team has stayed at the property enough times to know what's worth asking for at check-in, which rooms to request, and when rates are at their best. If you're booking through our link, you'll see the member rate — typically 10-25% below what the hotel quotes on its own site or on Booking.com.</p>

      <h2 class="headline neon-pink" style="font-size:32px; margin-top:40px;">Insider tips</h2>
      <ul style="list-style:none; padding:0; margin:0; font-size:16px;">
{tips_html}      </ul>

      <!-- Second CTA -->
      <div style="background:rgba(191,0,255,.06); border:1px solid var(--neon-cyan); border-radius:10px; padding:28px; margin:40px 0; text-align:center;">
        <div class="display neon-cyan" style="font-size:14px; margin-bottom:10px;">READY TO BOOK?</div>
        <h3 class="headline" style="font-size:26px; margin:0 0 14px;">Member rates at {name}</h3>
        <p style="margin:0 0 20px; color:var(--text-muted);">Rates from our booking partner — lower than the hotel's public rate. Free to check.</p>
        <a class="btn btn-cyan" href="{book_href}" {book_rel} style="font-size:15px; padding:14px 32px;">{book_label}</a>
      </div>
    </div>

    <!-- SIDEBAR -->
    <aside>
      <div class="card" style="padding:24px; position:sticky; top:100px;">
        <div class="display neon-cyan" style="font-size:12px; margin-bottom:14px;">QUICK FACTS</div>
        <dl style="margin:0; font-size:14px;">
          <dt style="color:var(--text-muted); font-size:11px; letter-spacing:.1em; text-transform:uppercase; margin-top:12px;">Location</dt>
          <dd style="margin:4px 0 0; font-size:15px;">{city}, {("NV" if city in ["Las Vegas","Henderson","Mesquite","Laughlin"] else "AZ")}</dd>

          <dt style="color:var(--text-muted); font-size:11px; letter-spacing:.1em; text-transform:uppercase; margin-top:16px;">Area</dt>
          <dd style="margin:4px 0 0; font-size:15px;">{area.replace("-"," ").title() if area else "—"}</dd>

          <dt style="color:var(--text-muted); font-size:11px; letter-spacing:.1em; text-transform:uppercase; margin-top:16px;">Vibe</dt>
          <dd style="margin:4px 0 0; font-size:14px; line-height:1.6;">{", ".join(t.replace("-"," ").title() for t in tags[:4]) if tags else "—"}</dd>
        </dl>
        <div style="margin-top:24px;">
          <a class="btn btn-pink" href="{book_href}" {book_rel} style="width:100%; text-align:center; padding:14px; font-size:13px;">{book_label}</a>
        </div>
      </div>
    </aside>
  </div>
</section>
""" + (f"""
<!-- RELATED HOTELS -->
<section class="section section-dark">
  <div class="container">
    <div class="section-head">
      <h2 class="headline neon-yellow" style="font-size:clamp(28px,4vw,40px);">You might also like</h2>
      <p class="kicker">Other {city_label} hotels we recommend.</p>
    </div>
    <div class="grid grid-3">
{related_html}    </div>
  </div>
</section>
""" if related else "") + """
<style>
  @media (max-width:800px) {
    section.section .container[style*="grid-template-columns:1fr 320px"] { grid-template-columns: 1fr !important; }
    aside .card { position:static !important; }
  }
</style>
""" + FOOTER

    write(f"hotels/{slug}.html", html)

# ---------------------------- CITY PAGES ---------------------------- #

CITY_PAGES = [
    ("las-vegas-strip",   "Las Vegas Strip Hotels — Member Rates | TheVegasHub",
     "Hand-picked Las Vegas Strip hotels with member-rate savings — Venetian, Wynn, Bellagio, Aria, Caesars, and every icon in between.",
     "Las Vegas Strip",
     lambda h: h["city"]=="Las Vegas" and h["area"] in ("strip","off-strip","summerlin","southwest","north","south")),
    ("downtown-fremont",  "Downtown Fremont Hotels in Las Vegas — Member Rates | TheVegasHub",
     "Downtown Las Vegas hotels on Fremont Street — cheaper rooms, classic Vegas neon, better cocktails. Member-rate links inside.",
     "Downtown Fremont",
     lambda h: h["area"]=="downtown"),
    ("henderson",         "Henderson, NV Hotels — Green Valley Ranch, M Resort | TheVegasHub",
     "Henderson, Nevada hotels — Green Valley Ranch, M Resort, and the hilltop resorts locals actually recommend to their in-laws.",
     "Henderson, NV",
     lambda h: h["city"]=="Henderson"),
    ("mesquite",          "Mesquite, NV Hotels — Golf, Spa & Casino | TheVegasHub",
     "Mesquite, Nevada hotels — CasaBlanca, Eureka, Virgin River. Quiet, cheaper, and 90 minutes north of the Strip.",
     "Mesquite, NV",
     lambda h: h["city"]=="Mesquite"),
    ("laughlin",          "Laughlin, NV Hotels on the Colorado River | TheVegasHub",
     "Laughlin, Nevada hotels on the Colorado River — Edgewater, Aquarius, Harrah's, Tropicana. Member-rate booking links inside.",
     "Laughlin, NV",
     lambda h: h["city"]=="Laughlin"),
    ("grand-canyon",      "Hotels Near the Grand Canyon South Rim | TheVegasHub",
     "Hotels near the Grand Canyon South Rim — Tusayan, Williams, Kingman. Gateway lodges for day trips from Las Vegas.",
     "Grand Canyon Area",
     lambda h: h["area"]=="grand-canyon"),
]

CITY_INTROS = {
    "las-vegas-strip": {
        "tagline": "The four-mile corridor that defines Las Vegas.",
        "intro": [
            "The Strip is what everyone means when they say 'Vegas.' Four miles of neon, fountains, and megaresorts running from Mandalay Bay in the south to the Stratosphere in the north, with the Sphere now anchoring the east side of the mid-Strip.",
            "Our Strip picks are weighted toward three things that actually matter for a weekend: room quality (who renovated recently), walkability (how far is your show), and pools (the real differentiator from April through October). Member rates save 10-25% off the public rate at most properties.",
        ],
        "what_to_do": [
            ("Bellagio Fountains", "Every 30 minutes from 3pm, every 15 after 8pm. Best view: bridge at Caesars."),
            ("The Sphere", "Book tickets before you book your hotel — it's the closest walk from Venetian/Palazzo."),
            ("Walk the Strip at night", "Start at Bellagio, go north, drink somewhere you can see the fountains."),
        ],
    },
    "downtown-fremont": {
        "tagline": "Old Vegas — neon, cocktails, and cheaper rooms 10 minutes from the Strip.",
        "intro": [
            "Downtown Fremont is the Vegas your grandparents came to — classic casinos, the covered neon canopy of the Fremont Street Experience, and some of the best cocktail bars in the city. Rooms run 30-50% cheaper than the Strip for the same category, and the walk between properties is measured in minutes, not miles.",
            "We recommend Downtown as a first night or last night on a Vegas trip — it's a totally different flavor from the Strip, and you can Uber back for $15.",
        ],
        "what_to_do": [
            ("Fremont Street Experience", "The neon canopy runs shows every hour after dark — free."),
            ("Container Park", "Shops, kids' park, giant fire-breathing praying mantis. Worth 30 minutes."),
            ("Carson Kitchen / Downtown Cocktail Room", "Best food + drinks in Vegas for under $50/head."),
        ],
    },
    "henderson": {
        "tagline": "Hilltop resorts, Strip views, locals' favorite pools.",
        "intro": [
            "Henderson is the wealthy suburb southeast of Vegas proper — think Summerlin with better Strip skyline views. Two hilltop resorts (Green Valley Ranch and M Resort) sit above the valley with west-facing patios that frame the Strip at sunset.",
            "If you're here for a bachelor party, Raiders game, or Strip nightlife, stay on the Strip. If you're here with family, a group of friends who don't want casino smoke, or anyone over 40 who wants quiet — Henderson's the move.",
        ],
        "what_to_do": [
            ("Green Valley Ranch pool", "Best pool deck in Henderson. Day passes available."),
            ("Lake Las Vegas", "20 minutes from the Strip. Rent a kayak, lunch at MonteLago Village."),
            ("Ethel M Chocolate Factory", "Free tour, free samples, free cactus garden. 15 minutes from Henderson hotels."),
        ],
    },
    "mesquite": {
        "tagline": "Golf, spa, river-country weekends — 90 minutes north of Vegas.",
        "intro": [
            "Mesquite is Nevada's best-kept golf secret. A 90-minute drive north of Vegas on I-15, right at the Arizona border, it has four full casino-resorts, a half-dozen of the best-rated golf courses in the Southwest, and rooms that run 60-70% cheaper than the Strip.",
            "We send couples and small groups here for quieter weekends — the vibe is Palm Springs circa 1985 with a casino floor attached. Zion National Park is a 75-minute drive east. St. George, Utah is 30 minutes away.",
            "All 4 Mesquite properties below have their own dedicated pages — click through for full reviews, insider tips on room requests, and member-rate booking.",
        ],
        "what_to_do": [
            ("Play Wolf Creek Golf Club", "Nevada's most photographed public course. Red-rock canyon views on every hole."),
            ("CasaBlanca Spa", "Old-school full-service spa — cheaper than the Strip by 40-60%."),
            ("Day trip to Zion", "75-minute drive east through the Virgin River Gorge. Stunning."),
            ("Valley of Fire State Park", "45 minutes south. Red-rock desert with petroglyphs — underrated over the Grand Canyon for a quick trip."),
            ("Dinner at Jagers Mesquite Grill", "The town's best steak, a block from the CasaBlanca."),
        ],
    },
    "laughlin": {
        "tagline": "The Colorado River's own casino town — beaches, buffets, boats.",
        "intro": [
            "Laughlin is Vegas's little sibling 90 minutes south on the Colorado River, where the neon hotels run along a riverfront with actual sand beaches, paddleboats, and jet skis. Rooms routinely hit $50/night midweek.",
            "It's not trying to be the Strip — it's warmer, it's older, it's cheaper, and the locals still know the blackjack dealers' names. Come for a weekend, not a week.",
        ],
        "what_to_do": [
            ("Colorado River jet ski rental", "From any hotel beach. By the hour."),
            ("Riverwalk", "Walk between the 9 casinos along the river — they're all connected by path."),
            ("Oatman, AZ day trip", "45-minute drive. Ghost-town, wild burros, photogenic as hell."),
        ],
    },
    "grand-canyon": {
        "tagline": "Gateway hotels for the South Rim, West Rim, and Route 66.",
        "intro": [
            "The Grand Canyon South Rim is 4.5 hours from Vegas by car. To hit it right, most visitors sleep the night before in Williams or Tusayan, do the Rim in the morning, and drive back to Vegas or continue to Sedona.",
            "Our Grand Canyon picks include the Grand Hotel at the Grand Canyon (closest to the South Rim entrance) and the Grand Canyon Railway Hotel (if you want to take the train in). Williams and Kingman are classic Route 66 stops worth the stay.",
        ],
        "what_to_do": [
            ("Drive the South Rim scenic drive", "Hermit Road + Desert View Drive. Park at pullouts, walk 50 feet, be stunned."),
            ("Take the Grand Canyon Railway", "2h 15min each way from Williams. Old-school."),
            ("Historic Route 66 Williams", "Walk Railroad Avenue after dark. Neon signs, diners, BBQ."),
        ],
    },
}

FILTER_LABELS = {
    "luxury":       "Luxury",
    "suites":       "All-Suite",
    "pool":         "Pool",
    "non-gaming":   "Non-Gaming",
    "value":        "Value",
    "family":       "Family",
    "sphere-views": "Sphere View",
    "sphere-view":  "Sphere View",
    "mid-strip":    "Mid-Strip",
    "north-strip":  "North Strip",
    "south-strip":  "South Strip",
    "off-strip":    "Off-Strip",
    "classic":      "Classic",
    "new":          "Newly Opened",
    "fremont":      "Fremont",
    "downtown":     "Downtown",
    "summerlin":    "Summerlin",
    "sportsbook":   "Sportsbook",
    "river":        "Riverfront",
    "beach":        "Beach",
    "golf":         "Golf",
    "route-66":     "Route 66",
    "train":        "Train",
}

def filter_bar_html(matches):
    """Build a filter chip bar based on tags present across the matching hotels."""
    tag_counts = {}
    for h in matches:
        for t in (h.get("tags", []) or []):
            tag_counts[t] = tag_counts.get(t, 0) + 1
    # Keep tags with >=2 matches, sorted by count desc
    chosen = sorted([t for t, c in tag_counts.items() if c >= 2 and t in FILTER_LABELS],
                    key=lambda t: (-tag_counts[t], t))[:10]
    if not chosen:
        return ""
    chips = "".join(f'<button class="filter-chip" data-tag="{t}">{FILTER_LABELS[t]}</button>' for t in chosen)
    return f"""
    <div class="filter-bar" id="hotel-filter-bar">
      <span class="filter-bar-label">FILTER:</span>
      <button class="filter-chip active" data-tag="_all">All ({len(matches)})</button>
      {chips}
      <span class="filter-count" id="hotel-filter-count"></span>
    </div>"""

FILTER_JS = """<script>
(function(){
  const bar = document.getElementById('hotel-filter-bar');
  if (!bar) return;
  const grid = document.querySelector('#hotels-grid');
  const cards = grid ? [...grid.querySelectorAll('.card')] : [];
  const counter = document.getElementById('hotel-filter-count');
  function apply(tag) {
    [...bar.querySelectorAll('.filter-chip')].forEach(c => c.classList.toggle('active', c.dataset.tag === tag));
    let shown = 0;
    cards.forEach(card => {
      const tags = (card.dataset.tags || '').split(/\\s+/);
      const match = tag === '_all' || tags.includes(tag);
      card.dataset.hidden = match ? '0' : '1';
      if (match) shown++;
    });
    if (counter) counter.textContent = tag === '_all' ? '' : shown + ' match' + (shown === 1 ? '' : 'es');
    // Preserve in URL hash so filter is shareable
    if (tag !== '_all') location.hash = 'filter=' + tag;
    else history.replaceState(null, '', location.pathname);
  }
  bar.addEventListener('click', e => {
    const chip = e.target.closest('.filter-chip');
    if (chip) apply(chip.dataset.tag);
  });
  // Honor initial hash
  const m = (location.hash.match(/filter=([\\w-]+)/) || [])[1];
  if (m) apply(m);
})();
</script>"""

def page_city(slug, title, desc, heading, filt):
    matches = [h for h in HOTELS if filt(h)]
    cards = "".join(hotel_card(h) for h in matches) or "<p>Hotels coming soon.</p>"
    filter_html = filter_bar_html(matches)
    intro_data = CITY_INTROS.get(slug, {})
    tagline = intro_data.get("tagline", "")
    intros = intro_data.get("intro", [])
    what_to_do = intro_data.get("what_to_do", [])

    intro_html = ""
    if intros:
        paras = "".join(f'<p style="font-size:17px; line-height:1.8; margin:0 0 16px;">{p}</p>' for p in intros)
        intro_html = f"""
    <div class="card" style="padding:36px; margin-bottom:48px; max-width:860px;">
      <div class="display neon-cyan" style="font-size:13px; margin-bottom:12px;">ABOUT {heading.upper()}</div>
      <p style="font-size:19px; font-style:italic; margin:0 0 20px; color:#fff;">{tagline}</p>
      {paras}
    </div>"""

    wtd_html = ""
    if what_to_do:
        items = "".join(f"""      <div class="card" style="padding:20px;">
        <h3 class="headline neon-pink" style="font-size:18px; margin:0 0 8px;">{t}</h3>
        <p style="margin:0; font-size:14px;">{d}</p>
      </div>
""" for t, d in what_to_do)
        wtd_html = f"""
    <div style="margin-top:56px; margin-bottom:48px;">
      <h2 class="headline neon-yellow" style="font-size:clamp(28px,4vw,40px); margin:0 0 8px;">What to do in {heading}</h2>
      <p style="color:var(--text-muted); margin:0 0 24px;">Our editorial picks for how to spend a day.</p>
      <div class="grid grid-3">
{items}      </div>
    </div>"""

    jsonld = f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}},
  {{"@type":"ListItem","position":2,"name":"Hotels","item":"{SITE}/hotels"}},
  {{"@type":"ListItem","position":3,"name":"{heading}","item":"{SITE}/hotels/{slug}"}}
]}}
</script>"""
    html = head(title, desc, f"/hotels/{slug}", extra_jsonld=jsonld) + HEADER + f"""
<section class="section">
  <div class="container">
    <div class="section-head">
      <span class="pill pill-cyan">{heading.upper()}</span>
      <h1 class="headline-glow" style="font-size:clamp(44px,7vw,80px); margin:12px 0 8px;">HOTELS IN<br>{heading.upper()}</h1>
      <p class="kicker">{desc}</p>
    </div>
{intro_html}
    <div style="margin-top:{"0" if intros else "0"};">
      <h2 class="headline neon-cyan" style="font-size:clamp(28px,4vw,40px); margin:0 0 8px;">Our picks</h2>
      <p style="color:var(--text-muted); margin:0 0 24px;">Every hotel below has a dedicated page with insider tips — or jump straight to booking with the pink button.</p>
      {filter_html}
      <div class="grid grid-3" id="hotels-grid">
{cards}    </div>
    </div>
{wtd_html}
  </div>
</section>
""" + FILTER_JS + FOOTER
    write(f"hotels/{slug}.html", html)

# ---------------------------- /hotels/ INDEX ---------------------------- #

def page_hotels_index():
    cities = [
        ("Las Vegas Strip","/hotels/las-vegas-strip","Resorts, Sphere views, every casino icon.", "neon-cyan"),
        ("Downtown Fremont","/hotels/downtown-fremont","Old-Vegas neon, cheaper rooms, better cocktails.", "neon-pink"),
        ("Henderson","/hotels/henderson","Green Valley Ranch, M Resort — locals' picks.", "neon-yellow"),
        ("Mesquite","/hotels/mesquite","Golf, spa, quieter river-country weekend.", "neon-cyan"),
        ("Laughlin","/hotels/laughlin","Colorado River beaches and $20 buffets.", "neon-pink"),
        ("Grand Canyon","/hotels/grand-canyon","South Rim lodges, Williams train base.", "neon-yellow"),
    ]
    tiles = "".join(f"""      <a class="card" href="{href}" style="padding:32px; text-align:center; text-decoration:none;">
        <h3 class="display {cls}" style="font-size:24px; margin:0 0 8px;">{name.upper()}</h3>
        <p style="margin:0; color:var(--text-muted);">{blurb}</p>
      </a>
""" for name,href,blurb,cls in cities)
    html = head(
        "All Las Vegas & Grand Canyon Hotels | TheVegasHub",
        "Curated Las Vegas hotels across the Strip, Downtown Fremont, Henderson, Mesquite, Laughlin, and the Grand Canyon — with member-rate booking links.",
        "/hotels",
    ) + HEADER + f"""
<section class="section">
  <div class="container">
    <div class="section-head">
      <span class="pill pill-cyan">HOTELS</span>
      <h1 class="headline-glow" style="font-size:clamp(44px,7vw,80px); margin:12px 0 8px;">FIND YOUR HOTEL</h1>
      <p class="kicker">Pick a city — we've stayed in almost all of these ourselves.</p>
    </div>
    <div class="grid grid-3">
{tiles}    </div>
  </div>
</section>
""" + FOOTER
    write("hotels/index.html", html)

# ---------------------------- /tours/ ---------------------------- #

def page_tours():
    html = head(
        "Las Vegas Tours — Grand Canyon, Hoover Dam, Helicopters | TheVegasHub",
        "Hand-picked Las Vegas tours and day trips — Grand Canyon helicopters, Hoover Dam, Red Rock Canyon, Sphere, and more — with real-time pricing and instant booking.",
        "/tours",
    ) + HEADER + """
<section class="section">
  <div class="container">
    <div class="section-head">
      <span class="pill pill-pink">TOURS & DAY TRIPS</span>
      <h1 class="headline-glow" style="font-size:clamp(44px,7vw,80px); margin:12px 0 8px;">VEGAS TOURS</h1>
      <p class="kicker">The best day trips from Las Vegas — hand-picked by locals, with live pricing and instant booking.</p>
    </div>

    <h2 class="headline neon-cyan" style="margin-top:32px;">TOP PICKS RIGHT NOW</h2>
    <p style="color:var(--text-muted); margin-bottom:24px;">Live pricing below — refreshed whenever this page loads.</p>

    <div style="background:rgba(255,255,255,.03); border:1px solid rgba(191,0,255,.2); border-radius:10px; padding:20px; margin-bottom:32px;">
      <div data-vi-partner-id="U00009631" data-vi-widget-ref="W-e608db0e-5519-4eb8-a37f-01bb80769f0a"></div>
      <script async src="https://www.viator.com/orion/partner/widget.js"></script>
    </div>

    <h2 class="headline neon-pink" style="margin-top:40px;">MORE VEGAS EXPERIENCES</h2>
    <p style="color:var(--text-muted); margin-bottom:24px;">Additional day trips, tickets, and tours — instant booking.</p>

    <div style="background:rgba(255,255,255,.03); border:1px solid rgba(255,46,176,.2); border-radius:10px; padding:20px; margin-bottom:32px;">
      <ins class="klk-aff-widget"
           data-adid="1258235"
           data-lang=""
           data-currency=""
           data-cardH="126"
           data-padding="92"
           data-lgH="470"
           data-edgeValue="655"
           data-cid="136"
           data-tid="-1"
           data-amount="6"
           data-prod="dynamic_widget">
        <a href="//www.klook.com/" style="color:var(--neon-cyan);">Loading experiences…</a>
      </ins>
      <script type="text/javascript">
        (function (d, sc, u) {
          var s = d.createElement(sc),
            p = d.getElementsByTagName(sc)[0];
          s.type = "text/javascript"; s.async = true; s.src = u;
          p.parentNode.insertBefore(s, p);
        })(document, "script", "https://affiliate.klook.com/widget/fetch-iframe-init.js");
      </script>
    </div>

    <h2 class="headline neon-yellow" style="margin-top:48px;">CURATED TOUR GUIDES</h2>
    <p style="color:var(--text-muted); margin-bottom:24px;">Our hand-picked takes on each tour category.</p>
    <div class="grid grid-3">
      <div class="card" style="padding:24px;"><h3 class="display neon-cyan" style="margin:0 0 8px;">GRAND CANYON HELICOPTERS</h3><p>The difference between West Rim and South Rim, and which helicopter company we'd personally book.</p></div>
      <div class="card" style="padding:24px;"><h3 class="display neon-pink" style="margin:0 0 8px;">HOOVER DAM DAY TRIPS</h3><p>Bus, boat, or drive-yourself — how to see the dam without wasting a full day.</p></div>
      <div class="card" style="padding:24px;"><h3 class="display neon-yellow" style="margin:0 0 8px;">RED ROCK CANYON</h3><p>The 45-minute version and the full-day version — both done right.</p></div>
      <div class="card" style="padding:24px;"><h3 class="display neon-cyan" style="margin:0 0 8px;">THE SPHERE</h3><p>How to actually get tickets that aren't the nosebleeds, and the best hotels to walk from.</p></div>
      <div class="card" style="padding:24px;"><h3 class="display neon-pink" style="margin:0 0 8px;">STRIP NIGHT TOURS</h3><p>High Roller, gondola, fountain-side dinners — which are worth it.</p></div>
      <div class="card" style="padding:24px;"><h3 class="display neon-yellow" style="margin:0 0 8px;">VALLEY OF FIRE</h3><p>The most underrated day trip from Vegas — and why we like it more than the Grand Canyon.</p></div>
    </div>
  </div>
</section>
""" + FOOTER
    write("tours/index.html", html)

# ---------------------------- THINGS TO DO ---------------------------- #

LISTICLES = [
    ("25-free-things-to-do-in-vegas", "25 Free Things to Do in Las Vegas (From a Local) | TheVegasHub",
     "Twenty-five genuinely free things to do in Las Vegas — Bellagio fountains, Fremont Street, Red Rock, and every free show locals actually watch.",
     "25 Free Things to Do in Las Vegas",
     [("Watch the Bellagio Fountains","On the hour and half-hour from 3pm, every 15 mins after 8pm. Best viewed from the bridge at Caesars."),
      ("Walk the Fremont Street Experience","The free neon canopy shows run every hour after dark — zero cover, wild people-watching."),
      ("Ride the High Roller at sunset (yes, free-ish)","$25 happy-hour cabin gets you a full bar and a loop. Cheaper than any rooftop bar."),
      ("Explore the Conservatory at Bellagio","Changes 5 times a year. Open 24/7 and free to walk through."),
      ("Watch Mirage volcano... oh wait","R.I.P. Grab a drink at The Pinball Hall of Fame instead — it's free to enter."),
      ("Walk Red Rock Canyon scenic loop","$20 per car for the loop, zero per person if you're a passenger. Best desert views in the valley."),
      ("Take a free gondola ride? Almost.","The outdoor ride at the Venetian is paid; the window shopping in St. Mark's Square is free and photogenic."),
      ("Visit the Neon Museum Boneyard exterior","Walk past the glowing sign yard on Las Vegas Blvd after dark — the outside is free."),
      ("People-watch at the Wynn Atrium","Flowers, chandeliers, and serious money. Free coffee if you know where to sit."),
      ("Hit the Aria public art collection","Free self-guided tour. Maya Lin, Henry Moore, Jenny Holzer."),
      ("Watch a wedding at the Little White Chapel","People really will invite you in. Vegas in a nutshell."),
      ("Catch the free CircusCircus acts","Acrobats every half hour above the midway. Nostalgic, kid-friendly, free."),
      ("Walk the Strip at 6am","Empty, cool, photographable. The only time the Strip is ever quiet."),
      ("Hike the Historic Railroad Trail at Lake Mead","Free, easy, ends at Hoover Dam's rear view."),
      ("Tour the Ethel M Chocolate Factory","Free samples, free cactus garden. Real hidden gem."),
      ("Check out the Downtown Container Park","Shops, kids' park, the giant fire-breathing praying mantis. Free entry."),
      ("Watch planes land from Sunset Park","Best sunset in the valley and directly in line with the airport. Free. Bring food."),
      ("Visit the Clark County Wetlands Park","Nobody comes here. Ducks, herons, 3 miles of trails. Free."),
      ("Browse the Forum Shops aquarium","7 feeding times a day. Free to watch."),
      ("Catch the Silverton Aquarium mermaids","Free mermaid show in the lobby aquarium. Yes, really."),
      ("Walk the First Friday arts district","First Friday of every month — free entry to galleries in the 18b."),
      ("Tour the Springs Preserve gardens exterior","Grounds and trails are free; museum is paid. Still worth the walk."),
      ("Mount Charleston lookouts","Free pullouts with 50-mile valley views, 45 minutes from the Strip."),
      ("See the flamingos at the Flamingo","Live flamingos in a garden behind the pool. Free to walk through."),
      ("Do a sunrise at Hoover Dam","Bypass Bridge is free and the Dam views are 100% worth the 6am alarm.")]),

    ("best-pools-in-las-vegas", "Best Pools in Las Vegas 2026 — Ranked by Locals | TheVegasHub",
     "The best pools in Las Vegas ranked by locals — Mandalay Bay, Caesars Garden of the Gods, Cosmopolitan, Red Rock, and more. Pool-season picks.",
     "Best Pools in Las Vegas",
     [("Mandalay Bay Beach","A real sand beach, a wave pool, and a lazy river. Still the best big-pool complex on the Strip."),
      ("Caesars Palace Garden of the Gods","Seven pools, Roman columns, and the best adult pool (Venus) if you're over it."),
      ("Cosmopolitan Boulevard Pool","Pool parties above the Strip with live concerts. Views and noise for days."),
      ("Red Rock Resort Backyard Pool","Two pools, cabanas, desert mountain backdrop. Our favorite off-Strip pool scene."),
      ("Green Valley Ranch Pool Backyard","Grass, palm trees, Strip skyline views. Henderson's best-kept secret."),
      ("Wynn Tower Suites Pool","Exclusive to Tower Suite guests — the quietest luxury pool on the Strip."),
      ("Aria Liquid Pool","DayClub energy on weekends, chill vibes weekdays. Good food, young crowd."),
      ("Venetian Voyagers Club Pool","Four pools, cabanas, hidden adults-only Tao Beach. Underrated."),
      ("Bellagio Cypress Pool","Quiet and classy. Cabana rentals come with service and great cocktails."),
      ("MGM Grand Wet Republic","Pool party central. Skip this if you want quiet; come here if you want chaos."),
      ("Resorts World Pool Complex","Eight pools. Newest of the bunch. Kids welcome, families approved."),
      ("Palms Pool","Reopened renovated and we love it. Infinity edge with Strip views."),
      ("South Point Pool","Locals' pool. Cheap food, cheap drinks, zero pretense."),
      ("Circa Stadium Swim","Six pools stacked like stadium seats around a 143-foot screen. 21+. Sports-bar DNA."),
      ("Waldorf Astoria Pool (SLS/Hilton)","Highest pool on the Strip. The quiet-luxury option.")]),

    ("best-day-trips", "Best Day Trips from Las Vegas 2026 | TheVegasHub",
     "The best day trips from Las Vegas — Grand Canyon, Hoover Dam, Red Rock, Valley of Fire, Death Valley, and Zion. Drive times + booking links.",
     "Best Day Trips from Las Vegas",
     [("Grand Canyon West Rim (Skywalk)","2h15m each way · The closest Grand Canyon view from Vegas. Skywalk is the attention-grabber; Guano Point is the actual view."),
      ("Grand Canyon South Rim","4h15m each way · Longer drive, bigger canyon. Worth the overnight if you can."),
      ("Hoover Dam","45 min each way · The actual dam tour is 90 minutes. Combine with Lake Mead."),
      ("Red Rock Canyon Scenic Loop","30 min each way · 13-mile loop, pullouts, short hikes. Our go-to Vegas morning."),
      ("Valley of Fire State Park","1h each way · Underrated red-rock state park. Less crowded than Red Rock, more dramatic."),
      ("Mount Charleston","45 min each way · Pine trees, snow in winter, 30 degrees cooler in summer. Vegas's local reset."),
      ("Death Valley National Park","2h each way · October-April only. Lowest point in North America, wildest terrain."),
      ("Zion National Park","2h45m each way · Best done as an overnight in Springdale, UT. Drives you want to do."),
      ("Seven Magic Mountains","25 min each way · Giant neon-rock art installation. 15-minute stop, great photo."),
      ("Laughlin on the Colorado River","1h30m each way · Cheap rooms, beach, jet skis, buffets. Great weekend away from Vegas."),
      ("Area 51 / Extraterrestrial Highway","2h30m each way · Weird roadside stop. You won't see aliens. You will see a lot of Joshua trees."),
      ("Bryce Canyon","3h45m each way · Push-yourself long day. Most photogenic national park in the Southwest.")]),

    ("strip-hotels-under-200", "Las Vegas Strip Hotels Under $200 in 2026 | TheVegasHub",
     "The best Las Vegas Strip hotels under $200 per night in 2026 — locals' picks for good rooms, good pools, and good locations without the luxury price tag.",
     "Strip Hotels Under $200",
     [("Treasure Island (TI)","Center Strip, clean rooms, pedestrian bridge to Fashion Show Mall. Midweek often under $120."),
      ("Luxor","South Strip, huge pyramid, walking distance to Allegiant Stadium. Tower rooms only."),
      ("Excalibur","Cheapest real Strip hotel. Basic rooms, castle-themed, family-friendly. Often $79."),
      ("Flamingo","Center Strip in the middle of everything. Go Rooms are the renovated ones — ask for one."),
      ("MGM Grand","Huge complex, good pool, walkable to T-Mobile Arena. Midweek often under $150."),
      ("Harrah's","Center Strip Carnaval Court. Old-school but a great location. Often under $130."),
      ("LINQ","Attached to the High Roller observation wheel. Renovated rooms. Often under $150."),
      ("Planet Hollywood","Center Strip, great pool, the Miracle Mile shops. Often under $170."),
      ("Paris","Center Strip with Eiffel Tower. Rooms are average but views are not. Often under $180."),
      ("Park MGM","South Strip, non-smoking, Dolby Theater venue. Often under $180."),
      ("Rio","Off-Strip but huge all-suite rooms. Often under $100 during renovation."),
      ("Westgate Las Vegas","Off-Strip near the Convention Center. Biggest rooms in the city. Often under $120.")]),

    ("best-vegas-shows", "Best Vegas Shows Right Now (2026) | TheVegasHub",
     "The best Las Vegas shows right now in 2026 — residencies, Cirque du Soleil, Sphere productions, magic, comedy. Where to stay for each.",
     "Best Vegas Shows Right Now",
     [("The Sphere: Postcard from Earth","Immersive 16K visual experience. Not a concert — an IMAX on steroids. Stay at Venetian/Palazzo."),
      ("Adele at The Colosseum","When in town. Caesars is your stay. Nothing else comes close live."),
      ("Usher Residency","Wherever it's playing right now. Two-hour party — buy the meet-and-greet upgrade if your budget allows."),
      ("O by Cirque du Soleil","Bellagio. Water show. Old but still the one tourists should see."),
      ("Mystère by Cirque du Soleil","Treasure Island. Best bang-for-buck Cirque show. Family-friendly."),
      ("KÀ by Cirque du Soleil","MGM Grand. Most visually stunning stage in Vegas. Still flying trapezes after 20 years."),
      ("Absinthe","Caesars. Adults only. Comedy, burlesque, circus. Still hilarious year 14."),
      ("Michael Jackson ONE","Mandalay Bay. Cirque + MJ's catalog. Emotional even if you weren't a fan."),
      ("Magic Mike Live","Sahara. Bachelorette standard. Bring the bride."),
      ("Shin Lim at Mirage/future venue","Best close-up magic in Vegas right now."),
      ("Piff the Magic Dragon","Flamingo. Comedic magic. Cheaper than the big Cirque shows and arguably better."),
      ("David Copperfield","MGM Grand. The classic. Still impressive."),
      ("Criss Angel Mindfreak","Planet Hollywood. You either love it or you don't. No in-between."),
      ("The Beatles LOVE (closing)","Mirage — check status. If open, see it. If closed, streaming's the only way now.")]),

    ("best-vegas-buffets", "Best Las Vegas Buffets Ranked (2026) | TheVegasHub",
     "The best Las Vegas buffets in 2026 — Bacchanal, Wicked Spoon, Garden Buffet, and the rest. Ranked by locals who do this for research, not fun.",
     "Best Vegas Buffets Ranked",
     [("Bacchanal Buffet at Caesars Palace","$79 weekdays. Still the #1 buffet in Vegas — live-carving stations, seafood tower, best dessert spread. Reserve a slot online."),
      ("Wicked Spoon at Cosmopolitan","Individual-portion format that changed the buffet game. Adults only after 9pm. Best brunch."),
      ("The Buffet at Wynn","Understated, classy, excellent quality. Smaller crowds. Best for a real meal, not a competitive-eating session."),
      ("Garden Court Buffet at Main Street Station","Downtown. $28. Still the best value buffet in the city — chase it with a cocktail at the adjoining brewpub."),
      ("A.Y.C.E. Buffet at Palms","Reopened, renovated. Pool-day calorie refill station."),
      ("Flavors at Harrah's","Middle-of-the-road buffet in a middle-of-the-road Strip hotel. Cheap and fine."),
      ("The Buffet at Aria","Priced like a steakhouse, eats like one. Worth it once."),
      ("MGM Grand Buffet","Competent, huge, never empty. Sunday brunch is the play."),
      ("Bayside Buffet at Mandalay Bay","Pool-adjacent brunch with the strongest mimosa pour on the Strip."),
      ("South Point Buffet","Locals' buffet. $22 weekdays. Quality punches way above the price."),
      ("Carnival World Buffet at Rio","Reopening reports pending — historically one of the biggest in town."),
      ("Feast Buffet at Green Valley Ranch","Henderson. Best-kept secret of the Station Casinos chain."),
      ("Circus Buffet at CircusCircus","We recommend it ironically. You were warned.")]),

    ("best-adults-only-pools", "Best Adults-Only Pools in Las Vegas 2026 | TheVegasHub",
     "The best adults-only pools in Las Vegas for 2026 — Marquee Dayclub, Moorea, Encore Beach Club, and the best quiet adult pools for when you just want peace.",
     "Best Adults-Only Pools in Las Vegas",
     [("Marquee Dayclub at Cosmopolitan","21+. DJ-driven pool party every weekend, summer residencies. Book a cabana or table."),
      ("Encore Beach Club","21+. The original premium pool party. Calvin Harris, Diplo, Kaskade routinely. Bring real money."),
      ("Ayu Dayclub at Resorts World","21+ on weekends. Newest pool venue on the Strip. Massive."),
      ("Moorea Beach Club at Mandalay Bay","Topless-optional European-style adult pool. Much quieter than Dayclub energy."),
      ("Tao Beach at Venetian","21+. Smaller, more curated. Adults-only section with food from Tao."),
      ("Elia Beach Club at Virgin Hotels","21+. Underrated — Greek-island vibes with actual quality food."),
      ("Drai's Beach Club at The Cromwell","21+. Rooftop pool with Strip views. Night pool on Saturdays."),
      ("Stadium Swim at Circa Las Vegas","21+ downtown. 6 pools stacked like a stadium around a massive screen. Sports-bar vibe."),
      ("Waldorf Astoria Pool","Guests only. Adults-only. Quietest luxury pool on the Strip."),
      ("Rio Pool (adults-only section)","In the renovation reopen. Worth checking if you want a quieter pool."),
      ("Bellagio Cypress Pool","Guests only. Adults-only. The classy old-money pool."),
      ("Liquid Pool at Aria","21+ some days. Good daytime party without Encore Beach Club's intensity.")]),

    ("best-f1-hotels", "Best Las Vegas F1 Grand Prix Hotels 2026 | TheVegasHub",
     "Best hotels for the Las Vegas F1 Grand Prix 2026 — rooms with track views, walkable to the pit, and where to get the best member rates.",
     "Best Vegas F1 Hotels",
     [("Wynn Las Vegas","Inside the track. North-facing rooms look directly down the main straight. Views + no traffic."),
      ("Encore at Wynn","Same campus as Wynn — suites with track views without the Wynn price."),
      ("Venetian","Track wraps around the front drive. Palazzo side is quieter."),
      ("Palazzo","Same footprint as Venetian. All-suite = easier for a 4-night F1 weekend."),
      ("The Cosmopolitan","Terrace Suites face the pit and main straight. Book a terrace and you don't need a grandstand ticket."),
      ("Waldorf Astoria","North-facing rooms above floor 20 = track views without the hotel-inside-track insanity."),
      ("Fontainebleau","New for F1. North end of the Strip, close to Turn 14."),
      ("Bellagio","Faces the track across the fountains. Spectacular."),
      ("Caesars Palace","Track runs right along the property. Balcony suites sell out first."),
      ("Paris Las Vegas","Eiffel Tower observation deck becomes a grandstand during F1 weekend."),
      ("Flamingo","Closer to the track than Paris. Budget F1 option if you're not here for luxury."),
      ("Planet Hollywood","Mid-Strip, affordable F1 stay if you don't need a track-view room.")]),

    ("hidden-speakeasies-vegas", "10 Hidden Speakeasies in Las Vegas (Locals' Picks) | TheVegasHub",
     "The best hidden speakeasies and secret bars in Las Vegas — password-protected doors, unmarked entrances, and the cocktail scenes tourists don't find.",
     "Hidden Speakeasies in Las Vegas",
     [("The Laundry Room at Commonwealth","Downtown. Text for the password, enter through a hidden door inside Commonwealth. 22 seats."),
      ("Herbs & Rye","Off-Strip. Everyone eventually ends up here after 1am. Best steakhouse-speakeasy combo in the city."),
      ("Ghost Donkey at Cosmopolitan","Mezcal-focused, hidden inside Block 16 food hall. Disco ceiling. Nachos."),
      ("Peppermill's Fireside Lounge","Not hidden, but iconic. Sunken fire pit in the center. Unchanged since 1972."),
      ("Velveteen Rabbit","Downtown arts district. Local crowd. Some of the best cocktails in the city under $15."),
      ("Downtown Cocktail Room","Unmarked door near Ogden. Classic cocktails done right. First Tom Collins of your trip."),
      ("Vanderpump à Paris","Tucked inside Paris Las Vegas. Flower walls, pink everything, Lisa Vanderpump's place."),
      ("Atomic Liquors","America's oldest freestanding bar. Opened 1952. Not hidden but locally iconic."),
      ("Delilah at Wynn","Speakeasy-inspired supper club. Not truly hidden, but feels like it."),
      ("The Library at Alibi (Aria)","Inside the Aria lobby bar. Turn left at the fireplace."),
      ("Oak & Ivy at Downtown Container Park","Small, excellent, cash-first. The bartenders don't care who you are."),
      ("The Underground at Mob Museum","Actual basement speakeasy inside the Mob Museum. Prohibition-era cocktails.")]),

    ("best-cheap-eats-vegas", "15 Best Cheap Eats in Las Vegas (Under $20) | TheVegasHub",
     "The best cheap eats in Las Vegas under $20 — off-Strip tacos, Chinatown noodles, $5 shrimp cocktails, and the locals' go-to quick meals.",
     "Best Cheap Eats in Las Vegas",
     [("Raising Cane's on the Strip","Open 24/7. Chicken fingers. This is why we live in 2026."),
      ("Tacos El Gordo","East side + Strip. Best Tijuana-style tacos in the city. $3 tacos al pastor."),
      ("Pho Kim Long","Chinatown. Huge portions, under $15. Always a 30-minute wait. Always worth it."),
      ("Battista's Hole in the Wall","$45 dinner that feels like $90. Old-school Italian next to Flamingo, all-you-can-drink wine included."),
      ("The Peppermill coffeeshop","The adjoining diner has 24-hour breakfast. Famous fruit plate. Under $20."),
      ("Earl of Sandwich at Planet Hollywood","Best Strip lunch under $15. Cabo sandwich or the Original 1762."),
      ("Nacho Daddy downtown","Under $20. The fried-tarantula taco is a thing. Skip it — order the nachos."),
      ("Secret Pizza at Cosmopolitan","Hidden pizza counter on the 3rd floor. Under $10 a slice."),
      ("Monta Ramen, Chinatown","Best tonkotsu in the city. Under $18."),
      ("Fat Choy at Eureka Casino (Fremont)","Hawaiian + Asian fusion. Loco moco is the move. Under $18."),
      ("Gold Fork Burger Bar (Downtown)","Best Vegas burger under $15. 4 lines of delicious."),
      ("Makers & Finders","Arts District. Coffeeshop + Latin brunch. $15 huevos rancheros."),
      ("Shake Shack (Strip + Downtown)","Don't roll your eyes. It's good. Under $15."),
      ("Bachi Burger","Asian-fusion burgers. Ramen burger if you dare. Henderson location is quieter."),
      ("The Pizzeria at The Palazzo","24-hour NY slice. Under $8. Best pizza emergency in the city.")]),

    ("best-breakfast-spots-vegas", "12 Best Breakfast Spots in Las Vegas | TheVegasHub",
     "The best breakfast spots in Las Vegas — hangover fixes, brunch standouts, Strip breakfasts worth their price, and the locals' morning picks.",
     "Best Breakfast Spots in Las Vegas",
     [("Hash House A Go Go (Plaza + Linq)","Biggest portions in the city. The sage fried chicken benedict is the move."),
      ("Eggslut at Cosmopolitan","Sandwich-driven. The Fairfax is famous for good reason."),
      ("The Henry at The Cosmopolitan","24-hour menu. Chicken & waffles, famous burger. $30 average."),
      ("The Kitchen at The Wynn","High-end à la carte. Best eggs benedict on the Strip. $45."),
      ("Bouchon at The Venetian","Thomas Keller's bistro. Weekend brunch is the Vegas expense-account brunch."),
      ("Black Tap at The Venetian","Shake + burger for breakfast. $20 freak-out shakes."),
      ("Skinny Fats Happy","Off-Strip. Two menus — healthy vs happy. Always-packed locals' brunch."),
      ("Mr Mamas Breakfast & Lunch","Off-Strip chain. Chicken-fried everything. Loved by locals."),
      ("The Peppermill coffeeshop","Icons. Fruit plate, 24-hour menu, next to Resorts World."),
      ("Bacchanal Brunch at Caesars","Adds breakfast to the buffet rotation on Sat/Sun. Worth the price."),
      ("Oscar's at the Plaza (downtown)","Old-school downtown breakfast with a Strip-view from the dome."),
      ("Du-par's at Golden Gate","Pancakes since 1938. Thick-cut bacon. Downtown.")]),

    ("best-sports-bars-vegas", "Best Sports Bars in Las Vegas for 2026 | TheVegasHub",
     "The best sports bars in Las Vegas — UFC watch parties, Monday Night Football, F1 livestream, and locals' picks with the most screens.",
     "Best Sports Bars in Las Vegas",
     [("Circa Stadium Swim","6-pool sports complex with a 143-foot screen. 21+. Weekend game-day legendary."),
      ("The Barstool Sportsbook at Circa","Three-story bar-book. Best in the city. Food from Saddle Ranch."),
      ("Westgate SuperBook","Biggest sportsbook in Vegas. 30,000 sq ft, 220-foot video wall. Not fancy, just serious."),
      ("The Tap at MGM","MGM Grand sports bar. Closest to T-Mobile Arena. Perfect pre/post game."),
      ("Beer Park at Paris","Rooftop with a direct view of the Bellagio fountains AND every NFL Sunday game."),
      ("Cabana Grill at Durango","Best locals' sportsbook experience. Newer property, premium tech."),
      ("Hooters Vegas","Yes, really. It's a sports bar. Cheap beer, cheap wings, lots of screens."),
      ("Nine Fine Irishmen at NYNY","Authentic-ish Irish pub with soccer (football). UEFA / Premier League coverage."),
      ("Sporting Life Bar","Locals' sports bar off-Strip. Cheap beer, 15 screens, no tourists."),
      ("Canyon Grill at Red Rock Resort","Summerlin. Upscale but still sports-bar enough. Best views of the mountains during day games."),
      ("Fizz at Caesars","Champagne bar that happens to have the games on. Date-night sports."),
      ("Hash House A Go Go (Linq)","Not a sports bar proper but huge screens + huge breakfasts = ultimate NFL Sunday setup.")]),

    ("best-bachelorette-suites", "Best Bachelorette Party Suites in Las Vegas | TheVegasHub",
     "The best Las Vegas bachelorette party suites for 2026 — high-floor Cosmo terraces, Palms Sky Villa, Palazzo Prestige, and where to book for photos and parties.",
     "Best Bachelorette Party Suites",
     [("Palms Sky Villa","Mountain-view multi-level villas with their own pool. Legendary bachelorette territory. $$$$$."),
      ("Cosmopolitan Terrace Suite","Wraparound balcony with fountain views. Best bachelorette photo spot on the Strip."),
      ("Palazzo Prestige Club Lounge","Club-level rooms with suite space + separate lounge. Group-ready."),
      ("Venetian Prestige Suite","Same campus, slightly different vibe. Huge soak tub."),
      ("Caesars Palace Colosseum Suites","Old-Vegas glam. Request a Forum Tower renovated room."),
      ("The Signature at MGM","Separate building from the MGM casino. Kitchen + living room = house-party hosting."),
      ("Drai's Penthouse at The Cromwell","Penthouse suite above Drai's nightclub. 21+ energy."),
      ("Nobu Hotel at Caesars","Boutique bride-favorite. Japanese-minimalist suites."),
      ("Bellagio Penthouse","Fountain-view suites. Old-money bachelorette."),
      ("Red Rock Resort Lavish Suites","Summerlin. Bigger rooms, better deals, Strip skyline view."),
      ("Aria Sky Suites","Small separate tower, very private. Limo to the Strip."),
      ("SKYLOFTS at MGM Grand","Private check-in, butler service, rooftop suites. Wedding-level bachelorette.")]),

    ("best-rooftop-pools-vegas", "Best Rooftop Pools in Las Vegas (With Views) | TheVegasHub",
     "The best rooftop pools in Las Vegas — Drai's, Stadium Swim at Circa, Rio sky pool, and the highest pool decks with Strip views.",
     "Best Rooftop Pools in Las Vegas",
     [("Drai's Beach Club at The Cromwell","11 stories up. Best rooftop Strip view. Live DJ weekends."),
      ("Stadium Swim at Circa","Downtown. 6 pools stacked like stadium seats, 143-foot screen."),
      ("The Rooftop Pool at Virgin Hotels","21+. Elia Beach Club + a quiet separate adult pool. Greek-island styling."),
      ("Tank Pool at Golden Nugget","Downtown. Three-story shark-tank water slide through an actual aquarium."),
      ("Boulevard Pool at Cosmopolitan","8th-floor pool above the Strip. Concerts from pool deck during summer."),
      ("Sky Pool at Palms","Rooftop with west-facing sunset view."),
      ("Waldorf Astoria Pool","23rd floor. Guests only. Highest luxury pool on the Strip."),
      ("Ayu Dayclub at Resorts World","New high pool complex. 21+ weekends."),
      ("Pool District at Resorts World","Multi-tier pool deck, one of the largest on the Strip."),
      ("Plaza's Rooftop Pool","Downtown. Strip skyline views from way downtown."),
      ("Rio Pool","Under renovation — was the rooftop pool for parties, reopening specs pending."),
      ("Bellagio Pool Courtyard","Not a rooftop technically but elevated and legendary.")]),

    ("best-20-dinners-vegas", "15 Best $20 Dinners in Las Vegas | TheVegasHub",
     "15 best dinners in Las Vegas for under $20 — off-Strip Chinese, downtown burgers, Italian hole-in-the-wall, and the cheap-eats spots locals actually eat at.",
     "Best $20 Dinners in Las Vegas",
     [("Battista's Hole in the Wall","$45 dinner with bottomless wine — not under $20 per person if you drink, but worth listing. Sandwich at lunch is $14."),
      ("In-N-Out Burger","Every Vegas tourist denies wanting it. Every local has been at 1am. Under $10."),
      ("Tacos El Gordo (multiple)","$3 tacos al pastor. Dinner for $15, fully stuffed."),
      ("Pho Kim Long (Chinatown)","Huge bowl of pho under $15."),
      ("Monta Ramen (Chinatown)","Best tonkotsu for $18."),
      ("Pepperoni's Pizza at Planet Hollywood","Giant slice for under $8."),
      ("Secret Pizza at Cosmopolitan","Same deal. Under $10 a slice, open late."),
      ("Gold Fork Burger Bar","Downtown. Gourmet burger under $15."),
      ("Raising Cane's","24/7 chicken fingers combo under $12. Open late."),
      ("Nora's Italian Cuisine","West-side old-school Italian. Pasta dinners under $20."),
      ("District One Kitchen","Chinatown Vietnamese. Combo plates under $18."),
      ("Earl of Sandwich (Planet Hollywood)","Cabo sandwich + chips + drink under $14."),
      ("Shake Shack","Don't be snobby. $15 combo is fine."),
      ("Du-par's","Downtown. Breakfast-for-dinner under $18. Pancakes and bacon."),
      ("Nacho Daddy","Downtown. Massive nachos to share under $20 per person.")]),
]

def page_listicle(slug, title, desc, h1, items):
    schema_items = [{"@type":"ListItem","position":i+1,"name":n,"description":d} for i,(n,d) in enumerate(items)]
    jsonld = f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"ItemList","name":{json.dumps(h1)},"itemListElement":{json.dumps(schema_items)}}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}},
  {{"@type":"ListItem","position":2,"name":"Things to Do","item":"{SITE}/things-to-do"}},
  {{"@type":"ListItem","position":3,"name":{json.dumps(h1)},"item":"{SITE}/things-to-do/{slug}"}}
]}}
</script>"""
    rows = "".join(f"""      <div class="card" style="padding:24px; flex-direction:row; gap:20px; align-items:flex-start;">
        <div class="display neon-cyan" style="font-size:40px; min-width:60px; line-height:1;">{i+1:02d}</div>
        <div>
          <h3 class="headline" style="font-size:22px; margin:0 0 6px;">{n}</h3>
          <p style="margin:0; color:var(--text-muted);">{d}</p>
        </div>
      </div>
""" for i,(n,d) in enumerate(items))

    html = head(title, desc, f"/things-to-do/{slug}", extra_jsonld=jsonld) + HEADER + f"""
<section class="section">
  <div class="container" style="max-width:900px;">
    <div class="section-head">
      <span class="pill pill-pink">THINGS TO DO</span>
      <h1 class="headline-glow" style="font-size:clamp(40px,6vw,72px); margin:12px 0 8px;">{h1.upper()}</h1>
      <p class="kicker">{desc}</p>
    </div>
    <div style="display:flex; flex-direction:column; gap:16px;">
{rows}    </div>
    <div style="text-align:center; margin-top:40px;">
      <button onclick="VegasHub.share()" class="btn btn-cyan">SHARE THIS LIST</button>
      <a class="btn btn-ghost" href="/things-to-do" style="margin-left:12px;">All Lists</a>
    </div>
  </div>
</section>
""" + FOOTER
    write(f"things-to-do/{slug}.html", html)

ATTRACTIONS = [
    {
        "slug": "sphere",
        "name": "The Sphere Las Vegas",
        "tagline": "The world's largest 16K wraparound LED venue.",
        "hero_img": "/images/attractions/sphere.jpg",
        "hero_alt": "The Sphere Las Vegas glowing exterior at night on the east side of the Strip",
        "pill": "MUST-SEE",
        "intro": "The 366-foot-tall Sphere just east of the Strip is the single most architecturally distinct venue built in Las Vegas in 30 years. Whether you're there for Postcard from Earth, a U2 residency night, or an Anyma show, the experience is unlike any other concert venue on the planet.",
        "sections": [
            ("POSTCARD FROM EARTH", "Darren Aronofsky's 50-minute immersive visual experience is the default Sphere daytime/matinee show. 16K resolution, haptic seats, wraparound audio. Plays almost daily. Get a seat between row 150-250 for the best field of view."),
            ("CONCERT RESIDENCIES", "The Eagles, Kenny Chesney, Phish, Anyma, Dead & Company — Sphere bookings rotate every few months. A Sphere concert is visually unlike anything else in live music."),
            ("BEST HOTELS TO WALK FROM", "Sphere is connected by pedestrian bridge to the Venetian and Palazzo. Wynn, Encore, and Resorts World are a 5-10 minute walk. Don't drive — F1-weekend gridlock is a sample of every Sphere night."),
        ],
        "tip": "For concerts, check StubHub / Vivid Seats the day-of — prices crash when shows don't sell out. Resale 200s often come in below face value 90 min before curtain.",
        "book_label": "CHECK SPHERE TICKETS",
        "book_href": "https://www.thesphere.com/",
    },
    {
        "slug": "bellagio-fountains",
        "name": "Bellagio Fountains",
        "tagline": "The 8-acre lake with choreographed water shows every 30 minutes.",
        "hero_img": "/images/attractions/bellagio-fountains.jpg",
        "hero_alt": "Bellagio Fountains choreographed water jets in front of the Bellagio tower on the Las Vegas Strip at night",
        "pill": "FREE",
        "intro": "The single most photographed attraction in Las Vegas. Twelve hundred water jets, synchronized to a rotating soundtrack of everything from Sinatra to Lady Gaga, firing for 3-5 minutes every 30 minutes (and every 15 minutes after 8pm) — always free, always worth it.",
        "sections": [
            ("BEST VIEWING SPOTS", "The Bellagio Lake bridge (the footbridge on Las Vegas Blvd) is the iconic view. For a higher angle, Eiffel Tower observation deck at Paris or a fountain-view room at Cosmopolitan is unbeatable. For the cheap option: a fountain-view room at Bellagio itself — ask at check-in."),
            ("SCHEDULE", "Weekday afternoons: every 30 minutes starting 3pm. Weekend afternoons: 12pm. After 8pm nightly: every 15 minutes. Last show at midnight. Wind shuts them down — check the Bellagio concierge."),
            ("BEST SONGS TO CATCH", "'Time to Say Goodbye' (Con Te Partirò) is the classic, runs late evenings. Lady Gaga 'Poker Face' during pool-season weekends is a crowd highlight. Holiday shows run November through January."),
        ],
        "tip": "The show that plays closest to 9pm sharp is typically 'My Heart Will Go On' — the most photographed fountain moment in the world. Get to the bridge by 8:50.",
        "book_label": "STAY AT BELLAGIO",
        "book_href": "https://book.hotelroomdiscounters.com/url/d5e1e309-5600-4625-a5eb-f7fe775958f2?isPermanentLink=true",
    },
    {
        "slug": "high-roller",
        "name": "The High Roller at The LINQ",
        "tagline": "The 550-foot observation wheel on the Strip.",
        "hero_img": "/images/attractions/high-roller.jpg",
        "hero_alt": "The High Roller observation wheel at The LINQ Promenade on the Las Vegas Strip at sunset",
        "pill": "STRIP ICON",
        "intro": "Formerly the world's tallest observation wheel (London Eye 2.0), the High Roller gives you 30 minutes of panoramic Strip views from 550 feet up. The Happy Half Hour cabin turns it into a revolving bar with open bar included — a Vegas experience worth having exactly once.",
        "sections": [
            ("STANDARD RIDE", "$25-35 depending on time of day. One 30-minute rotation. Book sunset for best photos. Skip the line is usually available day-of through the LINQ app."),
            ("HAPPY HALF HOUR", "$80 cabin with a bartender. Open bar for the 30-minute ride. For groups of 8+. Best value per ounce on the Strip."),
            ("STAY NEARBY", "The LINQ Hotel is attached. Flamingo, Harrah's, Cromwell, and Caesars are all 2-minute walks. Planet Hollywood and Paris are 5 minutes."),
        ],
        "tip": "Book Happy Half Hour at sunset and you effectively get Strip photos + open bar + rotation for under $10/person with 8 people. Cheapest cabana on the Strip.",
        "book_label": "BOOK HIGH ROLLER",
        "book_href": "https://www.caesars.com/linq/things-to-do/high-roller",
    },
    {
        "slug": "fremont-street-experience",
        "name": "Fremont Street Experience",
        "tagline": "The 5-block neon canopy of Old Vegas.",
        "hero_img": "/images/attractions/fremont-street.jpg",
        "hero_alt": "Fremont Street Experience illuminated neon canopy over Downtown Las Vegas casinos",
        "pill": "FREE",
        "intro": "Five blocks of Downtown, covered by a 1,500-foot-long neon LED canopy that runs synchronized shows every hour after dark. Below: casinos, live music on three stages, zip-lines overhead, cocktail bars, and the street-performer chaos of Vegas's oldest casino strip. It's free, it's loud, and it's one of two places in the city every first-timer needs to see.",
        "sections": [
            ("THE CANOPY SHOWS", "Every hour after dark. Six-minute LED shows that feel like standing inside a music video. Best viewed from dead-center under the canopy, ideally near the Golden Nugget."),
            ("ZIP LINES (SLOTZILLA)", "$30-50 depending on which level (lower 'zip' or upper 'Zoom'). Runs the length of the canopy. Worth it once for the view."),
            ("BEST DRINKS", "Oak & Ivy at Downtown Container Park, Nacho Daddy's on Fremont, and the Peppermill-level classic Carousel Bar inside the Plaza. For cocktails, stroll 3 blocks south to Herbs & Rye."),
        ],
        "tip": "Fremont Street is also where locals go when tourists aren't looking. The crowd leans to older regulars + bachelorette parties, with the best people-watching on any Friday night between 9pm and midnight.",
        "book_label": "STAY DOWNTOWN",
        "book_href": "/hotels/downtown-fremont",
    },
    {
        "slug": "hoover-dam",
        "name": "Hoover Dam",
        "tagline": "The engineering marvel 45 minutes from the Strip.",
        "hero_img": "/images/attractions/hoover-dam.jpg",
        "hero_alt": "Hoover Dam massive concrete arch dam between Nevada and Arizona with Lake Mead reservoir",
        "pill": "DAY TRIP",
        "intro": "726 feet tall. 1,244 feet across. Holds back Lake Mead. Completed in 1935 — still one of the largest concrete structures ever built. The Hoover Dam tour is a 90-minute dose of historical context, actual engineering, and a view you can't get anywhere else on earth. It's 45 minutes from Vegas, and absolutely worth the drive.",
        "sections": [
            ("THE POWERPLANT TOUR", "$15, about 30 minutes. Takes you inside to see the generators. Best intro if you have kids."),
            ("THE DAM TOUR", "$30, about 60 minutes. Goes deeper into the structure — ventilation shafts, maintenance passages. Adults only, slightly claustrophobic, fascinating."),
            ("THE BYPASS BRIDGE (FREE)", "The Mike O'Callaghan-Pat Tillman Memorial Bridge is the arch bridge 900 feet downstream of the dam. Walk the pedestrian path for the best aerial view of the dam. Free."),
        ],
        "tip": "Combine Hoover Dam with a Lake Mead sightseeing stop or drive. The loop from the Strip takes 4 hours including the dam tour — add Valley of Fire State Park if you want a full day of desert scenery.",
        "book_label": "FIND A TOUR",
        "book_href": "/tours",
    },
]

def page_attraction(a):
    img = a["hero_img"]
    jsonld_attr = f"""<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"TouristAttraction",
  "name":{json.dumps(a['name'])},
  "url":"{SITE}/things-to-do/{a['slug']}",
  "image":"{SITE}{img}",
  "description":{json.dumps(a['intro'])},
  "address":{{"@type":"PostalAddress","addressLocality":"Las Vegas","addressRegion":"NV","addressCountry":"US"}}
}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}},
  {{"@type":"ListItem","position":2,"name":"Things to Do","item":"{SITE}/things-to-do"}},
  {{"@type":"ListItem","position":3,"name":{json.dumps(a['name'])},"item":"{SITE}/things-to-do/{a['slug']}"}}
]}}
</script>"""

    sections_html = "".join(f"""
    <div class="card" style="padding:36px; margin-bottom:20px;">
      <span class="pill pill-cyan">{p.upper()}</span>
      <h2 class="headline neon-cyan" style="font-size:30px; margin:14px 0 12px;">{p}</h2>
      <p style="font-size:17px; line-height:1.8; margin:0;">{body}</p>
    </div>""" for i, (p, body) in enumerate(a["sections"]))

    book_rel = 'rel="nofollow sponsored" target="_blank"' if a["book_href"].startswith("http") else ""

    html = head(
        f"{a['name']} — {a['tagline']} | TheVegasHub",
        a["intro"][:155],
        f"/things-to-do/{a['slug']}",
        extra_jsonld=jsonld_attr,
    ) + HEADER + f"""
<section class="hero" style="padding:80px 0 48px; background:linear-gradient(180deg, rgba(10,0,20,.55) 0%, rgba(10,0,20,.88) 100%), url('{img}') center/cover;">
  <div class="container">
    <span class="pill pill-pink" style="margin-bottom:16px; display:inline-block;">{a['pill']}</span>
    <h1 class="headline-glow" style="font-size:clamp(44px,8vw,92px); line-height:1.05; margin:12px 0 16px;">{a['name'].upper()}</h1>
    <p class="sub" style="max-width:720px;">{a['tagline']}</p>
    <a class="btn btn-cyan" href="{a['book_href']}" {book_rel} style="font-size:16px; padding:16px 36px;">{a['book_label']} →</a>
  </div>
</section>

<section class="section">
  <div class="container" style="max-width:900px;">
    <p style="font-size:19px; line-height:1.75; margin:0 0 36px;">{a['intro']}</p>
{sections_html}

    <div class="card" style="padding:28px; background:rgba(255,230,0,.06); border-color:var(--neon-yellow); margin:24px 0;">
      <span class="pill">INSIDER TIP</span>
      <p style="font-size:17px; line-height:1.7; margin:12px 0 0;">{a['tip']}</p>
    </div>

    <div style="text-align:center; padding:40px 0;">
      <a class="btn btn-cyan" href="{a['book_href']}" {book_rel} style="font-size:16px; padding:16px 36px;">{a['book_label']} →</a>
    </div>

    <div style="text-align:center; margin-top:32px;">
      <a class="btn btn-ghost" href="/things-to-do">More Things to Do</a>
    </div>
  </div>
</section>
""" + FOOTER
    write(f"things-to-do/{a['slug']}.html", html)

def page_things_index():
    tiles = "".join(f"""      <a class="card" href="/things-to-do/{s}" style="padding:28px; text-decoration:none;">
        <span class="pill pill-cyan">LIST</span>
        <h3 class="headline" style="font-size:24px; margin:14px 0 6px;">{h1}</h3>
        <p style="margin:0; color:var(--text-muted);">{d}</p>
      </a>
""" for s,_,d,h1,_ in LISTICLES)
    # All attractions: Atomic Golf (custom) + the 5 generated from ATTRACTIONS
    attraction_items = [
        ("atomic-golf", "Atomic Golf Las Vegas", "State-of-the-art driving range, lessons, and one of the best group nights out in the city.", "/images/attractions/atomic-golf.jpg", "Atomic Golf Las Vegas illuminated tech-enabled driving range tower at night"),
    ]
    for a in ATTRACTIONS:
        attraction_items.append((a["slug"], a["name"], a["tagline"], a["hero_img"], a["hero_alt"]))
    attractions = "".join(f"""      <a class="card" href="/things-to-do/{s}" style="text-decoration:none;">
        <img class="card-img" src="{img}" alt="{alt}" loading="lazy" onerror="this.style.display='none'">
        <div class="card-body">
          <span class="pill pill-pink">ATTRACTION</span>
          <h3 class="headline" style="font-size:22px; margin:12px 0 6px;">{name}</h3>
          <p style="margin:0; color:var(--text-muted); font-size:14px;">{desc}</p>
        </div>
      </a>
""" for s, name, desc, img, alt in attraction_items)
    html = head(
        "Things to Do in Las Vegas — Listicles by Locals | TheVegasHub",
        "Locals' ranked lists for Las Vegas — free things to do, best pools, best day trips, best shows, best cheap Strip hotels, plus featured attractions like Atomic Golf.",
        "/things-to-do",
    ) + HEADER + f"""
<section class="section">
  <div class="container">
    <div class="section-head">
      <span class="pill pill-pink">THINGS TO DO</span>
      <h1 class="headline-glow" style="font-size:clamp(44px,7vw,80px); margin:12px 0 8px;">VEGAS LISTICLES</h1>
      <p class="kicker">Ranked by people who actually live here and get nothing paid for their rankings.</p>
    </div>
    <div class="grid grid-3">
{tiles}    </div>

    <div class="section-head" style="margin-top:64px;">
      <h2 class="headline neon-pink" style="font-size:clamp(32px,5vw,48px); margin:0 0 8px;">FEATURED ATTRACTIONS</h2>
      <p class="kicker">Hand-picked Vegas experiences worth building a trip around.</p>
    </div>
    <div class="grid grid-3">
{attractions}    </div>
  </div>
</section>
""" + FOOTER
    write("things-to-do/index.html", html)

# ---------------------------- WHY VEGAS ---------------------------- #

WHY = [
    ("bachelor-parties", "Best Las Vegas Bachelor Party Hotels & Tips | TheVegasHub",
     "Las Vegas bachelor party planning — best hotel suites, day pools, clubs, strip clubs, and drivers. From people who've done this too many times.",
     "Bachelor Parties in Las Vegas",
     "For suites: Palazzo, Cosmopolitan Terrace Suites, or Palms Sky Villas. For day pools: Wet Republic, Tao Beach, Daylight. For drivers: Presidential Limo (locals' company). Always book dinner before the club. Never valet — the 45-minute line at 2am will kill the night."),
    ("family-with-kids", "Best Family-Friendly Las Vegas Hotels & Activities | TheVegasHub",
     "Family-friendly Las Vegas — best hotels with kids, best pools, Discovery Children's Museum, Shark Reef, Circus Circus Adventuredome, and how to skip the casino smoke.",
     "Family with Kids in Las Vegas",
     "Best family hotels: Excalibur (castle + arcade), Mandalay Bay (beach pool), Circus Circus (acrobats + Adventuredome), Resorts World (eight pools). Non-gaming options: Vdara, Trump, Signature at MGM. Must-dos: Shark Reef, Discovery Children's Museum, Ethel M cactus garden, Springs Preserve."),
    ("sports-fans", "Las Vegas for Sports Fans — F1, Raiders, Knights, UFC | TheVegasHub",
     "Las Vegas for sports fans — where to stay for F1 Grand Prix, Raiders games at Allegiant, Golden Knights at T-Mobile, UFC. Closest hotels to every venue.",
     "Las Vegas for Sports Fans",
     "Raiders / Allegiant Stadium: stay at Luxor, Mandalay Bay, Excalibur (walkable). Knights / T-Mobile Arena: MGM Grand, Park MGM, NYNY (walkable via bridge). F1: stay inside the track — Wynn, Venetian, Cosmopolitan (views + no traffic). UFC at T-Mobile: same as Knights. Bonus: the Durango Casino sportsbook is the best in the city."),
    ("first-timers", "First-Time Las Vegas Visitor's Guide | TheVegasHub",
     "A Las Vegas first-timer's guide — where to stay, what to skip, how long to go, what to book in advance, and the Strip mistakes every newbie makes.",
     "First-Time Las Vegas Visitors",
     "Stay on the center Strip your first trip: Cosmo, Bellagio, Caesars, or Venetian. 3 nights is the sweet spot. Book shows before you land — good ones sell out. Walk the Strip early morning. Do NOT drive on the Strip, ever. Use the Monorail or rideshares. The one thing every first-timer skips: Fremont Street at night. Go."),
    ("couples", "Romantic Las Vegas Hotels & Couples Trip Ideas | TheVegasHub",
     "Romantic Las Vegas — couples' hotel picks, best suites, spa days, fountain-view dinners, chapel weddings, and honeymoons.",
     "Las Vegas for Couples",
     "Couples' favorites: Bellagio fountain-view room + Picasso dinner, Vdara non-gaming calm, Wynn Tower Suite + spa morning. Show recs: O, LOVE while it's open, Absinthe for laughs. Skip the club if you want a real date."),
    ("weddings-honeymoons", "Las Vegas Weddings & Honeymoons — Venues, Chapels, Honeymoon Hotels | TheVegasHub",
     "Las Vegas weddings and honeymoons — best chapels, outdoor venues, elopement spots, and luxury honeymoon hotels.",
     "Weddings & Honeymoons",
     "Chapels: Little White Wedding Chapel (the iconic one), Graceland Chapel (for fun), Chapel of the Flowers (for parents). Outdoor: Valley of Fire permit, Red Rock Canyon permit, Neon Boneyard. Honeymoons: Wynn Tower Suites, Waldorf Astoria, Crockfords at Resorts World."),
    ("shows-residencies", "Las Vegas Shows & Residencies Guide | TheVegasHub",
     "Las Vegas residencies and headline shows — Sphere, Adele, Usher, Garth, Dolby Live, and which hotel puts you at the door.",
     "Shows & Residencies",
     "Sphere = stay at Venetian or Palazzo (connected). Colosseum at Caesars = stay at Caesars. Dolby Live at Park MGM = stay at Park MGM or NYNY. T-Mobile = stay at MGM Grand or NYNY. Buy shows before booking hotels — limit your dates to when your show is on."),
    ("conventions", "Las Vegas Convention Hotels — LVCC, Mandalay Bay, Caesars Forum | TheVegasHub",
     "Las Vegas convention and trade-show hotels — closest stays for LVCC, Mandalay Bay Convention Center, Caesars Forum, Wynn, and Venetian meetings.",
     "Conventions & Business Travel",
     "LVCC: Westgate, Las Vegas Hilton, Wynn, Encore, Resorts World. Mandalay Bay Convention Center: Mandalay Bay, Luxor, Delano. Venetian Expo: Venetian, Palazzo. Caesars Forum: Harrah's, LINQ, Flamingo. Monorail runs Convention Center ↔ MGM Grand."),
]

def page_why(slug, title, desc, h1, body):
    jsonld = f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}},
  {{"@type":"ListItem","position":2,"name":"Why Vegas","item":"{SITE}/why-vegas"}},
  {{"@type":"ListItem","position":3,"name":{json.dumps(h1)},"item":"{SITE}/why-vegas/{slug}"}}
]}}
</script>"""
    html = head(title, desc, f"/why-vegas/{slug}", extra_jsonld=jsonld) + HEADER + f"""
<section class="section">
  <div class="container" style="max-width:800px;">
    <div class="section-head">
      <span class="pill pill-yellow">WHY VEGAS</span>
      <h1 class="headline-glow" style="font-size:clamp(40px,6vw,72px); margin:12px 0 8px;">{h1.upper()}</h1>
      <p class="kicker">{desc}</p>
    </div>
    <div class="card" style="padding:32px;">
      <p style="font-size:18px; line-height:1.8;">{body}</p>
    </div>
    <div style="text-align:center; margin-top:32px;">
      <a class="btn btn-cyan" href="/hotels">Find a Hotel</a>
      <a class="btn btn-ghost" href="/why-vegas" style="margin-left:12px;">All Trip Types</a>
    </div>
  </div>
</section>
""" + FOOTER
    write(f"why-vegas/{slug}.html", html)

def page_why_index():
    tiles = "".join(f"""      <a class="card" href="/why-vegas/{s}" style="padding:24px; text-decoration:none;">
        <h3 class="headline neon-cyan" style="font-size:22px; margin:0 0 8px;">{h1}</h3>
        <p style="margin:0; color:var(--text-muted); font-size:14px;">{d}</p>
      </a>
""" for s,_,d,h1,_ in WHY)
    html = head(
        "Why Vegas? Trip-Type Guides — Bachelor, Family, Sports, First-Timer | TheVegasHub",
        "Why people visit Las Vegas — guides by trip type: bachelor parties, family, sports, couples, weddings, conventions, residencies, first-timers.",
        "/why-vegas",
    ) + HEADER + f"""
<section class="section">
  <div class="container">
    <div class="section-head">
      <span class="pill">WHY VEGAS</span>
      <h1 class="headline-glow" style="font-size:clamp(44px,7vw,80px); margin:12px 0 8px;">WHY VEGAS?</h1>
      <p class="kicker">Every trip has a reason. Here's where to stay for yours.</p>
    </div>
    <div class="grid grid-3">
{tiles}    </div>
  </div>
</section>
""" + FOOTER
    write("why-vegas/index.html", html)

# ---------------------------- PACKING LIST ---------------------------- #

def page_packing_list():
    categories = [
        ("Essentials (all Vegas trips)", [
            "Photo ID (driver's license or passport)",
            "Credit/debit cards + some cash",
            "Phone + charger + portable battery",
            "Sunscreen SPF 30+ (yes, even in winter)",
            "Sunglasses",
            "Lip balm with SPF",
            "Refillable water bottle",
            "Comfortable walking shoes (you'll do 20,000+ steps/day)",
            "Business casual outfit (for nicer restaurants)",
            "Hand lotion (Vegas air is desert-dry)",
            "Eye drops",
            "Earplugs (Strip rooms can be loud)",
        ]),
        ("Pool Day / Dayclub", [
            "Two swimsuits (one drying while you wear the other)",
            "Pool cover-up",
            "Flip-flops",
            "Waterproof phone pouch",
            "Pool-safe tote bag",
            "Book or Kindle",
            "Extra sunscreen (they sell $25 bottles at the pool)",
            "Cash for cabana tips",
        ]),
        ("Nightlife / Club", [
            "Going-out outfit (dresses/blazers pass most club codes)",
            "Non-sneaker shoes",
            "Small crossbody bag or clutch",
            "Lipstick / touchup kit",
            "Club-ready cash ($20s for drinks/tips)",
        ]),
        ("Shows & Dining", [
            "One nicer outfit for a main-room show",
            "Reservations confirmed (OpenTable or the hotel app)",
            "Printed or digital show tickets",
        ]),
        ("Grand Canyon / Outdoor Day Trip Add-on", [
            "Light fleece or jacket (Canyon rim is 30°F colder than Vegas)",
            "Hiking shoes",
            "Hat + extra sunscreen",
            "Park pass or $35 entry fee",
            "Snacks + water (2L per person minimum)",
            "Motion-sickness meds if taking a helicopter",
        ]),
        ("F1 Weekend / Big-Event Weekend", [
            "Earplugs (F1 cars are 130 dB)",
            "Event wristband / credentials",
            "Portable phone charger",
            "Layers (Vegas nights drop to 45°F in November)",
            "Backup plan for getting out at 1am (Uber surge will be brutal)",
        ]),
        ("Convention / Business Trip", [
            "2 business outfits per day (morning + evening)",
            "Laptop + charger + extension cord",
            "Business cards",
            "Comfortable dress shoes",
            "Small bottle of pain reliever",
            "Compression socks for flight + 8 hours of walking",
        ]),
        ("Family with Kids", [
            "Stroller or baby carrier (Strip distances are deceiving)",
            "Kids' swimsuits + floaties (most hotel pools have shallow ends)",
            "Snacks (buffet lines are not kid-friendly)",
            "Tablet + headphones",
            "Sunscreen stick for faces",
        ]),
    ]
    blocks = ""
    for name, items in categories:
        lis = "".join(f'<li><label><input type="checkbox"> <span>{it}</span></label></li>' for it in items)
        blocks += f"""
      <div class="card" style="padding:24px; margin-bottom:20px;">
        <h2 class="headline neon-cyan" style="font-size:22px; margin:0 0 12px;">{name}</h2>
        <ul style="list-style:none; padding:0; margin:0; display:grid; grid-template-columns:1fr 1fr; gap:6px 20px;">
          {lis}
        </ul>
      </div>
"""
    html = head(
        "Las Vegas Packing List — Printable & Shareable | TheVegasHub",
        "A free printable Las Vegas packing list by trip type — essentials, pool, clubs, shows, Grand Canyon, F1, conventions, and family. Share or print.",
        "/packing-list",
    ) + HEADER + f"""
<style>
  .packing-list ul label{{display:flex; gap:10px; cursor:pointer; font-size:15px;}}
  .packing-list ul input[type=checkbox]{{accent-color:var(--neon-cyan); min-width:18px; height:18px;}}
  @media (max-width:700px){{.packing-list ul{{grid-template-columns:1fr !important;}}}}
  @media print{{.packing-list ul{{grid-template-columns:1fr 1fr !important;}} .packing-list ul input{{accent-color:#000 !important;}}}}
</style>

<div class="print-header">
  <h1 style="font-size:28px; margin:0;">THE VEGAS HUB — Las Vegas Packing List</h1>
  <p style="margin:4px 0;">TheVegasHub.com · Insider Las Vegas travel · © TheVegasHub.com</p>
</div>

<section class="section packing-list">
  <div class="container" style="max-width:900px;">
    <div class="section-head no-print">
      <span class="pill pill-pink">FREE TOOL</span>
      <h1 class="headline-glow" style="font-size:clamp(40px,6vw,72px); margin:12px 0 8px;">PACKING LIST</h1>
      <p class="kicker">Organized by trip type. Check off as you pack, then print or share.</p>
    </div>

    <div class="no-print" style="display:flex; gap:12px; flex-wrap:wrap; margin-bottom:32px;">
      <button onclick="VegasHub.print()" class="btn btn-cyan">🖨️ PRINT LIST</button>
      <button onclick="VegasHub.share('Las Vegas Packing List — TheVegasHub', 'Free printable Vegas packing list', 'https://thevegashub.com/packing-list')" class="btn btn-pink">📤 SHARE</button>
      <a class="btn btn-ghost" href="https://twitter.com/intent/tweet?url=https%3A%2F%2Fthevegashub.com%2Fpacking-list&text=Free%20printable%20Vegas%20packing%20list" target="_blank" rel="noopener">POST ON X</a>
      <a class="btn btn-ghost" href="https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fthevegashub.com%2Fpacking-list" target="_blank" rel="noopener">SHARE ON FACEBOOK</a>
    </div>

{blocks}

    <div class="no-print" style="text-align:center; margin-top:40px; color:var(--text-muted); font-size:14px;">
      <p>Missing something? <a href="/contact" style="color:var(--neon-cyan);">Tell us</a> — we update this list monthly.</p>
    </div>
  </div>
</section>

<div class="print-watermark">TheVegasHub.com · Free printable · TheVegasHub.com · Insider Las Vegas travel · TheVegasHub.com · Share at TheVegasHub.com/packing-list · TheVegasHub.com</div>
""" + FOOTER
    write("packing-list/index.html", html)

# ---------------------------- ABOUT ---------------------------- #

def page_about():
    html = head(
        "About TheVegasHub — 30 Years of Local Las Vegas Expertise | TheVegasHub",
        "About TheVegasHub — a Las Vegas-headquartered travel guide run by 30-year locals. How we pick hotels, write listicles, and make money.",
        "/about",
    ) + HEADER + """
<section class="section">
  <div class="container" style="max-width:800px;">
    <div class="section-head">
      <span class="pill pill-cyan">ABOUT</span>
      <h1 class="headline-glow" style="font-size:clamp(40px,6vw,72px); margin:12px 0 8px;">HEADQUARTERED IN VEGAS.</h1>
      <p class="kicker">And we have been for thirty years.</p>
    </div>

    <div class="card" style="padding:36px; margin-bottom:24px;">
      <h2 class="headline neon-cyan" style="margin-top:0;">Who We Are</h2>
      <p>We're a small team based in Las Vegas. Our founders have lived here since the mid-1990s — through the Rat Pack ghost-town era, the explosion of the megaresorts, the post-9/11 rebuild, the Cosmo/Aria/Sphere wave, and every pool, buffet, and Cirque show along the way.</p>
      <p>We've stayed in nearly every hotel on this site. Some of them dozens of times. We've watched shows open, close, move, and come back. We know which casinos have the loosest slots (we won't tell you), which pool is actually worth a cabana (we will tell you), and which Strip bathroom is always the cleanest on a busy Friday night (ask us politely).</p>

      <h2 class="headline neon-pink">How We Make Money</h2>
      <p>We earn affiliate commissions when you book hotels and tours through our links. That commission comes from the hotel or tour company — not from you. Your price is the same whether you book through us or directly.</p>
      <p>We don't take paid placements. Every hotel ranking, every listicle, every "our favorite" on this site is editorial. If we don't like a hotel, we don't list it — we don't get paid to hide that.</p>

      <h2 class="headline neon-yellow">How We Pick</h2>
      <p>We rank hotels by a weighted blend of: room quality (how recently renovated, how big, how clean), location (walk time to the Strip or a specific venue), amenities (pool, spa, food, parking), and vibe. We don't care how much a property pays to other listing sites — we care whether we'd personally book it.</p>

      <h2 class="headline neon-cyan">Contact</h2>
      <p>Found a broken link, disagree with a ranking, have a Vegas question? <a href="/contact" style="color:var(--neon-cyan);">Drop us a line</a>. We answer every email.</p>
    </div>
  </div>
</section>
""" + FOOTER
    write("about/index.html", html)

# ---------------------------- CONTACT ---------------------------- #

def page_contact():
    html = head(
        "Contact TheVegasHub — Ask a Las Vegas Local | TheVegasHub",
        "Contact TheVegasHub — ask us anything about Las Vegas hotels, tours, or your upcoming trip. We're based in Vegas and we answer every email.",
        "/contact",
    ) + HEADER + """
<section class="section">
  <div class="container" style="max-width:640px;">
    <div class="section-head">
      <span class="pill">CONTACT</span>
      <h1 class="headline-glow" style="font-size:clamp(40px,6vw,72px); margin:12px 0 8px;">GET IN TOUCH</h1>
      <p class="kicker">Trip questions, press, partnership ideas — reach out.</p>
    </div>

    <form class="contact card" style="padding:32px;" id="contactForm" novalidate>
      <label for="c-name">Name</label>
      <input id="c-name" name="name" type="text" maxlength="120" required>

      <label for="c-email">Email</label>
      <input id="c-email" name="email" type="email" maxlength="254" required>

      <label for="c-subject">Subject</label>
      <input id="c-subject" name="subject" type="text" maxlength="180">

      <label for="c-message">Message</label>
      <textarea id="c-message" name="message" rows="6" maxlength="5000" required></textarea>

      <!-- Honeypot -->
      <input type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute; left:-10000px;">

      <button type="submit" class="btn btn-cyan" style="width:100%; margin-top:8px;">SEND MESSAGE</button>
      <p id="c-status" style="margin-top:12px; font-size:14px; min-height:20px;"></p>
    </form>
  </div>
</section>

<script>
document.getElementById('contactForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const f = e.target;
  const status = document.getElementById('c-status');
  status.style.color = 'var(--text-muted)';
  status.textContent = 'Sending…';
  const body = {
    name: f.name.value,
    email: f.email.value,
    subject: f.subject.value,
    message: f.message.value,
    website: f.website.value,
  };
  try {
    const r = await fetch('/api/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await r.json();
    if (r.ok && data.ok) {
      status.style.color = 'var(--neon-cyan)';
      status.textContent = '✔ Thanks — we got it and will reply shortly.';
      f.reset();
    } else {
      status.style.color = 'var(--neon-pink)';
      status.textContent = data.error || 'Something went wrong. Please try again.';
    }
  } catch (err) {
    status.style.color = 'var(--neon-pink)';
    status.textContent = 'Something went wrong. Please try again.';
  }
});
</script>
""" + FOOTER
    write("contact/index.html", html)

# ---------------------------- LEGAL PAGES ---------------------------- #

LEGAL_LAST_UPDATED = "April 17, 2026"

def legal_page(path, title, desc, heading, body_html):
    html = head(title, desc, path) + HEADER + f"""
<section class="section">
  <div class="container" style="max-width:820px;">
    <div class="section-head">
      <span class="pill">LEGAL</span>
      <h1 class="headline-glow" style="font-size:clamp(40px,6vw,72px); margin:12px 0 8px;">{heading.upper()}</h1>
      <p class="kicker">Last updated: {LEGAL_LAST_UPDATED}</p>
    </div>
    <div class="card" style="padding:36px; font-size:16px; line-height:1.75;">
{body_html}
    </div>
  </div>
</section>
""" + FOOTER
    write(path.lstrip("/") + "/index.html", html)

PRIVACY_BODY = """
      <h2 class="headline neon-cyan" style="margin-top:0;">1. Who We Are</h2>
      <p>TheVegasHub.com ("we," "our," "us") is a Las Vegas–based travel guide operated at thevegashub.com. We provide curated hotel, tour, and trip-planning content and earn affiliate commissions when visitors book through our partner links.</p>

      <h2 class="headline neon-pink">2. What We Collect</h2>
      <p><strong>Information you give us:</strong> If you fill out our contact form or subscribe to our newsletter, we collect the name, email, and message content you submit.</p>
      <p><strong>Information collected automatically:</strong> When you visit the site, we and our analytics provider (Google Analytics 4) collect standard web-server data — IP address, browser type, device type, pages visited, referring URL, and timestamps. This data is used in aggregate to understand site traffic.</p>
      <p><strong>Cookies:</strong> We use cookies for essential site functionality, analytics (Google Analytics), and affiliate link attribution. See our <a href="#cookies" style="color:var(--neon-cyan)">Cookies</a> section below.</p>

      <h2 class="headline neon-yellow">3. How We Use Your Information</h2>
      <ul>
        <li>To respond to your contact-form messages</li>
        <li>To send you our newsletter if you opt in</li>
        <li>To understand site usage and improve our content</li>
        <li>To attribute affiliate bookings and process commission payments</li>
        <li>To prevent fraud and abuse</li>
      </ul>
      <p>We do <strong>not</strong> sell your personal information to third parties.</p>

      <h2 class="headline neon-cyan">4. Third-Party Services</h2>
      <p>We share limited data with the following service providers, each of which has its own privacy policy:</p>
      <ul>
        <li><strong>Google Analytics 4</strong> — for aggregated site analytics</li>
        <li><strong>SMTP2GO</strong> — for delivering contact-form emails</li>
        <li><strong>Brevo (Sendinblue)</strong> — for newsletter delivery (if you subscribe)</li>
        <li><strong>Booking partners</strong> — when you click a booking link, the partner site receives a referral token so we can attribute your booking</li>
        <li><strong>Vercel</strong> — our hosting provider, which collects standard server logs</li>
      </ul>

      <h2 class="headline neon-pink">5. Your Rights</h2>
      <p>Depending on where you live, you may have rights to access, correct, or delete personal data we hold about you. To exercise these rights, email us at <a href="/contact" style="color:var(--neon-cyan)">our contact form</a>.</p>
      <p><strong>California residents</strong> have rights under the CCPA/CPRA. <strong>EU/UK residents</strong> have rights under GDPR. We will respond to verified requests within 30 days.</p>

      <h2 class="headline neon-yellow" id="cookies">6. Cookies</h2>
      <p>We use three categories of cookies:</p>
      <ul>
        <li><strong>Essential</strong> — required for basic site function (session, language preference). Always on.</li>
        <li><strong>Analytics</strong> — Google Analytics to measure site usage. You can opt out in our cookie banner or by using a browser extension like Google Analytics Opt-Out.</li>
        <li><strong>Affiliate attribution</strong> — our booking partners set cookies when you click a link so bookings can be tracked to us. Blocking these will not affect your ability to book.</li>
      </ul>

      <h2 class="headline neon-cyan">7. Data Retention</h2>
      <p>Contact form submissions are retained for up to 2 years. Newsletter subscribers remain until they unsubscribe. Analytics data is retained per Google's default GA4 settings (14 months).</p>

      <h2 class="headline neon-pink">8. Children's Privacy</h2>
      <p>Our site is not directed to children under 13. We do not knowingly collect personal information from anyone under 13.</p>

      <h2 class="headline neon-yellow">9. Changes to This Policy</h2>
      <p>We may update this Privacy Policy from time to time. The "last updated" date at the top will always reflect the most recent revision.</p>

      <h2 class="headline neon-cyan">10. Contact Us</h2>
      <p>Questions about this Privacy Policy? Email us through our <a href="/contact" style="color:var(--neon-cyan)">contact page</a>.</p>
"""

TERMS_BODY = """
      <h2 class="headline neon-cyan" style="margin-top:0;">1. Acceptance of Terms</h2>
      <p>By accessing or using TheVegasHub.com (the "Site"), you agree to these Terms of Service. If you do not agree, please do not use the Site.</p>

      <h2 class="headline neon-pink">2. Editorial Content</h2>
      <p>The information on this Site — including hotel rankings, tour recommendations, "things to do" lists, and editorial commentary — reflects the personal opinions of our writers. It is provided for informational purposes only.</p>
      <p>We strive for accuracy but cannot guarantee that every detail (room rates, amenities, show schedules, tour times, etc.) is current. Always confirm critical details directly with the hotel, tour operator, or venue before you book or travel.</p>

      <h2 class="headline neon-yellow">3. Affiliate Links</h2>
      <p>Many links on this Site are affiliate links — meaning we may earn a commission if you book through them. This does not increase the price you pay, and our rankings are editorial, not paid. See our <a href="/disclosure" style="color:var(--neon-cyan)">Affiliate Disclosure</a> for details.</p>

      <h2 class="headline neon-cyan">4. Third-Party Websites</h2>
      <p>Our links take you to third-party booking sites (Hotel Room Discounters, Atomic Golf, tour providers, etc.). Once you leave TheVegasHub.com, you are subject to those sites' terms and privacy policies. We are not responsible for their content, pricing, availability, or practices.</p>

      <h2 class="headline neon-pink">5. No Warranties</h2>
      <p>The Site is provided "as is." We make no warranties — express or implied — about the accuracy, completeness, or availability of any content. Your use of the Site and any booking you make through it is entirely at your own risk.</p>

      <h2 class="headline neon-yellow">6. Limitation of Liability</h2>
      <p>To the fullest extent permitted by law, TheVegasHub.com and its operators are not liable for any direct, indirect, incidental, or consequential damages arising from your use of the Site or any booking made through a link on the Site — including travel disruptions, cancellations, injuries, property damage, or financial loss.</p>

      <h2 class="headline neon-cyan">7. Intellectual Property</h2>
      <p>All editorial content on this Site — text, rankings, listicles, and original photography — is the property of TheVegasHub.com and is protected by copyright. You may share our URLs freely but may not copy or republish our editorial content without written permission.</p>
      <p>Hotel and attraction photos are either used with permission, licensed, or sourced from booking partner CDNs under our affiliate agreements.</p>

      <h2 class="headline neon-pink">8. User Submissions</h2>
      <p>If you send us feedback, questions, or content via our contact form, we may quote or use it (attributed or anonymously) to improve the Site. Please do not send confidential information.</p>

      <h2 class="headline neon-yellow">9. Prohibited Uses</h2>
      <p>You agree not to: (a) scrape or automatically collect content from the Site; (b) use the Site to send spam or abuse our contact form; (c) attempt to disrupt the Site's operation; or (d) use the Site for any illegal purpose.</p>

      <h2 class="headline neon-cyan">10. Governing Law</h2>
      <p>These Terms are governed by the laws of the State of Nevada, USA. Any dispute will be resolved in the state or federal courts of Clark County, Nevada.</p>

      <h2 class="headline neon-pink">11. Changes</h2>
      <p>We may update these Terms at any time. Continued use of the Site after changes are posted constitutes acceptance of the revised Terms.</p>

      <h2 class="headline neon-yellow">12. Contact</h2>
      <p>Questions? Reach us via our <a href="/contact" style="color:var(--neon-cyan)">contact page</a>.</p>
"""

DISCLOSURE_BODY = """
      <h2 class="headline neon-cyan" style="margin-top:0;">Short Version</h2>
      <p style="font-size:18px;"><strong>We earn commissions when you book hotels, tours, or experiences through our links.</strong> Your price is the same whether you book through us or go direct. Our rankings are editorial — no one pays us to feature them.</p>

      <h2 class="headline neon-pink">FTC Disclosure</h2>
      <p>In accordance with the U.S. Federal Trade Commission's guidelines on endorsements and testimonials (16 CFR Part 255), TheVegasHub.com discloses that many outbound links on this Site are affiliate or referral links.</p>
      <p>When you click one of these links and complete a booking or purchase on the partner's site, we may earn a commission. This commission is paid by the partner — not by you. You pay the same price as any other customer.</p>

      <h2 class="headline neon-yellow">Who Our Affiliate Partners Are</h2>
      <p>Our primary affiliate relationships include (but are not limited to):</p>
      <ul>
        <li><strong>Hotel Room Discounters</strong> — hotel bookings across the Las Vegas region</li>
        <li><strong>Viator</strong> (a Tripadvisor company) — tours and experiences</li>
        <li><strong>Klook</strong> — tours and experiences</li>
        <li><strong>Atomic Golf</strong> (via Impact Radius / sjv.io) — Atomic Golf reservations</li>
        <li>Various direct partnerships for car rentals, helicopter tours, and show tickets</li>
      </ul>

      <h2 class="headline neon-cyan">Our Editorial Independence</h2>
      <p>TheVegasHub.com does <strong>not</strong> accept paid placements, guest posts, sponsored reviews, or "featured hotel" buyouts. We are not influenced by which partner pays the highest commission — we rank hotels, tours, and attractions based on what we would personally book and recommend to friends.</p>
      <p>If a hotel doesn't belong on a list, we leave it off — regardless of whether it's an affiliate partner. If a new place earns a spot, we add it — whether or not it has an affiliate program yet.</p>

      <h2 class="headline neon-pink">How to Tell a Link Is an Affiliate Link</h2>
      <p>Every outbound booking link on this Site is an affiliate link by default. We also mark affiliate links with the HTML attribute <code>rel="nofollow sponsored"</code> in accordance with Google's guidance on affiliate disclosure.</p>

      <h2 class="headline neon-yellow">You Are Never Required to Use Our Links</h2>
      <p>Every hotel, tour, and attraction we recommend can also be booked on the provider's own website without using our link. If you prefer to book elsewhere, more power to you — we appreciate it if you use our links, but there is zero pressure.</p>

      <h2 class="headline neon-cyan">Contact</h2>
      <p>Questions about our affiliate relationships or editorial policy? Reach us through our <a href="/contact" style="color:var(--neon-cyan)">contact page</a>. We answer every email.</p>
"""

def page_legal():
    legal_page("/privacy", "Privacy Policy | TheVegasHub", "TheVegasHub.com privacy policy — what data we collect, how we use it, your rights, and how to contact us.", "Privacy Policy", PRIVACY_BODY)
    legal_page("/terms",   "Terms of Service | TheVegasHub", "TheVegasHub.com terms of service — site usage rules, limitation of liability, and editorial disclaimers.", "Terms of Service", TERMS_BODY)
    legal_page("/disclosure", "Affiliate Disclosure | TheVegasHub", "TheVegasHub.com affiliate disclosure — how we make money, FTC compliance, and our editorial independence policy.", "Affiliate Disclosure", DISCLOSURE_BODY)

# ---------------------------- README ---------------------------- #

README = """# TheVegasHub.com

Insider Las Vegas travel site — static HTML + Tailwind + Vercel serverless contact function.

## Project layout

```
/                      static HTML site root (deploy target)
├── index.html         homepage
├── hotels/            city pages
├── tours/             Tour & day-trip booking widgets
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
"""

def page_readme():
    write("README.md", README)

# ---------------------------- SITEMAP ---------------------------- #

def page_sitemap():
    """Regenerate sitemap.xml including all hotel pages."""
    today = "2026-04-17"
    urls = [
        ("/",                                                 "weekly",  "1.0"),
        ("/hotels",                                           "weekly",  "0.9"),
    ]
    # City hotel pages
    for slug, *_ in CITY_PAGES:
        urls.append((f"/hotels/{slug}", "weekly", "0.9"))
    # Individual hotel pages
    for h in HOTELS:
        urls.append((f"/hotels/{h['slug']}", "weekly", "0.8"))
    # Tours, things-to-do, why-vegas, etc.
    urls.extend([
        ("/tours",                                            "weekly",  "0.9"),
        ("/things-to-do",                                     "weekly",  "0.9"),
        ("/things-to-do/atomic-golf",                         "monthly", "0.8"),
    ])
    for slug, *_ in LISTICLES:
        urls.append((f"/things-to-do/{slug}", "monthly", "0.8"))
    for a in ATTRACTIONS:
        urls.append((f"/things-to-do/{a['slug']}", "monthly", "0.7"))
    urls.append(("/why-vegas", "monthly", "0.8"))
    for slug, *_ in WHY:
        urls.append((f"/why-vegas/{slug}", "monthly", "0.7"))
    urls.extend([
        ("/packing-list", "monthly", "0.8"),
        ("/about",        "yearly",  "0.5"),
        ("/contact",      "yearly",  "0.5"),
        ("/privacy",      "yearly",  "0.3"),
        ("/terms",        "yearly",  "0.3"),
        ("/disclosure",   "yearly",  "0.3"),
    ])
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, cf, pri in urls:
        lines.append(f'  <url><loc>{SITE}{path}</loc><lastmod>{today}</lastmod><changefreq>{cf}</changefreq><priority>{pri}</priority></url>')
    lines.append('</urlset>')
    write("sitemap.xml", "\n".join(lines) + "\n")

# ---------------------------- MAIN ---------------------------- #

if __name__ == "__main__":
    print("Building TheVegasHub.com ...")
    page_hotels_index()
    for slug, title, desc, heading, filt in CITY_PAGES:
        page_city(slug, title, desc, heading, filt)
    for h in HOTELS:
        page_hotel(h, HOTELS)
    page_tours()
    page_things_index()
    for slug, title, desc, h1, items in LISTICLES:
        page_listicle(slug, title, desc, h1, items)
    for a in ATTRACTIONS:
        page_attraction(a)
    page_why_index()
    for slug, title, desc, h1, body in WHY:
        page_why(slug, title, desc, h1, body)
    page_packing_list()
    page_about()
    page_contact()
    page_legal()
    page_sitemap()
    page_readme()
    print("Done.")

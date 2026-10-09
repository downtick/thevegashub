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
    # Safety net: never emit a meta description Google will truncate (>160 chars).
    if len(desc) > 160:
        desc = desc[:156].rstrip(" .,—-") + "…"
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script>try{{var q=new URLSearchParams(location.search).get('theme'),s=localStorage.getItem('vh_theme'),t=q||s;if(t==='dark')document.documentElement.setAttribute('data-theme','dark');else if(t==='light')document.documentElement.setAttribute('data-theme','light');}}catch(e){{}}</script>
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
      <a href="/map">Map</a>
      <a href="/events">Events</a>
      <a href="/tours">Tours</a>
      <a href="/things-to-do">Things to Do</a>
      <a href="/why-vegas">Why Vegas</a>
      <a href="/packing-list">Packing List</a>
      <a href="/about">About</a>
    </nav>
    <button class="theme-toggle" id="theme-toggle" type="button" aria-label="Toggle light or dark theme" title="Switch theme">🌙</button>
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
          <li><a href="/map">Hotel Map</a></li>
          <li><a href="/events">Events</a></li>
          <li><a href="/best-time-to-visit-las-vegas">Best Time to Visit</a></li>
          <li><a href="/where-to-stay-in-las-vegas">Where to Stay</a></li>
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

def md_to_html(md):
    """Minimal markdown -> HTML for guide/landmark bodies: ## / ### headings,
    - lists, [text](url) links, **bold**, and blank-line-separated paragraphs."""
    def inline(s):
        s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
        return s
    out, para, listbuf = [], [], []
    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(para).strip()) + "</p>")
            para.clear()
    def flush_list():
        if listbuf:
            out.append("<ul>" + "".join("<li>" + inline(x) + "</li>" for x in listbuf) + "</ul>")
            listbuf.clear()
    for raw in md.strip().split("\n"):
        line = raw.strip()
        if not line:
            flush_para(); flush_list()
        elif line.startswith("## "):
            flush_para(); flush_list()
            out.append('<h2 class="headline neon-cyan" style="font-size:clamp(24px,3.5vw,32px); margin:34px 0 12px;">' + inline(line[3:]) + "</h2>")
        elif line.startswith("### "):
            flush_para(); flush_list()
            out.append('<h3 class="headline" style="font-size:20px; margin:22px 0 8px;">' + inline(line[4:]) + "</h3>")
        elif line.startswith("- "):
            flush_para(); listbuf.append(line[2:])
        else:
            flush_list(); para.append(line)
    flush_para(); flush_list()
    return "\n".join(out)

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

    # Meta description — aim 130-158 chars: unique note + consistent CTA.
    _cta = " Compare rooms, read local insider tips, and book direct with member rates at TheVegasHub."
    _body = note if note else f"{name} in {city}."
    meta_desc = (_body.rstrip() + _cta)
    if len(meta_desc) > 158:
        meta_desc = meta_desc[:157].rstrip(" .,—-") + "…"

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
        f"{name} | TheVegasHub",
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

CITY_OG = {
    "mesquite": "og-mesquite.jpg",
}

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

    item_list_elements = ",".join(
        f'{{"@type":"ListItem","position":{i+1},"name":"{h["name"]}","url":"{SITE}/hotels/{h["slug"]}"}}'
        for i, h in enumerate(matches)
    )
    jsonld = f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}},
  {{"@type":"ListItem","position":2,"name":"Hotels","item":"{SITE}/hotels"}},
  {{"@type":"ListItem","position":3,"name":"{heading}","item":"{SITE}/hotels/{slug}"}}
]}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"ItemList","name":"Hotels in {heading}","itemListElement":[{item_list_elements}]}}
</script>"""
    og_img = CITY_OG.get(slug, "og-default.jpg")
    html = head(title, desc, f"/hotels/{slug}", og_image=og_img, extra_jsonld=jsonld) + HEADER + f"""
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
        "Hand-picked Las Vegas tours and day trips — Grand Canyon helicopters, Hoover Dam, Red Rock Canyon, and more — with real-time pricing and instant booking.",
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
     [("Mandalay Bay Beach","A real sand beach, a wave pool, and a lazy river. Still the best big-pool complex on the Strip.","https://book.hotelroomdiscounters.com/url/4c92ea5b-8041-4a15-ad5f-8e7c64d17a8c?isPermanentLink=true"),
      ("Caesars Palace Garden of the Gods","Seven pools, Roman columns, and the best adult pool (Venus) if you're over it.","https://book.hotelroomdiscounters.com/url/37fd4154-e924-4140-a926-1be749968985?isPermanentLink=true"),
      ("Cosmopolitan Boulevard Pool","Pool parties above the Strip with live concerts. Views and noise for days.","https://book.hotelroomdiscounters.com/url/a9072bd7-e0de-4928-915b-7f3b6f19eb4b?isPermanentLink=true"),
      ("Red Rock Resort Backyard Pool","Two pools, cabanas, desert mountain backdrop. Our favorite off-Strip pool scene.","https://book.hotelroomdiscounters.com/url/3547149e-31e6-4fa3-9e20-2895fe00f775?isPermanentLink=true"),
      ("Green Valley Ranch Pool Backyard","Grass, palm trees, Strip skyline views. Henderson's best-kept secret.","https://book.hotelroomdiscounters.com/url/60287820-6e5a-4937-9157-bbf09089493c?isPermanentLink=true"),
      ("Wynn Tower Suites Pool","Exclusive to Tower Suite guests — the quietest luxury pool on the Strip.","https://book.hotelroomdiscounters.com/url/f8b0e38f-c6fd-492e-9a3e-b997bd2e8815?isPermanentLink=true"),
      ("Aria Liquid Pool","DayClub energy on weekends, chill vibes weekdays. Good food, young crowd.","https://book.hotelroomdiscounters.com/url/67bc5bd8-c767-4df5-ba17-fe6023f41c1c?isPermanentLink=true"),
      ("Venetian Voyagers Club Pool","Four pools, cabanas, hidden adults-only Tao Beach. Underrated.","https://book.hotelroomdiscounters.com/url/c4641b79-1e63-4f8f-8660-dcd79cf737b1?isPermanentLink=true"),
      ("Bellagio Cypress Pool","Quiet and classy. Cabana rentals come with service and great cocktails.","https://book.hotelroomdiscounters.com/url/d5e1e309-5600-4625-a5eb-f7fe775958f2?isPermanentLink=true"),
      ("MGM Grand Wet Republic","Pool party central. Skip this if you want quiet; come here if you want chaos.","https://book.hotelroomdiscounters.com/url/eda6f82e-c1a8-4745-a3b8-15c3cef886d4?isPermanentLink=true"),
      ("Resorts World Pool Complex","Eight pools. Newest of the bunch. Kids welcome, families approved.","https://book.hotelroomdiscounters.com/url/def2dbd9-8b53-47f0-9492-5a483ae3413c?isPermanentLink=true"),
      ("Palms Pool","Reopened renovated and we love it. Infinity edge with Strip views.","https://book.hotelroomdiscounters.com/url/8a5c7665-1d99-4bc2-8fbb-96353a3aa443?isPermanentLink=true"),
      ("South Point Pool","Locals' pool. Cheap food, cheap drinks, zero pretense.","https://book.hotelroomdiscounters.com/url/6b092939-7475-4bdf-a165-8982357e66d8?isPermanentLink=true"),
      ("Circa Stadium Swim","Six pools stacked like stadium seats around a 143-foot screen. 21+. Sports-bar DNA.","https://book.hotelroomdiscounters.com/url/51a1024a-49bc-44f4-af9e-3cbcbf2833e7?isPermanentLink=true"),
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
     [("Treasure Island (TI)","Center Strip, clean rooms, pedestrian bridge to Fashion Show Mall. Midweek often under $120.","https://book.hotelroomdiscounters.com/url/a0f83e07-d06d-492b-bc03-a88f4ed1d83a?isPermanentLink=true"),
      ("Luxor","South Strip, huge pyramid, walking distance to Allegiant Stadium. Tower rooms only.","https://book.hotelroomdiscounters.com/url/fd87ef10-fd15-4a55-8928-4d0b9e001946?isPermanentLink=true"),
      ("Excalibur","Cheapest real Strip hotel. Basic rooms, castle-themed, family-friendly. Often $79.","https://book.hotelroomdiscounters.com/url/32e59033-e352-4828-ab85-9b183de1fd3b?isPermanentLink=true"),
      ("Flamingo","Center Strip in the middle of everything. Go Rooms are the renovated ones — ask for one.","https://book.hotelroomdiscounters.com/url/f59ce8fb-703e-4058-96f3-94fa74d3ab56?isPermanentLink=true"),
      ("MGM Grand","Huge complex, good pool, walkable to T-Mobile Arena. Midweek often under $150.","https://book.hotelroomdiscounters.com/url/eda6f82e-c1a8-4745-a3b8-15c3cef886d4?isPermanentLink=true"),
      ("Harrah's","Center Strip Carnaval Court. Old-school but a great location. Often under $130.","https://book.hotelroomdiscounters.com/url/0e5b1d45-da6b-4f44-a52f-f21458995288?isPermanentLink=true"),
      ("LINQ","Attached to the High Roller observation wheel. Renovated rooms. Often under $150.","https://book.hotelroomdiscounters.com/url/2a0a4ff9-6469-4e73-a614-5e72dcff6a57?isPermanentLink=true"),
      ("Planet Hollywood","Center Strip, great pool, the Miracle Mile shops. Often under $170.","https://book.hotelroomdiscounters.com/url/0b42f1b2-7f5e-4c86-9ed5-aeabd4cf269d?isPermanentLink=true"),
      ("Paris","Center Strip with Eiffel Tower. Rooms are average but views are not. Often under $180.","https://book.hotelroomdiscounters.com/url/d2a9e5ae-033e-4c3b-b5ae-dbfa56dfe7c9?isPermanentLink=true"),
      ("Park MGM","South Strip, non-smoking, Dolby Theater venue. Often under $180.","https://book.hotelroomdiscounters.com/url/7e6e6b4d-1330-4daf-9690-1e3d075fa8ef?isPermanentLink=true"),
      ("Rio","Off-Strip but huge all-suite rooms. Often under $100 during renovation.","https://book.hotelroomdiscounters.com/url/8cef1442-2bcb-4ce2-b973-08c8cd3db515?isPermanentLink=true"),
      ("Westgate Las Vegas","Off-Strip near the Convention Center. Biggest rooms in the city. Often under $120.","https://book.hotelroomdiscounters.com/url/b080dd7c-4f40-4cde-85f1-a8996132260c?isPermanentLink=true")]),

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

    ("las-vegas-on-a-budget", "Las Vegas on a Budget: 12 Ways to Save in 2026 | TheVegasHub",
     "How to do Las Vegas on a budget in 2026 — cheap Strip hotels, free shows, off-Strip eats, and the moves locals use to cut costs without missing anything.",
     "Las Vegas on a Budget",
     [("Visit Mid-Week","Sunday–Thursday rates are 40–60% lower than Friday–Saturday. Same pools, same casinos, same Strip — just cheaper rooms."),
      ("Stay at Excalibur or Luxor","Both are real Strip hotels under $100 midweek. You'll spend your time at the pool and casino floor anyway."),
      ("Eat in Chinatown","10 minutes from the Strip. Pho for $14, ramen for $18, Korean BBQ for $30/person. None of it is tourist-priced."),
      ("Watch the Bellagio Fountains (Free)","Runs every 15–30 minutes from 3pm daily, every 15 minutes on weekends. Best free show in the city — zero need to go inside."),
      ("Catch Fremont Street Experience (Free)","Hourly neon canopy light show after dark, with live bands every night on three stages. All free."),
      ("Drink at the Sportsbook","Free drinks while gambling. Even minimal slot play gets you comped drinks — far cheaper than $18 club cocktails."),
      ("Use the Free Strip Trams","Three free trams run on the Strip: Mandalay Bay–Excalibur–Luxor, Bellagio–Crystals–Aria–Veer, and Mirage–TI."),
      ("Walk the Strip at Sunrise","Spectacular at 6am — no crowds, great light, cool air. Best free experience in Vegas."),
      ("Skip the Nightclubs","Cover charges plus table minimums plus drinks = $200–400/person per night. The sportsbook has the same screens and costs nothing."),
      ("Pack In-Room Snacks","Bring a small bag of snacks and drinks. Hotel mini-bars and convenience store prices on the Strip are 3–5× what you'd pay at a regular grocery store."),
      ("Get a Total Rewards Card (Caesars)","Free loyalty card covers Caesars, Harrah's, LINQ, Paris, Flamingo, Horseshoe, Bally's. Free play, room discounts, and food comps accumulate fast."),
      ("Watch at the Race & Sportsbook","Avoid $50 game tickets — watch every NFL game, UFC fight, and F1 race at a free (or nearly free) sportsbook seat with a cold beer.")]),

    ("pool-parties-las-vegas", "Best Las Vegas Pool Parties 2026 | Dayclubs & Beach Clubs | TheVegasHub",
     "The best Las Vegas pool parties and dayclubs in 2026 — Encore Beach Club, Marquee, Wet Republic, Drai's, and where to go without blowing your budget.",
     "Best Las Vegas Pool Parties",
     [("Encore Beach Club","21+. The top dayclub in Las Vegas — premier DJs, multiple pools, bungalows, and cabanas. Opens Memorial Day weekend. Cover $40–80/person."),
      ("Marquee Dayclub at Cosmopolitan","21+. Open Thursday–Sunday. Strip views from the 8th floor. Known for celebrity DJ residencies and large bungalows."),
      ("Wet Republic at MGM Grand","21+. Highest-capacity dayclub on the Strip. Multiple pools, good for large groups. Mid-range pricing."),
      ("Drai's Beach Club at The Cromwell","21+ rooftop 11 floors up with direct Strip views. Hip-hop and R&B focused. Some winter programming."),
      ("Ayu Dayclub at Resorts World","The newest mega-dayclub — multi-pool complex, large capacity. Newer property means shorter lines than the legacy clubs."),
      ("Tao Beach at Venetian","21+. More intimate and quieter than Encore or Wet Republic. Better for groups that want the dayclub vibe without peak-intensity crowds."),
      ("Stadium Swim at Circa","21+ all pools, Downtown. Six pools, 143-foot screen overhead showing sports. More laid-back than Strip dayclubs with lower prices."),
      ("Moorea Beach Club at Mandalay Bay","21+. Topless-optional. Adults-only section within the Mandalay Bay beach complex. Quieter and less frenetic."),
      ("Daylight Beach Club at Mandalay Bay","High-capacity indoor/outdoor dayclub inside Mandalay Bay. Backs onto the beach complex for seamless flow."),
      ("Liquid Pool Lounge at Aria","21+ on selected days. More relaxed pace than the mega-clubs. Good for late-morning pool time before evening plans."),
      ("Venus Pool at Caesars Palace","Adults-only, topless-optional, inside Garden of the Gods. Exclusively for Caesars guests. No dayclub cover, no DJ — a quiet contrast to everything else."),
      ("Boulevard Pool at Cosmopolitan","8th-floor hotel pool with Strip views. Lower-key than Marquee Dayclub. Summer concert series uses this pool deck.")]),

    ("grand-canyon-day-trip-from-las-vegas", "Grand Canyon Day Trip from Las Vegas 2026 | TheVegasHub",
     "How to do a Grand Canyon day trip from Las Vegas in 2026 — West Rim vs South Rim, helicopter options, what to combine, and what locals skip.",
     "Grand Canyon Day Trip from Las Vegas",
     [("Grand Canyon West Rim (Skywalk)","2h15m from Las Vegas. Hualapai Tribe-operated. The Skywalk glass bridge extends 70 feet over the rim. Best for first-time visitors on a one-day schedule. Book the Skywalk add-on ($35–50) in advance."),
      ("Grand Canyon South Rim","4h15m by car. The full classic Grand Canyon — Mather Point, Bright Angel Trail, Desert View Watchtower. Better as an overnight but doable in a very long day."),
      ("Hoover Dam (En Route)","Only 45 minutes from Las Vegas. Easy add-on to any Grand Canyon day. Free to view from the bypass bridge, or take the powerplant tour for $15–30."),
      ("Helicopter from Boulder City","Papillon and Maverick both fly Grand Canyon day trips from Boulder City (45 min from Vegas). Total flight 45–50 min each way plus canyon floor time. $400–600/person."),
      ("Airplane Tour (Budget Option)","Small-plane tours from Henderson Executive Airport are $200–350/person. More distance, no canyon floor, but cheaper than helicopter."),
      ("Valley of Fire (Quick Detour)","1 hour from Las Vegas en route to West Rim. Ancient red sandstone formations and Aztec petroglyphs. The Wave and Elephant Rock are 15-minute walks. Free with $15 state park fee."),
      ("Antelope Canyon (2-Day Version)","4 hours from Las Vegas near Page, AZ. Combine with Horseshoe Bend for an overnight road trip. The most photographed slot canyon in the world — book a guided tour in advance."),
      ("Zion National Park (Overnight)","2h45m from Las Vegas via I-15. Angels Landing is the signature hike (permit required). Combine with the Grand Canyon for a national park road trip."),
      ("Organized Bus Tour","Round-trip bus tours to West Rim or South Rim cost $100–180/person with lunch included. Depart from the Strip, no driving required. Good for solo travelers."),
      ("Self-Drive Tips","Fill gas before leaving Las Vegas. There is no fuel between Boulder City and the West Rim. Bring 2 liters of water per person — the canyon rim temperatures are 10–15°F hotter than downtown Las Vegas.")]),
]

LISTICLE_FAQ = {
    "best-pools-in-las-vegas": [
        ("What is the best pool in Las Vegas?", "Mandalay Bay Beach is the best large-scale pool complex in Las Vegas, featuring a real sand beach, wave pool, and lazy river. For luxury, Caesars Garden of the Gods has seven pools including the adults-only Venus pool."),
        ("Which Las Vegas Strip hotels have the best pools?", "Top hotels for pools include Mandalay Bay (beach and wave pool), Caesars Palace (Garden of the Gods), The Cosmopolitan (Boulevard Pool with Strip views), Wynn (Tower Suites Pool), Bellagio (Cypress Pool), and MGM Grand (Wet Republic dayclub)."),
        ("Are Las Vegas hotel pools open to non-guests?", "Most Las Vegas hotel pools are reserved for hotel guests. Some pools offer dayclub access for a cover charge on weekends. Residents may access some Caesars pools for free on select days."),
        ("What is the best adults-only pool in Las Vegas?", "The Venus pool at Caesars Palace is one of the best adults-only pools on the Strip — quiet, elegant, and rarely crowded. Encore Beach Club at Wynn is the top choice for adults who want a dayclub experience."),
    ],
    "strip-hotels-under-200": [
        ("What is the cheapest hotel on the Las Vegas Strip?", "Excalibur is consistently the cheapest real Strip hotel, with rooms often available for $79/night midweek. Luxor and Flamingo are the next most affordable, regularly under $100-$120 on weekdays."),
        ("Can you find Las Vegas Strip hotels under $100?", "Yes. Excalibur and Luxor often drop below $100 midweek. Rio Hotel & Casino (just off-Strip) frequently dips below $100 as well. Weekends on the Strip rarely see rates that low."),
        ("Which Strip hotels have the best value under $200?", "The best-value Strip hotels under $200 include Treasure Island (center Strip, clean rooms), Flamingo (Go Rooms only), LINQ (renovated, attached to High Roller), Paris (Eiffel Tower views), and Park MGM (non-smoking)."),
        ("Is it cheaper to stay on the Strip or off-Strip?", "Off-Strip hotels like Rio and Westgate Las Vegas offer lower rates and larger rooms, but you will need an Uber or car to reach the Strip. If you prefer to walk everywhere, budget Strip hotels like Excalibur are worth the slight premium."),
    ],
    "25-free-things-to-do-in-vegas": [
        ("What are the best free things to do in Las Vegas?", "The best free things in Las Vegas include the Bellagio Fountains (every 15-30 min from 3pm), Fremont Street Experience neon light shows (hourly after dark), the Conservatory at Bellagio, Aria public art collection, and the Ethel M Chocolate Factory with free samples."),
        ("Are there free shows in Las Vegas?", "Yes — several. The Fremont Street Experience canopy shows run every hour after dark and are completely free. The Bellagio Fountains run every 15-30 minutes and are free to watch from the street. Circus Circus has free acrobatic acts every 30 minutes above its midway."),
        ("How do I enjoy Las Vegas on a small budget?", "Focus on free spectacles: Bellagio Fountains, Fremont Street Experience, walking the Strip at sunrise. Eat off-Strip in Chinatown (pho under $15, ramen under $18). Use the free tram between Mandalay Bay and Excalibur. Drink at the sportsbook instead of club."),
        ("Is there anything free to do in Las Vegas during the day?", "Yes — Red Rock Canyon scenic loop ($20/car, free per person), Clark County Wetlands Park, Springs Preserve walking trails, the Forum Shops aquarium (7 free feeding shows daily), and watching the flamingos at Flamingo hotel's wildlife habitat."),
    ],
    "best-day-trips": [
        ("What is the best day trip from Las Vegas?", "Hoover Dam (45 min each way) is the easiest and most impressive day trip from Las Vegas. Grand Canyon West Rim (2h15m) is the closest Grand Canyon experience. Red Rock Canyon (30 min) is the best morning hike. Valley of Fire (1h) is the most underrated."),
        ("Can you do the Grand Canyon as a day trip from Las Vegas?", "Yes — Grand Canyon West Rim (Skywalk) is 2h15m from Las Vegas and makes a comfortable day trip. The South Rim is 4h15m each way and is better as an overnight. Many visitors do the West Rim plus Hoover Dam in one long day."),
        ("How far is Zion National Park from Las Vegas?", "Zion National Park is about 2h45m from Las Vegas via I-15 through St. George, Utah. It makes a long day trip or an excellent overnight in Springdale. The best time to visit is March-May and September-November."),
        ("What is the best day trip from Las Vegas for families?", "Hoover Dam is great for families (free bypass bridge, paid tours). Red Rock Canyon has easy, short scenic trails. Seven Magic Mountains (25 min) is a quick, photogenic stop. Grand Canyon West Rim has the Skywalk, which kids love."),
    ],
    "best-adults-only-pools": [
        ("What are the best adults-only pool parties in Las Vegas?", "The top adults-only pool parties are Encore Beach Club (21+, premium DJs), Marquee Dayclub at Cosmopolitan (21+, great views), Drai's Beach Club at The Cromwell (21+, rooftop with Strip views), and Ayu Dayclub at Resorts World (21+, newest venue)."),
        ("Which Las Vegas pools require guests to be 21+?", "Stadium Swim at Circa (21+ only, all pools), Waldorf Astoria Pool (guests only, adults), Bellagio Cypress Pool (guests only, adults), Drai's Beach Club (21+), Tao Beach at Venetian (21+), Encore Beach Club (21+), and Moorea Beach Club at Mandalay Bay (21+, topless-optional)."),
        ("What is the best quiet adult pool in Las Vegas?", "The Waldorf Astoria Pool is the quietest luxury adult pool — guests only, no dayclub energy. The Bellagio Cypress Pool is the classic old-money quiet option. Wynn Tower Suites Pool is exclusive to Tower Suite guests and extremely peaceful."),
    ],
    "best-vegas-shows": [
        ("What is the best show in Las Vegas right now?", "The Sphere's Postcard from Earth is the most technically impressive experience in Las Vegas right now — 16K resolution, wraparound audio, haptic seats. For live music, Adele at The Colosseum at Caesars Palace is the pinnacle residency. For circus, O by Cirque at Bellagio is the classic."),
        ("Which Cirque du Soleil show should I see in Las Vegas?", "O at Bellagio is the most famous and visually spectacular — a water-based show in a 1.5-million-gallon pool. KÀ at MGM Grand has the most stunning flying stage. Mystère at Treasure Island is the best family-friendly and most affordable Cirque show."),
        ("How far in advance should I book Las Vegas shows?", "Book major residencies (Adele, Usher, headliners) as soon as you know your dates — they sell out months in advance. Cirque shows can usually be booked 2-4 weeks out. The Sphere is often available 1-2 weeks out. Day-of resale is available at reduced prices for many shows."),
    ],
    "best-f1-hotels": [
        ("What are the best hotels for the Las Vegas F1 Grand Prix?", "Hotels inside the track get you the best experience: Wynn (north-facing rooms look down the main straight), The Cosmopolitan (terrace suites face the pit), Venetian, Palazzo, and Bellagio. These hotels eliminate traffic issues and provide track views from your room."),
        ("When is the Las Vegas F1 Grand Prix 2026?", "The Las Vegas Grand Prix runs in November each year, typically the third week of November. Exact 2026 dates are available on the Formula 1 official calendar. Book hotels immediately when dates are announced — F1 weekend rates are 3-5x normal prices."),
        ("Can you watch the F1 from a hotel room in Las Vegas?", "Yes — some hotel rooms directly overlook the track. Wynn north-facing rooms above floor 20, Cosmopolitan terrace suites, and Waldorf Astoria north-facing rooms offer track views. The Paris Eiffel Tower observation deck becomes a grandstand during F1 weekend."),
    ],
    "best-bachelorette-suites": [
        ("What are the best hotels for a bachelorette party in Las Vegas?", "Top bachelorette party hotels are The Cosmopolitan (terrace suites with wraparound balcony fountain views), Palms Sky Villas (multi-level with private pools), Nobu Hotel at Caesars (boutique Japanese-minimalist), and Palazzo Prestige Suites (massive rooms for groups)."),
        ("Which Las Vegas hotel has the best bachelorette suite?", "The Palms Sky Villas are the ultimate bachelorette suites — multi-level penthouse villas with their own pool deck and mountain views. The Cosmopolitan Terrace Suite offers the most iconic photo backdrop (Bellagio Fountain views). SKYLOFTS at MGM include butler service."),
        ("How much should I budget for a Las Vegas bachelorette party?", "Budget varies widely. Hotel suite: $500-5,000/night split among the group. Nightclub table: $2,000-8,000 minimum. Dinner: $80-200/person at a Strip restaurant. Pool party cabana: $500-2,000. Plan $300-600/person per day for a mid-range Las Vegas bachelorette weekend."),
    ],
    "las-vegas-on-a-budget": [
        ("What is the cheapest way to visit Las Vegas?", "Visit mid-week (Sunday-Thursday) and avoid major events. Stay at Excalibur, Luxor, or Circus Circus (often under $60-80 midweek). Eat in Chinatown ($12-18 meals) or at the Garden Court Buffet downtown ($28). Watch the Bellagio Fountains and Fremont Street for free entertainment."),
        ("Can you visit Las Vegas for cheap?", "Yes. The entertainment is surprisingly free-heavy — Bellagio Fountains, Fremont Street shows, casino floors, and the Strip walk are all free. Food is cheapest off-Strip in Chinatown. Budget hotels run $60-120 midweek. The main expense to control is drinks at clubs."),
        ("How much spending money do I need for a weekend in Las Vegas?", "For a budget Vegas weekend (2 nights): hotel $120-200 total, food $100-150, entertainment/shows $50-100, drinks $80-150, transport $40-60. Budget $500-700 total for a frugal but fun 3-day Vegas trip. Mid-range runs $1,000-1,500/person."),
    ],
    "pool-parties-las-vegas": [
        ("What are the best pool parties in Las Vegas?", "The top pool party venues are Encore Beach Club (21+, premium DJs), Marquee Dayclub at Cosmopolitan (21+, Strip views), MGM's Wet Republic (big energy, top DJs), Drai's Beach Club at The Cromwell (rooftop 21+), and Ayu Dayclub at Resorts World (newest, largest)."),
        ("How much does it cost to get into a Las Vegas pool party?", "General admission to most dayclubs runs $30-50 for women and $40-80 for men on weekends. Table minimums start around $2,000-5,000 at premier venues like Encore Beach Club. Day passes to hotel pools (non-dayclub) are often free for guests or $20-35 for non-guests."),
        ("When is pool party season in Las Vegas?", "Las Vegas pool party season runs approximately March/April through October. Peak season is May-September. The biggest DJ residencies run from Memorial Day weekend through Labor Day. Some venues like Drai's run indoor pool parties year-round."),
    ],
    "grand-canyon-day-trip-from-las-vegas": [
        ("How far is the Grand Canyon from Las Vegas?", "The Grand Canyon West Rim (Skywalk) is about 2h15m from Las Vegas — the closest Grand Canyon experience. The Grand Canyon South Rim (the 'main' canyon) is 4h15m by car. Most Las Vegas visitors choose the West Rim for a day trip and the South Rim for an overnight."),
        ("Is the Grand Canyon day trip from Las Vegas worth it?", "Yes — the West Rim is absolutely worth a day trip. The scale of the canyon is impossible to describe and must be seen in person. The Skywalk adds a unique experience. Allow 8-10 hours total (drive + tour). If you have 2 days, the South Rim is significantly more dramatic."),
        ("What is the difference between Grand Canyon West and South Rim?", "West Rim is 2h15m from Vegas, operated by the Hualapai Tribe, includes the Skywalk glass bridge ($35-50 extra), and shows a narrower, lower section of the canyon. South Rim is 4h15m from Vegas, operated by the National Park Service, shows the classic Grand Canyon panorama that covers most photos you've seen."),
    ],
}

LISTICLE_EXTRA_FOOTER = {
    "strip-hotels-under-200": """    <div style="background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.08); border-radius:10px; padding:18px 20px; margin-top:40px; font-size:13px; color:var(--text-muted); line-height:1.7;">
      <strong style="color:rgba(245,245,245,.6); font-size:11px; letter-spacing:.08em; text-transform:uppercase; display:block; margin-bottom:6px;">Pricing Disclaimer</strong>
      Price ranges listed (e.g. "often under $200") reflect rates that have been observed for these properties at some point in time and are provided as general guidance only. Hotel pricing is dynamic and subject to change based on availability, travel dates, demand, and seasonality. Rates shown are not guaranteed. Always verify current pricing before booking.
    </div>
""",
}

def page_listicle(slug, title, desc, h1, items):
    faq_data = LISTICLE_FAQ.get(slug, [])
    schema_items = [{"@type":"ListItem","position":i+1,"name":item[0],"description":item[1]} for i,item in enumerate(items)]

    faq_schema = ""
    if faq_data:
        faq_entities = [{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq_data]
        faq_schema = f'\n<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":faq_entities})}\n</script>'

    jsonld = f"""<script type="application/ld+json">
{json.dumps({"@context":"https://schema.org","@type":"ItemList","name":h1,"itemListElement":schema_items})}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}},
  {{"@type":"ListItem","position":2,"name":"Things to Do","item":"{SITE}/things-to-do"}},
  {{"@type":"ListItem","position":3,"name":{json.dumps(h1)},"item":"{SITE}/things-to-do/{slug}"}}
]}}
</script>{faq_schema}"""

    def make_row(i, item):
        n, d = item[0], item[1]
        link = item[2] if len(item) > 2 else None
        name_html = (f'<a href="{link}" target="_blank" rel="nofollow sponsored noopener" '
                     f'style="color:inherit; text-decoration:underline; text-decoration-color:var(--neon-cyan);">{n}</a>') if link else n
        return f"""      <div class="card" style="padding:24px; flex-direction:row; gap:20px; align-items:flex-start;">
        <div class="display neon-cyan" style="font-size:40px; min-width:60px; line-height:1;">{i+1:02d}</div>
        <div>
          <h3 class="headline" style="font-size:22px; margin:0 0 6px;">{name_html}</h3>
          <p style="margin:0; color:var(--text-muted);">{d}</p>
        </div>
      </div>
"""
    rows = "".join(make_row(i, item) for i, item in enumerate(items))

    faq_html = ""
    if faq_data:
        faq_items = "".join(f"""      <div class="card" style="padding:24px; margin-bottom:16px;">
        <h3 class="headline neon-cyan" style="font-size:20px; margin:0 0 8px;">{q}</h3>
        <p style="margin:0; color:var(--text-muted); line-height:1.65;">{a}</p>
      </div>
""" for q, a in faq_data)
        faq_html = f"""
    <div style="margin-top:56px;">
      <h2 class="headline neon-yellow" style="font-size:clamp(26px,4vw,38px); margin:0 0 20px;">Frequently Asked Questions</h2>
{faq_items}    </div>"""

    extra_footer = LISTICLE_EXTRA_FOOTER.get(slug, "")

    html = head(title, desc, f"/things-to-do/{slug}", extra_jsonld=jsonld) + HEADER + f"""
<section class="section">
  <div class="container" style="max-width:900px;">
    <div class="section-head">
      <span class="pill pill-pink">THINGS TO DO</span>
      <h1 class="headline-glow" style="font-size:clamp(40px,6vw,72px); margin:12px 0 8px;">{h1.upper()}</h1>
      <p class="kicker">{desc}</p>
    </div>
    <h2 class="headline neon-cyan" style="font-size:clamp(22px,3vw,30px); margin:0 0 20px;">Our picks, ranked by locals</h2>
    <div style="display:flex; flex-direction:column; gap:16px;">
{rows}    </div>
{extra_footer}{faq_html}
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
        f"{a['name']} | TheVegasHub",
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

# Full-length guide bodies (markdown), keyed by slug. Override the short WHY
# blurbs above. Authored against the blog-writing word list.
WHY_BODY = {
    "bachelor-parties": '''Planning a bachelor party here is mostly about three bookings: the right suite, a day at a pool club, and a dinner reservation before the night club. Get those three locked and the weekend runs itself. Miss them and you'll spend Saturday in lines.

## Book a suite, not four separate rooms

A suite is the move for a group. It gives you a pre-game spot, a place to leave bags, and one room number everyone routes back to. The [Palazzo](/hotels/palazzo) has some of the largest standard suites on the Strip — sunken living room, room for eight to pre-party. [Cosmopolitan](/hotels/cosmopolitan) Terrace suites come with a wraparound balcony over the Strip, which is rare and worth the upgrade for photos alone. If the group is big and the budget is real, the Palms Sky Villas are a different tier — multiple bedrooms, a private pool on some, the kind of thing you rent once.

Whatever you book, put the suite on one card and split it after. Trying to divide a suite bill at checkout with eight hungover guys never goes well.

## Pool clubs run the daytime

The dayclub is where a Vegas bachelor party actually happens. Wet Republic at MGM Grand is the classic high-energy one. Encore Beach Club draws the biggest DJs. Tao Beach at the Venetian reopened newer and slightly calmer. Buy a table if the group is more than four — a table gets you in without the line, a spot to sit, and bottle service you were going to buy anyway.

Book the table two weeks out for a Saturday, more for a holiday weekend. Dayclubs run their loudest May through September, so check [when you're coming](/best-time-to-visit-las-vegas) — a November bachelor party is a very different, mostly-indoor weekend.

## Eat before the club, always

The single most common bachelor-party mistake is going to the nightclub hungry at 11pm. Book a real dinner at 8 or 9 — a steakhouse, a big group table, something with substance. You'll drink better, last longer, and not make bad decisions on an empty stomach. Then walk into the club fed.

Most clubs let a table host add your group to the list. If you're not buying a nightclub table, get on the guest list before midnight — after that, the cover and the line both jump.

## Get a driver, skip the valet

Do not valet on a bachelor party. The valet line at 2am on a Saturday can run 45 minutes, and it will end the night on a sour note while everyone stands around. Use rideshare for small hops. For the whole night, a booked driver or a party bus is worth it for a group of eight — one price, no waiting, no one's phone hunting for a surge-priced ride at closing time.

Locals use a handful of limo companies that quote flat rates for the night. Book ahead; the good ones sell out on fight weekends and holidays.

## A sane schedule for two nights

Two nights is the right length. Here's a version that works:

- Friday: land, check in, late lunch, an easy pool afternoon, dinner, then a bar crawl or a lower-key club to warm up.
- Saturday: the big day — dayclub in the afternoon, nap and shower, the steakhouse dinner, then the headline nightclub.
- Sunday: recovery brunch, checkout, done.

Don't stack two nightclub nights back to back. Nobody makes it, and the groom least of all.

## Where to keep it cheaper

You can run a good bachelor weekend without Sky Villa money. Stay [Downtown](/where-to-stay-in-las-vegas) at a place like the Golden Nugget, keep the table minimums low, and rideshare to one Strip dayclub for the marquee afternoon. You trade the walk-everywhere location for cheaper rooms, cheaper drinks, and a Fremont Street night that most groups end up rating higher than the club anyway.

Lock the suite, the pool table, and the dinner first. Everything else you can figure out when you land — start with the [hotel map](/map) to see how close your picks actually sit.''',

    "family-with-kids": '''Vegas with kids works better than most parents expect, as long as you pick the right hotel and plan around two things: the pool and the casino smoke. Get those right and the rest of the city has more for a 9-year-old than you'd think.

## The best hotels for families

Four Strip hotels are built for this. [Excalibur](/hotels/excalibur) is a literal castle with an arcade and a kid-friendly price — the easiest first pick. [Mandalay Bay](/hotels/mandalay-bay) has the best family pool on the Strip: a real sand beach, a wave pool, and a lazy river. Circus Circus runs free circus acts every half hour plus the indoor Adventuredome theme park, which saves any 105-degree afternoon. Resorts World is the newest option, with a pool complex big enough that kids never get bored.

Book a hotel with a pool your kids will actually use. In summer, the pool is the trip — plan on being in it from late morning through the afternoon heat, then heading out once the sun drops.

## Rooms away from the smoke

The casino floor is the one real downside of Vegas with kids. Most Strip hotels still allow smoking on the gaming floor, and you walk through it to reach the elevators. Two ways around it: pick a non-gaming hotel, or pick a room tower far from the casino.

The non-gaming options are the cleanest fix. [Vdara](/hotels/vdara), [Trump International](/hotels/trump-international), and the [Signature at MGM](/hotels/signature-mgm) have no casino at all — no smoke, quieter lobbies, and many rooms with kitchens for cheaper breakfasts. They sit a short walk or tram ride from the action without putting a slot floor between your kids and the pool.

## What to actually do

Beyond the pool, the city has real attractions for kids:

- Shark Reef at Mandalay Bay — a walk-through aquarium with sharks and a tunnel.
- The Discovery Children's Museum downtown — three floors of hands-on exhibits, ideal for under-10s.
- Springs Preserve — desert trails, a small museum, and animal exhibits, away from the Strip.
- Ethel M Chocolate Factory and its cactus garden in Henderson — a free, easy afternoon.
- The Adventuredome at Circus Circus — indoor roller coasters and rides when it's too hot outside.

The [Bellagio fountains](/things-to-do/bellagio-fountains) and the Fremont Street light show are both free and both land well with kids at night.

## Getting around without a meltdown

Distances on the Strip are deceiving — Mandalay Bay to the Bellagio is a 25-minute walk in the heat, which is a lot with a stroller. Use the free trams between the south-end hotels (Mandalay Bay–Luxor–Excalibur, and Bellagio–Aria–Park MGM), rideshare for longer hops, and do your walking early in the morning before the pavement bakes. Our [where-to-stay guide](/where-to-stay-in-las-vegas) breaks down which part of the Strip keeps your walks short.

## When to bring the kids

Summer break lines up with the hottest months — June through August run over 100 degrees most days. That's fine if you commit to a pool hotel and treat mornings and evenings as your outdoor time. If you have flexibility, spring break in March or a fall trip in October gives you 80-degree days and far more comfortable sightseeing. The [best-time guide](/best-time-to-visit-las-vegas) has the month-by-month breakdown.

One booking note: nearly every resort charges a nightly [resort fee](/things-to-do/resort-fees) of $35 to $55 on top of the room, and it usually covers the pool and wifi. Factor it into the comparison so the "cheap" room doesn't surprise you at checkout.''',

    "sports-fans": '''Las Vegas turned into a real sports town fast. The Raiders, the Golden Knights, a Formula 1 race down the Strip, and a UFC home base all landed within a few years, and a Major League Baseball team is on the way. Where you stay depends entirely on which venue you're headed to — the right hotel is a walk, the wrong one is a 30-minute ride in game-day traffic.

## Raiders at Allegiant Stadium

Allegiant Stadium sits just west of the south Strip. The walkable hotels are [Luxor](/hotels/luxor), [Mandalay Bay](/hotels/mandalay-bay), and [Excalibur](/hotels/excalibur) — all a 10-to-15-minute walk over the pedestrian bridge, no rideshare surge, no parking hunt. Mandalay Bay is the closest of the three. Stay here for a Raiders game and you can walk to the stadium and back, which on a sold-out Sunday is worth more than any room upgrade. Full breakdown on our [hotels near Allegiant Stadium](/hotels-near-allegiant-stadium) page.

Rideshare pickup after an NFL game is a mess — the surge is real and the lots empty slowly. Walking beats it every time, so book the location.

## Golden Knights and UFC at T-Mobile Arena

T-Mobile Arena sits behind New York-New York, mid-south Strip. The walkable picks are [MGM Grand](/hotels/mgm-grand), Park MGM, and New York-New York, all connected to the arena by the outdoor Toshiba Plaza. This is where the Golden Knights play and where most big UFC cards land. Stay in this cluster and you walk out of your hotel, cross the plaza, and you're at your seat.

Fight weekends spike hotel rates across the whole city, so book early and check the [best-time guide](/best-time-to-visit-las-vegas) for which weekends fill up.

## Formula 1 down the Strip

The [F1 Las Vegas Grand Prix](/events/formula-1-las-vegas-grand-prix) is different from every other event here — the track is the Strip itself. The circuit runs past Wynn, the Venetian, and the Bellagio, so the best move is to stay inside the track at a hotel with a room facing the circuit. [Wynn](/hotels/wynn), the [Venetian](/hotels/venetian), and the [Cosmopolitan](/hotels/cosmopolitan) all put you trackside with no need to cross closed roads. See our [hotels near the F1 circuit](/hotels-near-f1-circuit) page for the trackside rooms.

F1 weekend is the single biggest rate spike on the Vegas calendar — a trackside room can run four to five times its normal price, and the good ones sell out months ahead. If you want to be there, book early.

## Watching, not attending

Plenty of sports trips here are about watching, not going to a game. The sportsbooks are the draw, and they're open to non-guests. The Circa book downtown is the largest in the world — three stories, a giant screen, stadium seating. On the Strip, the Westgate SuperBook is the old-school giant. Out in the suburbs, the Durango Casino sportsbook is newer and a local favorite for game day without the tourist crush.

March Madness is the peak sportsbook weekend of the year — the first Thursday and Friday fill every book in town. Book a room early and get to your book by mid-morning to claim a seat.

## Quick pick by venue

- Raiders / Allegiant Stadium → Mandalay Bay, Luxor, or Excalibur (walk the bridge).
- Golden Knights or UFC / T-Mobile Arena → MGM Grand, Park MGM, or New York-New York.
- F1 Grand Prix → a trackside room at Wynn, the Venetian, or the Cosmopolitan.
- Watching games → Circa (downtown), Westgate, or Durango sportsbooks.

Use the [hotel map](/map) to see how close each hotel actually sits to your venue before you book, and check [where to stay](/where-to-stay-in-las-vegas) if you want the wider neighborhood breakdown.''',

    "first-timers": '''Your first Vegas trip comes down to a few decisions that are easy to get wrong: where to stay, how long to go, and what to book before you land. Get these right and the Strip is one of the easiest big trips to pull off. Get them wrong and you'll spend the first day fixing avoidable mistakes.

## Stay on the Center Strip

For a first trip, pay for the center. [Cosmopolitan](/hotels/cosmopolitan), Bellagio, Caesars Palace, and the [Venetian](/hotels/venetian) all sit in the walkable core, near the Bellagio fountains and the best pedestrian bridges. From here you can leave your room, see five landmark hotels on foot, and be back without a rideshare.

The temptation is to book a cheaper room at the far south or north end to save $40 a night. Don't, not on your first trip — you'll spend the savings on cabs and burn an hour a day walking in the heat. Our [where-to-stay guide](/where-to-stay-in-las-vegas) breaks down every area if you want to compare.

## Three nights is the sweet spot

Three nights is right for a first trip. Two feels rushed; you land, you're jet-lagged, and it's over. Four or five and the late nights start to catch up with you. Three gives you two full days and nights — enough for the Strip, one show, a pool afternoon, and a night downtown, without the burnout that hits everyone by day four.

## Book shows before you fly

The good shows sell out. Cirque du Soleil's "O" at the Bellagio, the residencies at the Sphere, the headliners at the Colosseum — these move weeks ahead. Buy your show first, then set your hotel dates around it. Working backward from a sold-out show after you've already booked the room is how people end up seeing nothing. Our [shows guide](/things-to-do/best-vegas-shows) covers what's worth it.

## The mistakes every newbie makes

A short list of things first-timers get wrong:

- Driving on the Strip. Never do this. Traffic crawls, parking is a maze, and rideshare or the Monorail is faster and cheaper. If you rent a car for a day trip, valet it and leave it.
- Skipping Fremont Street. Downtown's [Fremont Street Experience](/things-to-do/fremont-street-experience) — the neon canopy, the free shows, the cheaper drinks — is the one thing first-timers skip and later wish they hadn't. Go for a night.
- Underestimating the walk. Hotels look close together and aren't. Mandalay Bay to the Bellagio is 25 minutes on foot.
- Forgetting the resort fee. Nearly every hotel adds $35 to $55 a night on top of the rate. Compare the [all-in price](/things-to-do/resort-fees), not the headline.

## Walk the Strip in the morning

The Strip at 8am is a different place — cool, empty, and easy to photograph without a crowd in every shot. Do your sightseeing walk early, then retreat to a pool or air conditioning through the afternoon heat, and come back out when the sun drops and the neon takes over. This one habit makes a summer trip far more pleasant.

## Getting around

Skip the rental car for a Strip-only trip. Rideshare handles the longer hops, the Monorail runs behind the east-side hotels from the Convention Center down to MGM Grand, and the free trams connect a few south-end resorts. For anything off the Strip — Downtown, Red Rock Canyon, Hoover Dam — rideshare or a [booked tour](/tours) is the move.

Pick your dates with the [best-time guide](/best-time-to-visit-las-vegas), then use the [hotel map](/map) to see exactly where each center-Strip hotel sits. That's the whole first-trip playbook.''',

    "couples": '''A couples trip to Vegas is a different city than the bachelor-party version. Skip the club, book a good dinner and a spa morning, and the Strip turns into one of the better short romantic getaways in the country — fountains, rooftop views, and a lot of it walkable at night.

## Rooms worth the upgrade

Two upgrades are worth the money on a couples trip. A Bellagio fountain-view room puts the water show outside your window every half hour — you can watch it from bed, which is the kind of thing you book once and remember. The [Wynn](/hotels/wynn) Tower Suites come with a separate, quieter pool and a spa that's among the best in the city.

If you'd rather skip the casino entirely, [Vdara](/hotels/vdara) is the pick: no gaming floor, no smoke, a calm lobby, and a rooftop pool, all a two-minute walk from the Bellagio. It's the quiet-luxury option that couples who've done the loud version tend to graduate to.

## Book dinner with a view

The meal is the centerpiece of a couples night here. A few reservations worth planning around: a fountain-view table at a Bellagio restaurant so you catch the water show between courses, the Eiffel Tower restaurant at Paris for the Strip from above, or a quiet high-end room away from the crowds if you want to actually hear each other. Book the reservation before you book the show — the good tables at 8pm fill first.

## Pick a show, skip the club

Vegas shows are what you do instead of the nightclub. The romantic picks: Cirque du Soleil's "O" at the Bellagio, an intimate headliner residency, or "Absinthe" if you want to laugh through a late show. Our [shows guide](/things-to-do/best-vegas-shows) has the current lineup and what's actually worth the ticket. One show a night is plenty — leave time for a slow walk and a drink after.

## A spa morning changes the trip

The move that separates a couples trip from a party trip is a slow morning. Book a spa day — the Wynn, the Aria, and the Waldorf Astoria all run couples treatments — and don't schedule anything before noon. A morning in the spa followed by a late poolside lunch resets the whole trip and is the opposite of the 2am-checkout version of Vegas.

## Free and romantic

You don't have to spend to make it feel like a getaway. The [Bellagio fountains](/things-to-do/bellagio-fountains) run free every half hour and every fifteen minutes after 8pm — the late shows on the lake bridge are a genuine moment. The Conservatory inside the Bellagio changes with the seasons and is free to walk through. And a slow evening stroll from the Bellagio up to the Venetian, fountains on one side and the canal on the other, costs nothing and is most couples' favorite hour of the trip.

## Make it a wedding or honeymoon

Plenty of couples come to Vegas to get married, elope, or honeymoon, and the city makes all three easy. If that's the plan, our [weddings and honeymoons guide](/why-vegas/weddings-honeymoons) covers the chapels, the outdoor permits at Red Rock and Valley of Fire, and the honeymoon hotels.

Pick warm, comfortable dates with the [best-time guide](/best-time-to-visit-las-vegas) — April and October are ideal for patio dinners — and use the [hotel map](/map) to land on a room close to the fountains. That's the couples version of Vegas.''',

    "weddings-honeymoons": '''Getting married in Vegas is genuinely easy — a Clark County license, a chapel slot, and you can be married the same afternoon. The city does about 80,000 weddings a year, so the process is smooth and the options run from a $200 chapel to a red-rock overlook at sunrise. Here's how to pick.

## The license comes first

Before any ceremony, both people go to the Clark County Marriage License Bureau downtown, in person, with a valid ID. No blood test, no waiting period — you can get the license and marry the same day. The bureau keeps long hours, including evenings and weekends, which is why so many late-night ceremonies happen. Do this first; a chapel can't marry you without it.

## The classic chapels

The chapels are the reason people fly here to marry. A few worth knowing:

- A Little White Wedding Chapel — the iconic one, home of the drive-thru "Tunnel of Love." This is the Vegas wedding people picture.
- Graceland Chapel — the original Elvis-officiant chapel, still the most fun version if you want the show.
- Chapel of the Flowers — the polished, photograph-friendly option that reads well with parents and looks good in pictures.

Chapels book slots by the half hour and sell out on weekends and holidays, especially anything with a memorable date. Reserve ahead rather than walking in.

## Outdoor and desert ceremonies

If a chapel isn't your style, the desert around Vegas is the alternative. Red Rock Canyon and Valley of Fire State Park both allow permitted ceremonies against red-sandstone backdrops — you book a permit and usually a photographer who knows the spots. The Neon Museum's Boneyard, full of old Vegas signs, is the offbeat urban option for couples who want something that only exists here.

These take more planning than a chapel — permits, a photographer, and timing around the light — but the photos are unlike anything you'll get indoors. Come in spring or fall; a July noon in the desert is brutal for a ceremony. The [best-time guide](/best-time-to-visit-las-vegas) has the comfortable months.

## Where to honeymoon after

Once you're married, the honeymoon hotels are the same short list of quiet-luxury rooms couples book anyway. The [Wynn](/hotels/wynn) Tower Suites come with the city's best spa. The Waldorf Astoria (formerly the Mandarin) is non-gaming, calm, and adults-lean, with a sky-high lobby bar. Crockfords at Resorts World is the newest luxury tower on the Strip. Any of the three gives you a room away from the casino crush for the nights after the ceremony.

## Make it a full couples trip

A wedding weekend is better with a couples itinerary wrapped around it — a fountain-view dinner, a show instead of a club, and a slow spa morning. Our [couples guide](/why-vegas/couples) has those picks, and most of them pair naturally with a chapel afternoon.

## A simple plan

- Get the marriage license downtown, in person, day-of or the day before.
- Book the chapel slot or the outdoor permit ahead — weekends fill.
- Reserve a honeymoon room away from the casino floor.
- Plan the ceremony for a comfortable month, not a July afternoon.

Use the [hotel map](/map) to keep your chapel, dinner, and room close together, and read [where to stay](/where-to-stay-in-las-vegas) to pick the right stretch of the Strip for the weekend.''',

    "shows-residencies": '''The smartest way to plan a show trip to Vegas is backwards: pick the show first, then book the dates it's playing, then book the hotel attached to the venue. Residencies run on set nights, so locking your dates to your show keeps you from flying in the week your headliner is dark.

## Stay at the venue's hotel

Every big Vegas venue is attached to a hotel, and staying there means you walk to your seat instead of fighting post-show rideshare traffic. The pairings worth knowing:

- The [Sphere](/things-to-do/sphere) — stay at the [Venetian](/hotels/venetian) or the [Palazzo](/hotels/palazzo), both connected by a walkway. The Sphere sits right behind them.
- The Colosseum at Caesars Palace — stay at [Caesars](/hotels/caesars-palace). The theater is inside the hotel.
- Dolby Live at Park MGM — stay at Park MGM or New York-New York next door.
- T-Mobile Arena (the big concerts) — stay at [MGM Grand](/hotels/mgm-grand) or New York-New York, both a short walk across the plaza.

Post-show, a walkable room is worth more than a nicer one a rideshare away. Fifteen thousand people leaving the Sphere at once is not the moment to be hunting a surge-priced car.

## The Sphere is its own thing

The Sphere changed what a Vegas show can be. The 366-foot sphere behind the Venetian runs two kinds of nights: the immersive "Postcard from Earth" experience during the day and early evening, and concert residencies — the Eagles, U2's run, Dead & Company, Anyma — at night. Either way, it's a venue unlike anything else, and it's the one show first-timers should build a trip around. Our [Sphere guide](/things-to-do/sphere) covers what's playing and where to sit.

## Cirque and the long-running shows

Beyond the residencies, Vegas has a bench of shows that run year-round, so your dates are flexible. Cirque du Soleil alone has several — "O" at the Bellagio (the water show), "Mystère" at Treasure Island, "KÀ" at MGM. "Absinthe" at Caesars is the raunchy, funny late-night pick. These don't require date-planning the way a residency does; you can catch them any week. Our [full shows guide](/things-to-do/best-vegas-shows) ranks what's worth the ticket.

## Buy before you book the hotel

The order matters. Popular residency nights and the best Cirque seats sell out weeks ahead, and prices climb as the date fills. Buy the ticket first. Then set your hotel dates to match — flying in for a Sphere trip only to find your act is dark that week is the avoidable mistake here.

One resale tip: for concerts that don't sell out, the resale market often drops below face value in the last 90 minutes before curtain. If your dates are set and the show has open seats, waiting can pay off — though for a must-see residency, buy early and don't gamble on it.

## Build the trip around the calendar

Because residencies cluster on certain weekends, the show calendar can decide your dates for you. If you're flexible on timing, cross-check the [best-time guide](/best-time-to-visit-las-vegas) so you land on comfortable weather and reasonable rates as well as the right show nights. Then use the [hotel map](/map) to book the room closest to your venue.''',

    "conventions": '''Vegas runs on conventions — CES alone brings over 100,000 people every January — and the one thing that decides your week is how far your hotel is from your show floor. The city has four main convention venues, spread miles apart, so "on the Strip" isn't specific enough. Match your hotel to your venue and you walk to the floor; miss it and you're in a rideshare line every morning.

## Las Vegas Convention Center (LVCC)

The LVCC on Paradise Road is the biggest venue in town and hosts CES and most of the mega-shows. The closest hotels are Westgate (attached by its own walkway), the Las Vegas Hilton, and the north-Strip resorts — [Wynn](/hotels/wynn), [Encore](/hotels/encore), and Resorts World — all a short ride or the Monorail away. Full breakdown on our [hotels near the Convention Center](/hotels-near-convention-center) page.

The Monorail is the key here: it runs behind the east-side Strip hotels from the Convention Center station down to MGM Grand, which skips the traffic entirely during a big show. If your event is at the LVCC, staying near a Monorail stop is worth more than staying on the Strip itself.

## Mandalay Bay Convention Center

Mandalay Bay's convention space anchors the south end. Stay at [Mandalay Bay](/hotels/mandalay-bay), [Luxor](/hotels/luxor), or Delano and you're connected by tram or a covered walk — no rideshare needed all week. This is one of the easiest venues to stay near, because the three connected hotels cover every budget from Luxor's value rooms up to Delano's suites.

## Venetian Expo

The Venetian Expo (the old Sands Expo) sits behind the [Venetian](/hotels/venetian) and [Palazzo](/hotels/palazzo), and staying in either puts you an indoor walk from the floor. It's the most comfortable convention stay on the Strip — you never step outside to reach your session, which in July or during F1 traffic is a real advantage.

## Caesars Forum

Caesars Forum sits behind the Linq, between Caesars Palace and the Strip. The walkable hotels are Harrah's, the Linq, and the Flamingo, all a few minutes on foot. Caesars Palace itself is a slightly longer but covered walk. Stay in this cluster and you're at the Forum in ten minutes without a car.

## Book early and expect high rates

Convention weeks are the most expensive, most sold-out weeks of the year. CES in early January, and the big shows through spring and fall, push rates up and fill rooms months ahead. Book as soon as your dates are set. If your company isn't covering a room block, our [where-to-stay guide](/where-to-stay-in-las-vegas) helps you find a nearby hotel that isn't priced for the show.

## A few business-travel notes

- Pick a hotel with fast in-room wifi and a real desk — the non-gaming towers like the Signature at MGM and Vdara are quieter for calls between sessions.
- The Monorail is faster than rideshare during any big convention. Buy a multi-day pass.
- Build in a day. Vegas is a good place to add 24 hours to a work trip — a show, a pool afternoon, or a [Grand Canyon day trip](/tours) turns a convention into a real visit.

Use the [hotel map](/map) to see exactly how far your hotel sits from your venue before you book.''',
}

def page_why(slug, title, desc, h1, body):
    jsonld = f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}},
  {{"@type":"ListItem","position":2,"name":"Why Vegas","item":"{SITE}/why-vegas"}},
  {{"@type":"ListItem","position":3,"name":{json.dumps(h1)},"item":"{SITE}/why-vegas/{slug}"}}
]}}
</script>"""
    body_html = md_to_html(WHY_BODY[slug]) if slug in WHY_BODY else f'<p style="font-size:18px; line-height:1.8;">{body}</p>'
    html = head(title, desc, f"/why-vegas/{slug}", extra_jsonld=jsonld) + HEADER + f"""
<section class="section">
  <div class="container" style="max-width:820px;">
    <div class="section-head">
      <span class="pill pill-yellow">WHY VEGAS</span>
      <h1 class="headline-glow" style="font-size:clamp(40px,6vw,72px); margin:12px 0 8px;">{h1.upper()}</h1>
      <p class="kicker">{desc}</p>
    </div>
    <div class="guide">
{body_html}
    </div>
    <div style="text-align:center; margin-top:36px;">
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
  <h2 style="font-size:28px; margin:0;">THE VEGAS HUB — Las Vegas Packing List</h2>
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
      <p>We're a small team based in Las Vegas. We've been coming here since the mid-1990s and have lived here for many years now — through the explosion of the megaresorts, the post-9/11 rebuild, the Cosmo/Aria/Sphere wave, and every pool, buffet, and Cirque show along the way.</p>
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
      <label for="c-name">Name <span style="color:var(--neon-pink);">*</span></label>
      <input id="c-name" name="name" type="text" maxlength="120" required>

      <label for="c-email">Email <span style="color:var(--neon-pink);">*</span></label>
      <input id="c-email" name="email" type="email" maxlength="254" required>

      <label for="c-phone">Phone <span style="color:var(--neon-pink);">*</span></label>
      <input id="c-phone" name="phone" type="tel" maxlength="24" required autocomplete="tel" inputmode="tel" placeholder="(702) 555-1234">

      <label for="c-subject">Subject <span style="color:var(--neon-pink);">*</span></label>
      <input id="c-subject" name="subject" type="text" maxlength="180" required>

      <label for="c-message">Message <span style="color:var(--neon-pink);">*</span></label>
      <textarea id="c-message" name="message" rows="6" maxlength="5000" required></textarea>

      <label style="display:flex; gap:12px; align-items:flex-start; text-transform:none; letter-spacing:normal; font-family:'Inter',sans-serif; color:var(--text-muted); font-size:13px; line-height:1.55; margin-top:8px;">
        <input id="c-sms" name="sms_consent" type="checkbox" required style="min-width:18px; margin-top:4px; accent-color:var(--neon-cyan); width:auto; margin-bottom:0;">
        <span>I agree to receive a text message from TheVegasHub regarding this specific inquiry. <em>Standard message &amp; data rates apply.</em></span>
      </label>

      <!-- Honeypot -->
      <input type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute; left:-10000px;">

      <button type="submit" class="btn btn-cyan" style="width:100%; margin-top:16px;">SEND MESSAGE</button>
      <p id="c-status" style="margin-top:12px; font-size:14px; min-height:20px;"></p>

      <p style="font-size:11px; color:var(--text-muted); margin-top:16px; line-height:1.5;">
        Fields marked <span style="color:var(--neon-pink);">*</span> are required. Your info is used only to reply to your request and is never sold. See our <a href="/privacy" style="color:var(--neon-cyan);">Privacy Policy</a>.
      </p>
    </form>
  </div>
</section>

<script>
document.getElementById('contactForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const f = e.target;
  const status = document.getElementById('c-status');

  // Client-side required check (we still validate server-side)
  if (!f.name.value.trim() || !f.email.value.trim() || !f.phone.value.trim() || !f.subject.value.trim() || !f.message.value.trim()) {
    status.style.color = 'var(--neon-pink)';
    status.textContent = 'Please fill in all required fields.';
    return;
  }
  if (!f.sms_consent.checked) {
    status.style.color = 'var(--neon-pink)';
    status.textContent = 'Please agree to the SMS consent to continue.';
    return;
  }

  status.style.color = 'var(--text-muted)';
  status.textContent = 'Sending…';
  const body = {
    name: f.name.value,
    email: f.email.value,
    phone: f.phone.value,
    subject: f.subject.value,
    message: f.message.value,
    sms_consent: f.sms_consent.checked,
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

# ---------------------------- HOTEL MAP ---------------------------- #

# (x%, y%) positions on the schematic map, keyed by hotel slug. The stage is a
# VERTICAL corridor: Fremont/Downtown cluster along the top (north), the Strip as
# a central ribbon running north->south, and off-Strip hotels offset to the west
# (left). Coordinates are the same 0-100 percentage space the inline SVG uses, so
# the HTML dots and the SVG backdrop line up exactly (preserveAspectRatio="none").
MAP_POSITIONS = {
    # Fremont Street / Downtown — top band (north)
    "plaza-downtown":         (29, 6),
    "golden-nugget-downtown": (50, 9),
    "fremont-hotel":          (70, 6),
    # Strip — north to south (east side = right, west side = left)
    "crockfords":             (40, 19),
    "encore":                 (61, 22),
    "wynn":                   (63, 26),
    "trump-international":     (37, 28),
    "treasure-island":        (40, 31),
    "venetian":               (60, 34),
    "palazzo":                (63, 38),
    "caesars-palace":         (38, 44),
    "flamingo":               (62, 46),
    "bellagio":               (39, 50),
    "cosmopolitan":           (61, 53),
    "vdara":                  (34, 56),
    "aria":                   (42, 59),
    "signature-mgm":          (63, 67),
    "mgm-grand":              (60, 71),
    "excalibur":              (40, 76),
    "luxor":                  (39, 84),
    "mandalay-bay":           (42, 92),
    # Off-Strip — west column
    "otonomus":               (16, 38),
    "westgate-flamingo-bay":  (13, 46),
    "rio":                    (21, 44),
    "palms":                  (16, 55),
    "palms-place":            (23, 57),
}

MAP_ZONE = {"strip": "zone-strip", "off-strip": "zone-off", "downtown": "zone-downtown"}

def page_map():
    """Interactive stylized neon map of the Strip + Fremont hotels."""
    map_hotels = [
        h for h in HOTELS
        if h.get("area") in ("strip", "off-strip", "downtown") and h["slug"] in MAP_POSITIONS
    ]

    dots = ""
    for h in map_hotels:
        x, y = MAP_POSITIONS[h["slug"]]
        link = h.get("link", "")
        is_todo = (not link) or link.startswith("TODO")
        book_href = link if not is_todo else "/contact"
        book_label = "DETAILS →" if is_todo else "BOOK NOW →"
        book_rel = 'rel="nofollow sponsored noopener" target="_blank"' if book_href.startswith("http") else ""
        zone = MAP_ZONE.get(h["area"], "zone-strip")
        below = " pop-below" if y < 16 else ""
        name = h["name"]
        dots += f"""      <div class="map-dot {zone}{below}" style="left:{x}%; top:{y}%;" role="button" tabindex="0" aria-label="{name}">
        <span class="map-dot-mark"></span>
        <span class="map-pop">
          <span class="map-pop-name">{name}</span>
          <a class="map-pop-book" href="{book_href}" {book_rel}>{book_label}</a>
        </span>
      </div>
"""

    # Soft resort-parcel glow behind each dot (aligned to the same coordinates).
    blocks = ""
    for h in map_hotels:
        x, y = MAP_POSITIONS[h["slug"]]
        blocks += f'      <span class="map-block {MAP_ZONE.get(h["area"], "zone-strip")}" style="left:{x}%; top:{y}%;"></span>\n'

    # Deterministic scatter of faint "city lights" for the night backdrop.
    import random as _random
    _rng = _random.Random(1971)
    _palette = ["#00eaff", "#ff2eb0", "#bf00ff", "#ffe600", "#ffffff"]
    specks = ""
    for _ in range(72):
        sx = round(_rng.uniform(4, 96), 1)
        sy = round(_rng.uniform(4, 96), 1)
        rad = round(_rng.uniform(0.3, 0.9), 2)
        col = _rng.choice(_palette)
        op = round(_rng.uniform(0.06, 0.20), 2)
        specks += f'<circle cx="{sx}" cy="{sy}" r="{rad}" fill="{col}" opacity="{op}"/>'

    n_strip = sum(1 for h in map_hotels if h["area"] == "strip")
    n_off = sum(1 for h in map_hotels if h["area"] == "off-strip")
    n_dt = sum(1 for h in map_hotels if h["area"] == "downtown")

    jsonld_map = f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}},
  {{"@type":"ListItem","position":2,"name":"Hotel Map","item":"{SITE}/map"}}
]}}
</script>"""

    style = """
<style>
  .map-stage{ position:relative; width:100%; max-width:600px; margin:0 auto; aspect-ratio:5 / 7;
    background:
      radial-gradient(120% 70% at 50% 0%, rgba(191,0,255,.14) 0%, rgba(10,0,20,0) 55%),
      radial-gradient(90% 55% at 50% 100%, rgba(0,234,255,.08) 0%, rgba(10,0,20,0) 60%),
      linear-gradient(180deg, #05010e 0%, #0a0016 100%);
    border:1px solid var(--card-border); border-radius:16px; overflow:visible; touch-action:manipulation; }
  .map-svg{ position:absolute; inset:0; width:100%; height:100%; z-index:1; }
  .svg-fremont{ stroke:var(--neon-pink); stroke-width:2.5; stroke-linecap:round; vector-effect:non-scaling-stroke;
    opacity:.6; filter:drop-shadow(0 0 5px var(--neon-pink)); }
  /* Las Vegas Blvd — illustrated road */
  .road-bed{ fill:rgba(3,2,10,.55); }
  .road-edge{ stroke:var(--neon-cyan); stroke-width:1.5; vector-effect:non-scaling-stroke; opacity:.45;
    filter:drop-shadow(0 0 4px var(--neon-cyan)); }
  .road-center{ stroke:rgba(255,230,0,.55); stroke-width:1.2; vector-effect:non-scaling-stroke; stroke-dasharray:2.5 3.5; }
  .cross-st{ stroke:rgba(245,245,245,.16); stroke-width:1; vector-effect:non-scaling-stroke; stroke-dasharray:1 2; }
  .cross-label{ position:absolute; right:2%; transform:translateY(-50%); z-index:2; font-family:'Oswald',sans-serif;
    font-weight:500; font-size:9px; letter-spacing:.1em; color:rgba(245,245,245,.4); white-space:nowrap; pointer-events:none; }
  /* soft resort-parcel glow behind each dot */
  .map-block{ position:absolute; z-index:2; width:34px; height:22px; transform:translate(-50%,-50%);
    border-radius:6px; filter:blur(4px); opacity:.13; pointer-events:none; }
  .map-block.zone-strip{ background:var(--neon-cyan); }
  .map-block.zone-off{ background:var(--neon-purple); }
  .map-block.zone-downtown{ background:var(--neon-pink); }
  .map-label{ position:absolute; z-index:2; font-family:'Bebas Neue','Oswald',sans-serif; letter-spacing:.18em;
    font-size:12px; color:rgba(245,245,245,.55); white-space:nowrap; pointer-events:none; }
  .label-fremont{ top:3%; left:50%; transform:translateX(-50%); color:rgba(255,46,176,.75); }
  .label-strip{ top:52%; left:50%; transform:translate(-50%,-50%) rotate(-90deg); transform-origin:center;
    color:rgba(0,234,255,.6); }
  .map-dot{ position:absolute; z-index:3; width:16px; height:16px; transform:translate(-50%,-50%);
    cursor:pointer; outline:none; }
  .map-dot-mark{ display:block; width:16px; height:16px; border-radius:50%; border:2px solid rgba(255,255,255,.85);
    animation:mapPulse 2.6s ease-in-out infinite; }
  .zone-strip .map-dot-mark{ background:var(--neon-cyan); box-shadow:0 0 6px var(--neon-cyan),0 0 14px rgba(0,234,255,.7); }
  .zone-off .map-dot-mark{ background:var(--neon-purple); box-shadow:0 0 6px var(--neon-purple),0 0 14px rgba(191,0,255,.7); }
  .zone-downtown .map-dot-mark{ background:var(--neon-pink); box-shadow:0 0 6px var(--neon-pink),0 0 14px rgba(255,46,176,.7); }
  @keyframes mapPulse{ 0%,100%{ transform:scale(1); } 50%{ transform:scale(1.28); } }
  .map-dot:hover, .map-dot:focus-visible, .map-dot:focus-within, .map-dot.open{ z-index:60; }
  .map-dot:focus-visible .map-dot-mark{ outline:2px solid #fff; outline-offset:3px; }
  .map-pop{ position:absolute; left:50%; bottom:calc(100% + 8px); transform:translate(-50%,4px);
    min-width:160px; max-width:220px; background:rgba(5,0,12,.97); border:1px solid var(--neon-cyan);
    border-radius:10px; padding:12px 14px; box-shadow:0 0 20px rgba(0,234,255,.35); text-align:center;
    opacity:0; visibility:hidden; transition:opacity .15s ease, transform .15s ease; z-index:70; }
  .pop-below .map-pop{ bottom:auto; top:calc(100% + 8px); }
  .zone-off .map-pop{ border-color:var(--neon-purple); box-shadow:0 0 20px rgba(191,0,255,.35); }
  .zone-downtown .map-pop{ border-color:var(--neon-pink); box-shadow:0 0 20px rgba(255,46,176,.35); }
  .map-dot:hover .map-pop, .map-dot:focus-within .map-pop, .map-dot.open .map-pop{
    opacity:1; visibility:visible; transform:translate(-50%,0); }
  .map-pop-name{ display:block; font-family:'Oswald',sans-serif; font-weight:700; font-size:13px; line-height:1.3;
    color:#fff; margin-bottom:10px; }
  .map-pop-book{ display:inline-block; font-family:'Bebas Neue',sans-serif; letter-spacing:.06em; font-size:14px;
    color:#000 !important; background:var(--neon-cyan); border-radius:6px; padding:7px 14px; text-decoration:none; }
  .map-pop-book:hover{ background:#fff; color:#000 !important; }
  .map-legend{ display:flex; flex-wrap:wrap; justify-content:center; gap:18px; margin:24px 0 0;
    font-size:13px; color:var(--text-muted); }
  .map-legend span{ display:inline-flex; align-items:center; gap:7px; }
  .map-legend i{ width:12px; height:12px; border-radius:50%; display:inline-block; }
  .lg-strip{ background:var(--neon-cyan); box-shadow:0 0 6px var(--neon-cyan); }
  .lg-off{ background:var(--neon-purple); box-shadow:0 0 6px var(--neon-purple); }
  .lg-downtown{ background:var(--neon-pink); box-shadow:0 0 6px var(--neon-pink); }
  @media (max-width:560px){
    .map-stage{ max-width:100%; aspect-ratio:4 / 7; }
    .map-pop{ min-width:140px; }
    .map-label{ font-size:10px; }
    .map-block{ width:26px; height:16px; }
    .cross-label{ font-size:8px; }
  }
</style>
"""

    html = head(
        "Las Vegas Strip &amp; Fremont Hotel Map — Interactive Hotel Finder | TheVegasHub",
        "Interactive map of Las Vegas Strip, off-Strip, and Fremont Street hotels. Tap or hover any hotel to see its name and book with member rates.",
        "/map",
        extra_jsonld=jsonld_map,
    ) + style + HEADER + f"""
<section class="section">
  <div class="container">
    <div style="text-align:center; max-width:720px; margin:0 auto 8px;">
      <span class="pill pill-cyan">EXPLORE</span>
      <h1 class="headline-glow" style="font-size:clamp(40px,7vw,72px); line-height:1.05; margin:14px 0 12px;">HOTEL MAP</h1>
      <p class="sub" style="margin:0 auto;">The Las Vegas Strip, off-Strip, and Fremont Street at a glance. Tap or hover any glowing dot for the hotel name and a direct booking link.</p>
    </div>

    <div id="map-stage" class="map-stage">
      <svg class="map-svg" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
        <g class="map-specks">{specks}</g>
        <rect class="road-bed" x="45" y="14.5" width="10" height="82.5"></rect>
        <line class="road-edge" x1="45" y1="14.5" x2="45" y2="97"></line>
        <line class="road-edge" x1="55" y1="14.5" x2="55" y2="97"></line>
        <line class="road-center" x1="50" y1="15" x2="50" y2="96"></line>
        <line class="cross-st" x1="18" y1="18" x2="82" y2="18"></line>
        <line class="cross-st" x1="20" y1="31" x2="80" y2="31"></line>
        <line class="cross-st" x1="14" y1="47" x2="86" y2="47"></line>
        <line class="cross-st" x1="20" y1="74" x2="80" y2="74"></line>
        <line class="svg-fremont" x1="22" y1="8" x2="78" y2="8"></line>
      </svg>
{blocks}      <span class="map-label label-fremont">◄ FREMONT ST ►</span>
      <span class="map-label label-strip">LAS VEGAS BLVD</span>
      <span class="cross-label" style="top:18%;">W SAHARA</span>
      <span class="cross-label" style="top:31%;">SPRING MTN</span>
      <span class="cross-label" style="top:47%;">FLAMINGO</span>
      <span class="cross-label" style="top:74%;">TROPICANA</span>
{dots}    </div>

    <div class="map-legend">
      <span><i class="lg-strip"></i> Strip ({n_strip})</span>
      <span><i class="lg-off"></i> Off-Strip ({n_off})</span>
      <span><i class="lg-downtown"></i> Fremont / Downtown ({n_dt})</span>
    </div>

    <div style="text-align:center; margin-top:32px;">
      <a class="btn btn-ghost" href="/hotels">Browse all hotels</a>
    </div>
  </div>
</section>

<script>
(function(){{
  var stage = document.getElementById('map-stage');
  if(!stage) return;
  function closeAll(except){{
    var open = stage.querySelectorAll('.map-dot.open');
    for(var i=0;i<open.length;i++){{ if(open[i]!==except) open[i].classList.remove('open'); }}
  }}
  function toggle(dot){{
    var was = dot.classList.contains('open');
    closeAll(dot);
    dot.classList.toggle('open', !was);
  }}
  stage.addEventListener('click', function(e){{
    if(e.target.closest('.map-pop-book')) return;   // let the booking link work
    var dot = e.target.closest('.map-dot');
    if(dot){{ e.stopPropagation(); toggle(dot); }}
    else {{ closeAll(null); }}
  }});
  stage.addEventListener('keydown', function(e){{
    var dot = e.target.closest('.map-dot');
    if(dot && (e.key==='Enter' || e.key===' ')){{ e.preventDefault(); toggle(dot); }}
    if(e.key==='Escape'){{ closeAll(null); }}
  }});
  document.addEventListener('click', function(e){{ if(!e.target.closest('#map-stage')) closeAll(null); }});
}})();
</script>
""" + FOOTER
    write("map/index.html", html)

# ---------------------------- EVENTS ---------------------------- #

HOTELS_BY_SLUG = {h["slug"]: h for h in HOTELS}

# Third-party disclaimer shown on the events index and every event page.
EVENTS_DISCLAIMER = """
    <div class="card" style="padding:22px 24px; background:rgba(255,230,0,.06); border-color:var(--neon-yellow); margin:0 0 32px;">
      <span class="pill">PLEASE NOTE</span>
      <p style="margin:12px 0 0; color:var(--text-muted); line-height:1.7; font-size:14px;">
        Every event listed here is organized and operated by an independent third party. TheVegasHub is
        <strong>not affiliated with, endorsed by, or responsible for</strong> any event, organizer, or venue shown.
        Dates, times, locations, pricing, and availability are set by the event organizers and are
        <strong>subject to change or cancellation at any time without notice</strong>. Always confirm the details
        directly with the official event organizer before making travel plans. Hotel links are affiliate links &mdash;
        see our <a href="/disclosure">Disclosure</a>.
      </p>
    </div>"""

# Booking CTA (user-requested link to thevegashub.com).
EVENTS_BOOK_CTA = """
    <div class="card" style="padding:32px; text-align:center; background:rgba(0,234,255,.06); border-color:var(--neon-cyan); margin-top:44px;">
      <h2 class="headline neon-cyan" style="font-size:clamp(24px,4vw,34px); margin:0 0 10px;">Need a hotel for the trip?</h2>
      <p style="margin:0 0 20px; color:var(--text-muted);">Compare Las Vegas, Henderson, Laughlin, and Mesquite hotels with member-rate booking links.</p>
      <a class="btn btn-cyan" href="https://thevegashub.com" style="font-size:16px; padding:16px 36px;">Book a hotel at TheVegasHub.com →</a>
    </div>"""

EVENTS = [
    {
        "slug": "las-vegas-triathlon",
        "name": "Las Vegas Triathlon",
        "pill": "TRIATHLON",
        "date": "October 10, 2026",
        "start_iso": "2026-10-10", "end_iso": "2026-10-10",
        "city": "Boulder City, NV", "region": "Boulder City",
        "admission": "Free for spectators",
        "summary": "A multisport competition utilizing Boulder Beach at Lake Mead as a swim-to-bike transition hub. Spectators gather at the finish-line race village to watch participants navigate the final miles along the paved River Mountain Loop trail.",
        "best_for": "Endurance sports fans and families supporting participants.",
        "planning_notes": [
            "Wave starts begin at 6:30 AM &mdash; arrive by 6:00 AM to secure a viewing spot on the rocky shoreline.",
            "Sturdy, closed-toe footwear is required for navigating the gravel and rock surfaces of Boulder Beach.",
            "There is no natural shade at the race village; bring portable umbrellas and high-SPF sunscreen.",
        ],
        "ada": "The race village sits on paved lots and hard-packed dirt; accessible parking provides paved access to the transition area.",
        "near_venue": "Closest to the venue: Boulder Dam Hotel, Boulder City Inn, and Best Western Hoover Dam Hotel in Boulder City. For casino-resort stays with member-rate booking, the Henderson resorts below are roughly 25 minutes away.",
        "hotels_heading": "Where to Stay Near Boulder City",
        "hotel_slugs": ["green-valley-ranch", "m-resort", "south-point"],
    },
    {
        "slug": "laughlin-desert-classic",
        "name": "Laughlin Desert Classic",
        "pill": "OFF-ROAD RACE",
        "date": "October 15–19, 2026",
        "start_iso": "2026-10-15", "end_iso": "2026-10-19",
        "city": "Laughlin, NV", "region": "Laughlin",
        "admission": "Ticketed; pit access may require a separate fee or signed waiver",
        "summary": "An off-road championship race featuring trophy trucks and UTVs on a sandy, multi-lap circuit. The layout lets fans watch technical jumps from tiered ridge-line viewing areas and mechanical repairs in the nearby pit zones.",
        "best_for": "Action sports fans and off-road enthusiasts.",
        "hotels_heading": "Where to Stay in Laughlin",
        "hotel_slugs": ["aquarius-laughlin", "edgewater-laughlin", "harrahs-laughlin", "tropicana-laughlin"],
    },
    {
        "slug": "hump-n-bump",
        "name": "Hump N Bump",
        "pill": "OFF-ROAD",
        "date": "October 30 – November 1, 2026",
        "start_iso": "2026-10-30", "end_iso": "2026-11-01",
        "city": "Moapa Valley (Logandale), NV", "region": "Logandale",
        "admission": "Ticketed trail access; fairgrounds staging area is free",
        "summary": "An off-road gathering at the Clark County Fairgrounds where 4×4 vehicles navigate rock obstacles in the Logandale Trails. Spectators use sandstone ridges as natural platforms to watch drivers tackle technical ledges and deep sand washes.",
        "best_for": "Off-road enthusiasts and fans of technical rock crawling.",
        "near_venue": "Logandale sits about 45 minutes northeast of the Strip and roughly the same from Mesquite. The Mesquite resorts below make an easy base with member-rate booking.",
        "hotels_heading": "Where to Stay Near Logandale",
        "hotel_slugs": ["casablanca-mesquite", "virgin-river-mesquite", "eureka-mesquite"],
    },
    {
        "slug": "formula-1-las-vegas-grand-prix",
        "name": "Formula 1 Las Vegas Grand Prix",
        "pill": "FORMULA 1",
        "date": "November 19–21, 2026",
        "start_iso": "2026-11-19", "end_iso": "2026-11-21",
        "city": "Las Vegas, NV", "region": "Las Vegas",
        "admission": "Ticketed; tiered grandstand seating and luxury hospitality packages",
        "summary": "An international street race utilizing a 3.8-mile circuit through the Las Vegas Strip. The evening event lets spectators in grandstand zones track cars navigating 17 technical turns amid the resort corridor.",
        "best_for": "International racing fans and marquee-event seekers.",
        "hotels_heading": "Where to Stay on the Strip",
        "hotel_slugs": ["bellagio", "caesars-palace", "cosmopolitan", "venetian"],
    },
]

def _event_hotels_grid(e):
    ev_hotels = [HOTELS_BY_SLUG[s] for s in e["hotel_slugs"] if s in HOTELS_BY_SLUG]
    return '<div class="grid grid-3">\n' + "".join(hotel_card(h) for h in ev_hotels) + "\n    </div>"

def page_event(e):
    ev_schema = {
        "@context": "https://schema.org", "@type": "Event",
        "name": e["name"], "startDate": e["start_iso"], "endDate": e["end_iso"],
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": {"@type": "Place", "name": e["city"],
                     "address": {"@type": "PostalAddress", "addressLocality": e["region"],
                                 "addressRegion": "NV", "addressCountry": "US"}},
        "description": e["summary"],
        "organizer": {"@type": "Organization", "name": "Independent third-party event organizer"},
        "image": f"{SITE}/images/og/og-default.jpg",
    }
    breadcrumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": "Events", "item": f"{SITE}/events"},
        {"@type": "ListItem", "position": 3, "name": e["name"], "item": f"{SITE}/events/{e['slug']}"},
    ]}
    jsonld = ('<script type="application/ld+json">' + json.dumps(ev_schema) + '</script>\n'
              '<script type="application/ld+json">' + json.dumps(breadcrumb) + '</script>')

    notes_html = ""
    if e.get("planning_notes"):
        lis = "".join(f'<li style="margin-bottom:10px;">{n}</li>' for n in e["planning_notes"])
        notes_html = f"""
    <div class="card" style="padding:28px; margin:24px 0;">
      <span class="pill pill-cyan">PLANNING NOTES</span>
      <ul style="margin:14px 0 0; padding-left:20px; color:var(--text-muted); line-height:1.6;">{lis}</ul>
    </div>"""

    ada_html = ""
    if e.get("ada"):
        ada_html = f"""
    <div class="card" style="padding:22px 24px; margin:0 0 24px;">
      <span class="pill">ACCESSIBILITY</span>
      <p style="margin:12px 0 0; color:var(--text-muted); line-height:1.7;">{e['ada']}</p>
    </div>"""

    near_html = f'<p style="color:var(--text-muted); font-size:14px; margin:0 0 20px;">{e["near_venue"]}</p>' if e.get("near_venue") else ""

    html = head(
        f"{e['name']} — {e['date']} | TheVegasHub Events",
        f"{e['name']} on {e['date']} in {e['city']}. {e['summary'][:110]}",
        f"/events/{e['slug']}",
        extra_jsonld=jsonld,
    ) + HEADER + f"""
<section class="section">
  <div class="container" style="max-width:900px;">
    <div class="section-head">
      <span class="pill pill-pink">{e['pill']}</span>
      <h1 class="headline-glow" style="font-size:clamp(36px,6vw,64px); line-height:1.05; margin:12px 0 10px;">{e['name'].upper()}</h1>
      <p class="kicker">{e['date']} &middot; {e['city']} &middot; {e['admission']}</p>
    </div>
{EVENTS_DISCLAIMER}
    <p style="font-size:18px; line-height:1.8; margin:0 0 18px;">{e['summary']}</p>
    <p style="font-size:16px; line-height:1.7; margin:0 0 8px;"><strong class="neon-cyan">Best for:</strong> {e['best_for']}</p>
{notes_html}
{ada_html}
    <h2 class="headline neon-cyan" style="font-size:clamp(24px,3.5vw,34px); margin:40px 0 8px;">{e['hotels_heading']}</h2>
    {near_html}
    {_event_hotels_grid(e)}
{EVENTS_BOOK_CTA}
    <div style="text-align:center; margin-top:32px;">
      <a class="btn btn-ghost" href="/events">← All Upcoming Events</a>
    </div>
  </div>
</section>
""" + FOOTER
    write(f"events/{e['slug']}.html", html)

def page_events_index():
    cards = ""
    for e in EVENTS:
        cards += f"""      <a class="card" href="/events/{e['slug']}" style="padding:28px; text-decoration:none;">
        <span class="pill pill-pink">{e['pill']}</span>
        <h3 class="headline" style="font-size:24px; margin:12px 0 6px;">{e['name']}</h3>
        <p class="display neon-cyan" style="font-size:13px; margin:0 0 4px;">{e['date']}</p>
        <p style="color:var(--text-muted); font-size:13px; margin:0 0 12px;">{e['city']} &middot; {e['admission']}</p>
        <p style="color:var(--text-muted); margin:0; line-height:1.6;">{e['summary'][:150]}&hellip;</p>
        <span class="display neon-cyan" style="font-size:12px; display:block; margin-top:14px;">Event details &rarr;</span>
      </a>
"""

    item_list = {"@context": "https://schema.org", "@type": "ItemList",
                 "name": "Upcoming Las Vegas Events",
                 "itemListElement": [
                     {"@type": "ListItem", "position": i + 1, "name": e["name"], "url": f"{SITE}/events/{e['slug']}"}
                     for i, e in enumerate(EVENTS)]}
    breadcrumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": "Events", "item": f"{SITE}/events"}]}
    jsonld = ('<script type="application/ld+json">' + json.dumps(item_list) + '</script>\n'
              '<script type="application/ld+json">' + json.dumps(breadcrumb) + '</script>')

    html = head(
        "Upcoming Las Vegas Events 2026 — Races, F1 &amp; Festivals | TheVegasHub",
        "Upcoming events in and around Las Vegas — the F1 Grand Prix, off-road races, and the Las Vegas Triathlon. Dates, spectator info, and where to stay.",
        "/events",
        extra_jsonld=jsonld,
    ) + HEADER + f"""
<section class="section">
  <div class="container">
    <div class="section-head">
      <span class="pill pill-cyan">EVENTS</span>
      <h1 class="headline-glow" style="font-size:clamp(44px,7vw,80px); margin:12px 0 8px;">UPCOMING EVENTS</h1>
      <p class="kicker">Races, motorsport, and marquee events in and around Las Vegas — with spectator notes and where to stay.</p>
    </div>
{EVENTS_DISCLAIMER}
    <div class="grid grid-3">
{cards}    </div>
{EVENTS_BOOK_CTA}
  </div>
</section>
""" + FOOTER
    write("events/index.html", html)

# ---------------------------- GUIDES (pillar pages) ---------------------------- #

GUIDES = [
    {
        "slug": "best-time-to-visit-las-vegas",
        "title": "Best Time to Visit Las Vegas (2026) | TheVegasHub",
        "desc": "When to visit Las Vegas: month-by-month weather, the cheapest months to book, the event weeks that spike rates, and pool season. Plan your trip dates.",
        "h1": "Best Time to Visit Las Vegas",
        "pill": "TRIP PLANNING",
        "kicker": "Month-by-month weather, the cheapest weeks to book, and the dates to avoid.",
        "intro": """<p>The two best stretches are mid-March through May and mid-September through November. You get warm days, cool-enough nights, and room rates that aren't set for a convention crowd. Winter is the cheapest time to sleep on the Strip. Summer is the hottest, and midweek in July it's often cheaper than winter — if you can handle 105 degrees.</p>
<p>Below is what each season actually feels like, the weeks rooms cost the most, and the best month for the kind of trip you're taking.</p>""",
        "sections": [
            ("The weather, by season", """<p>Spring (March to May): highs climb from the low 70s in March to the low 90s by late May. Nights stay in the 50s and 60s. This is the most comfortable stretch of the year for walking the Strip.</p>
<p>Summer (June to August): daytime highs run 100 to 110. July averages a high near 105, and the pavement makes it feel hotter. Nights only drop to the mid-80s. Plan on being indoors or in a pool from noon to 5pm.</p>
<p>Fall (September to November): September still runs mid-90s. October cools to the low 80s. By November days sit around 65 and nights drop into the 40s. October is a lot of people's favorite month here.</p>
<p>Winter (December to February): highs of 55 to 60, nights near 40, and it gets windy. You won't swim in an unheated pool, but you can walk all day without sweating through your shirt.</p>"""),
            ("The cheapest months to book", """<p>January and February are the low season. After the first week of January, midweek rooms on the Strip drop to some of the lowest rates of the year. February is similar, minus one weekend (more on that below).</p>
<p>High summer — mid-July through August, Sunday through Thursday — is the other bargain window. The heat scares people off, so a room that runs $220 on a March Saturday can fall under $80 on a July Tuesday.</p>
<p>The pattern under all of this: Sunday through Thursday is always cheaper than Friday and Saturday, in every month. Shift your trip one day earlier and you'll often save more than any promo code.</p>"""),
            ("The weeks to expect high rates", """<p>A handful of dates fill the city and push rates up. If your trip is flexible, these are the ones to dodge:</p>
<ul>
<li>New Year's Eve — the single most expensive night of the year on the Strip.</li>
<li>CES, the first full week of January — a business crowd of 100,000-plus takes over. Rooms spike for about four nights, then crash right after.</li>
<li>Super Bowl weekend, early February — Vegas has turned into a Super Bowl destination, and rooms follow.</li>
<li>March Madness, mid-to-late March — sportsbooks fill for the first-weekend games.</li>
<li>EDC, mid-May — three nights of the electronic dance festival move rates across the whole Strip, not just the host hotel.</li>
<li>The <a href="/events/formula-1-las-vegas-grand-prix">Formula 1 Grand Prix</a>, mid-to-late November — the biggest rate jump on the calendar. A room near the circuit can run four to five times its normal price.</li>
<li>National Finals Rodeo, the first ten days of December — a lock-out for value on the south end especially.</li>
<li>Big fight weekends — UFC and boxing cards land on Mexican Independence weekend (mid-September) and Cinco de Mayo, among others. They move fast and move rates with them.</li>
</ul>"""),
            ("Pool season runs March to October", """<p>Most Strip pools open in March and close in late October. Dayclubs — Encore Beach Club, Marquee, Wet Republic — run their loudest from May through September. If a pool scene is the point of your trip, come between Memorial Day and Labor Day.</p>
<p>Two exceptions worth knowing: Stadium Swim at Circa downtown is heated and open year-round, and a few resort pools keep one heated pool going through winter. Our <a href="/things-to-do/best-pools-in-las-vegas">pool guide</a> has the full list.</p>"""),
            ("The best month for your kind of trip", """<p>On a budget: January or February, midweek. Or high summer midweek if the heat doesn't stop you.</p>
<p>For the pools and dayclubs: May through September.</p>
<p>For walking, sightseeing, and eating your way down the Strip: March, April, October, and November. Warm days, no heat exhaustion.</p>
<p>Traveling with kids on summer break: June through August. You're locked into the heat, so book a hotel with a pool you'll actually use, and plan indoor mornings.</p>
<p>A couples trip: April and October hit the sweet spot — warm evenings, patios open, rates lower than peak.</p>"""),
            ("Month-by-month at a glance", """<ul>
<li><strong>January:</strong> cold nights, cheap rooms — except CES week and the NYE hangover. Good value.</li>
<li><strong>February:</strong> cool, quiet, cheap. Watch Super Bowl weekend.</li>
<li><strong>March:</strong> warming up, pools reopen, March Madness fills sportsbooks late in the month.</li>
<li><strong>April:</strong> near-perfect weather, moderate rates. One of the best months.</li>
<li><strong>May:</strong> hot by late month, pool season on, EDC spikes mid-May.</li>
<li><strong>June:</strong> heat sets in, summer-break families arrive, rooms still reasonable midweek.</li>
<li><strong>July:</strong> hottest month, lowest midweek rates of the year.</li>
<li><strong>August:</strong> still very hot, cheap midweek, dayclubs busy.</li>
<li><strong>September:</strong> heat eases late, fight weekends spike rates.</li>
<li><strong>October:</strong> ideal weather, one of the most popular months.</li>
<li><strong>November:</strong> cool and pleasant — until F1 weekend, which is its own animal.</li>
<li><strong>December:</strong> chilly, NFR fills early December, holidays and NYE close the year hot.</li>
</ul>
<p>Once you've picked your dates, the next call is where on (or off) the Strip to stay — that's covered in <a href="/where-to-stay-in-las-vegas">where to stay in Las Vegas</a>. Remember that nearly every resort adds a nightly <a href="/things-to-do/resort-fees">resort fee</a> of $35 to $55 on top of the room rate.</p>"""),
        ],
        "faq": [
            ("What is the cheapest month to visit Las Vegas?", "January and February, midweek (Sunday through Thursday), after the first week of January. Midweek dates in July and August also run cheap because of the heat."),
            ("What is the hottest month in Las Vegas?", "July, with average highs near 105°F and nights in the mid-80s. June through August all sit above 100 most days."),
            ("When is pool season in Las Vegas?", "Most pools open in March and close in late October, and dayclubs peak May through September. Stadium Swim at Circa downtown is heated and open year-round."),
            ("When are Las Vegas hotel rates highest?", "New Year's Eve, CES week (early January), Super Bowl weekend, EDC (mid-May), the Formula 1 Grand Prix (mid-to-late November), and National Finals Rodeo (early December)."),
            ("What is the best month for a first Las Vegas trip?", "April or October — warm days, cool nights, and rates below the summer and event-week peaks."),
        ],
    },
    {
        "slug": "where-to-stay-in-las-vegas",
        "title": "Where to Stay in Las Vegas | TheVegasHub",
        "desc": "Where to stay in Las Vegas by area — Center Strip, South Strip, North Strip, Downtown Fremont, off-Strip, and Henderson — with the best pick for your trip.",
        "h1": "Where to Stay in Las Vegas",
        "pill": "HOTEL GUIDE",
        "kicker": "The Strip is four miles long. Here's which part to book for your trip.",
        "intro": """<p>Quick answer. First trip, want to walk to the famous stuff: stay Center Strip. Cheapest big-name rooms: South Strip or Downtown. Late nights and clubs: Center to North Strip. Quiet, cheaper, and you've got a car or you're visiting family: Henderson or off-Strip.</p>
<p>The Strip is about four miles long. "On the Strip" can mean a two-minute walk to the Bellagio fountains or a 25-minute walk in the heat to get there. Which end you pick matters more than most first-timers expect. Here's how the areas break down.</p>""",
        "sections": [
            ("Center Strip — best for first-timers", """<p>This is the core: Bellagio, Caesars Palace, the <a href="/hotels/cosmopolitan">Cosmopolitan</a>, Paris, Planet Hollywood, the Flamingo, and the LINQ. The Bellagio fountains, the Sphere views, the best pedestrian bridges, and the shortest walks between casinos are all here.</p>
<p>Stay in this stretch and you can leave your room, see five landmark hotels, and be back without a rideshare. That convenience is why it's the priciest area on Friday and Saturday. If it's your first Vegas trip, pay for the location — you'll walk everywhere and save the cab money.</p>"""),
            ("South Strip — value, families, and sports", """<p>MGM Grand, <a href="/hotels/mandalay-bay">Mandalay Bay</a>, <a href="/hotels/luxor">Luxor</a>, <a href="/hotels/excalibur">Excalibur</a>, and Park MGM sit at the south end, next to T-Mobile Arena and a short walk from Allegiant Stadium. Luxor and Excalibur are two of the cheapest big-name rooms in the city, which makes this end popular with families and anyone in town for a game or a concert.</p>
<p>The trade-off is distance. From Mandalay Bay to the Bellagio is a 25-minute walk or a tram-plus-walk. Plan on rideshares to reach the center, or lean into the south-end pools, arenas, and restaurants.</p>"""),
            ("North Strip — luxury and the Sphere", """<p><a href="/hotels/wynn">Wynn</a>, <a href="/hotels/encore">Encore</a>, Resorts World, the <a href="/hotels/venetian">Venetian</a>, and the <a href="/hotels/palazzo">Palazzo</a> anchor the north end, with the Sphere and Fashion Show mall right here. This is where the newest luxury towers and the quieter, more polished pools are.</p>
<p>It's calmer than the center and a walk to the Sphere for a show. The far north thins out — Circus Circus up here is the budget outlier, cheap but a real hike from the action. Great area if you want a nicer room and don't mind a rideshare to the middle.</p>"""),
            ("Downtown and Fremont Street — cheaper, older, more fun than people expect", """<p>Downtown is a 10-to-15-minute rideshare north of the Strip, and it's a different city. The Golden Nugget, the Plaza, the Fremont, the D, and Circa (21-and-up) sit under the Fremont Street Experience light canopy. Rooms run cheaper, table minimums are lower, and the drinks cost less than the Strip.</p>
<p>Stay down here if your budget is tight, you like old-school Vegas, or you want to gamble without $25 minimums. You'll rideshare to the Strip when you want it, but plenty of trips never leave. Our <a href="/hotels/downtown-fremont">Downtown Fremont hotels</a> page has the full list.</p>"""),
            ("Off-Strip — quiet and cheaper, if you don't mind a ride", """<p>The Rio, the Palms, Westgate, and Virgin Hotels sit a few minutes off the Strip. You give up the walk-everywhere location and get bigger rooms, shorter lines, and often free or cheaper parking. These work well for a return visitor who already knows the Strip and would rather have a quiet base and a rideshare habit.</p>"""),
            ("Henderson and the suburbs — resort feel, local prices", """<p>Green Valley Ranch and the <a href="/hotels/m-resort">M Resort</a> sit in Henderson, 20 to 30 minutes southeast of the Strip. These are locals' resorts: real spas, quiet pools, cheaper rooms, and none of the Strip crush. You need a car to make it work.</p>
<p>This is the pick if you're visiting family in the valley, playing golf, or you simply want to sleep somewhere calm. Same for the far northwest — Red Rock Resort out by Summerlin is a resort in its own right, close to the canyon, far from the neon.</p>"""),
            ("How to choose in one line", """<ul>
<li>First Vegas trip, want to walk to everything → Center Strip.</li>
<li>Lowest price on a name-brand room → Luxor or Excalibur (South Strip), or Downtown.</li>
<li>Clubs and late nights → Center to North Strip.</li>
<li>Sports and arenas → South Strip.</li>
<li>Newest luxury and the Sphere → North Strip.</li>
<li>Quiet, a car, or visiting family → Henderson or off-Strip.</li>
</ul>
<p>Every resort adds a nightly <a href="/things-to-do/resort-fees">resort fee</a> of roughly $35 to $55 on top of the advertised rate, so compare the all-in price, not the headline. To see where each hotel actually sits, use the <a href="/map">hotel map</a>. Not sure when to come? Read <a href="/best-time-to-visit-las-vegas">the best time to visit Las Vegas</a> first.</p>"""),
        ],
        "faq": [
            ("Where should a first-timer stay in Las Vegas?", "Center Strip — near the Bellagio fountains and Caesars Palace — so you can walk to the most famous hotels without a rideshare."),
            ("Where are the cheapest hotels on the Strip?", "The south end: Luxor and Excalibur are two of the cheapest big-name rooms. Downtown Fremont is cheaper still."),
            ("Is it better to stay on the Strip or Downtown?", "The Strip for landmarks and walkability; Downtown for cheaper rooms, lower table minimums, and old-Vegas Fremont Street. Downtown is a 10-to-15-minute rideshare from the Strip."),
            ("Where should I stay to be near Allegiant Stadium or T-Mobile Arena?", "The South Strip — Mandalay Bay, Luxor, Excalibur, MGM Grand, and Park MGM are the closest hotels."),
            ("Do all Las Vegas hotels charge a resort fee?", "Nearly all do — about $35 to $55 per night on top of the room rate — so compare the all-in price when you book."),
        ],
    },
]

def page_guide(g):
    import datetime
    today = datetime.date.today().isoformat()
    article = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": g["h1"], "description": g["desc"],
        "author": {"@type": "Organization", "name": "TheVegasHub"},
        "publisher": {"@type": "Organization", "name": "TheVegasHub"},
        "mainEntityOfPage": f"{SITE}/{g['slug']}",
        "image": f"{SITE}/images/og/og-default.jpg",
        "datePublished": today, "dateModified": today,
    }
    faq_entities = [{"@type": "Question", "name": q,
                     "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in g["faq"]]
    faqpage = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_entities}
    breadcrumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": g["h1"], "item": f"{SITE}/{g['slug']}"}]}
    jsonld = "\n".join('<script type="application/ld+json">' + json.dumps(x) + '</script>'
                       for x in (article, faqpage, breadcrumb))

    sections_html = "".join(
        f'<h2 class="headline neon-cyan" style="font-size:clamp(24px,3.5vw,32px); margin:36px 0 14px;">{h2}</h2>\n{body}\n'
        for h2, body in g["sections"])

    faq_cards = "".join(f"""      <div class="card" style="padding:24px; margin-bottom:14px;">
        <h3 class="headline" style="font-size:19px; margin:0 0 8px;">{q}</h3>
        <p style="margin:0; color:var(--text-muted); line-height:1.7;">{a}</p>
      </div>
""" for q, a in g["faq"])

    style = """
<style>
  .guide p{ font-size:17px; line-height:1.8; margin:0 0 16px; }
  .guide ul{ margin:0 0 18px; padding-left:22px; }
  .guide li{ margin-bottom:9px; line-height:1.7; }
  .guide .lead p{ font-size:19px; }
  .guide h2:first-of-type{ margin-top:8px; }
</style>
"""

    html = head(g["title"], g["desc"], f"/{g['slug']}", extra_jsonld=jsonld) + style + HEADER + f"""
<section class="section">
  <div class="container" style="max-width:820px;">
    <div class="section-head">
      <span class="pill pill-cyan">{g['pill']}</span>
      <h1 class="headline-glow" style="font-size:clamp(36px,6vw,64px); line-height:1.05; margin:12px 0 10px;">{g['h1'].upper()}</h1>
      <p class="kicker">{g['kicker']}</p>
    </div>
    <div class="guide">
      <div class="lead">{g['intro']}</div>
{sections_html}    </div>

    <h2 class="headline neon-yellow" style="font-size:clamp(24px,3.5vw,32px); margin:44px 0 16px;">Frequently Asked Questions</h2>
{faq_cards}
    <div style="text-align:center; margin-top:36px;">
      <a class="btn btn-cyan" href="/hotels">Find a Hotel</a>
      <a class="btn btn-ghost" href="/map" style="margin-left:12px;">Hotel Map</a>
    </div>
  </div>
</section>
""" + FOOTER
    write(f"{g['slug']}/index.html", html)

# ---------------------------- LANDMARK LANDING PAGES ---------------------------- #

LANDMARKS = [
    {
        "slug": "hotels-near-sphere",
        "title": "Hotels Near the Sphere Las Vegas | TheVegasHub",
        "desc": "The closest hotels to the Sphere in Las Vegas — the Venetian and Palazzo connect by walkway, with north-Strip and center-Strip options a short walk away.",
        "h1": "Hotels Near the Sphere",
        "pill": "HOTELS NEAR",
        "kicker": "The closest places to stay for a Sphere show — ranked by how short the walk back is.",
        "body": '''The [Sphere](/things-to-do/sphere) sits just east of the Strip, directly behind the Venetian and Palazzo. If you're seeing a show there, the walk from your room matters — 15,000 people leave at once, and a hotel you can walk back to beats a rideshare line every time. These are the closest places to stay.

## Connected by walkway — the Venetian and Palazzo

The [Venetian](/hotels/venetian) and the [Palazzo](/hotels/palazzo) are the two hotels physically closest to the Sphere, linked to it by a pedestrian walkway. You can leave the show and be in your room in under ten minutes without stepping onto a road. For a Sphere night, these are the pick — same complex, all-suite rooms, and the shortest possible walk back.

## A short walk — north-Strip hotels

Just north, [Wynn](/hotels/wynn), [Encore](/hotels/encore), and Resorts World are a 5-to-10-minute walk from the Sphere. You trade the covered walkway for a slightly longer stroll and get the newest luxury rooms on the Strip in return. Any of the three works well if the Venetian is booked or you want a different room style.

## Across the Strip — Caesars and the center

The center-Strip hotels — Caesars Palace, the [Cosmopolitan](/hotels/cosmopolitan), and the Flamingo — are a 10-to-15-minute walk or a quick rideshare. These make sense if you're pairing a Sphere show with a few days of center-Strip sightseeing and don't mind the short hop east on show night.

## Booking notes

Sphere nights sell out, and hotel rates near the venue climb on big residency weekends. Buy your show ticket first, then book the room — flying in to find your act is dark that week is the avoidable mistake. Nearly every hotel adds a nightly [resort fee](/things-to-do/resort-fees) of $35 to $55 on top of the rate, so compare the all-in price.

To see exactly how close each hotel sits to the Sphere, use the [hotel map](/map). For what's actually playing and where to sit, read the [Sphere guide](/things-to-do/sphere).''',
    },
    {
        "slug": "hotels-near-allegiant-stadium",
        "title": "Hotels Near Allegiant Stadium Las Vegas | TheVegasHub",
        "desc": "The closest hotels to Allegiant Stadium — Mandalay Bay, Luxor, and Excalibur are a short walk over the pedestrian bridge from the Raiders' home.",
        "h1": "Hotels Near Allegiant Stadium",
        "pill": "HOTELS NEAR",
        "kicker": "Walk to Raiders games and skip the post-game rideshare surge.",
        "body": '''Allegiant Stadium — home of the Raiders — sits just west of the south Strip, across Interstate 15. On a game day the smart move is to walk, not drive: the post-game rideshare surge is brutal and the lots empty slowly. A few south-Strip hotels put you a 10-to-15-minute walk from the gates.

## The walkable three

[Mandalay Bay](/hotels/mandalay-bay) is the closest Strip hotel to the stadium, a straight shot across the pedestrian bridge over I-15. [Luxor](/hotels/luxor) and [Excalibur](/hotels/excalibur) sit right behind it and share the same walk — both are among the cheapest big-name rooms in the city, which makes them the value pick for a game weekend. Stay in any of the three and you walk to kickoff and walk back after, no car, no surge.

## A little farther — the rest of the south Strip

Park MGM, New York-New York, and [MGM Grand](/hotels/mgm-grand) are a longer 20-minute walk or a short rideshare to the stadium. These are the better base if you're also going to a Golden Knights game or a concert at T-Mobile Arena, which sits behind New York-New York — you'd be walking distance to both venues.

## Getting there

The pedestrian bridge from Mandalay Bay is the fastest route on foot and avoids stadium traffic entirely. If you drive, book parking in advance — game-day lots sell out and street parking near the stadium is restricted. Rideshare drop-off is fine going in; coming out, walking back to a south-Strip hotel beats the pickup line most nights.

## Booking notes

Raiders home games and big stadium concerts push hotel rates up across the south Strip, and they sell out early for marquee opponents. Book as soon as the schedule drops. Nearly every hotel adds a nightly [resort fee](/things-to-do/resort-fees) of $35 to $55 on top of the rate.

Use the [hotel map](/map) to see how close each hotel sits to the stadium, and read our [sports-fan guide](/why-vegas/sports-fans) for the full venue-by-venue breakdown.''',
    },
    {
        "slug": "hotels-near-f1-circuit",
        "title": "Hotels Near the F1 Las Vegas Circuit | TheVegasHub",
        "desc": "Where to stay for the F1 Las Vegas Grand Prix — trackside hotels on the Strip circuit like Wynn, the Venetian, and the Cosmopolitan, with booking tips.",
        "h1": "Hotels Near the F1 Circuit",
        "pill": "HOTELS NEAR",
        "kicker": "The track is the Strip. The best rooms face the circuit — here's where to book.",
        "body": '''The [Formula 1 Las Vegas Grand Prix](/events/formula-1-las-vegas-grand-prix) is unlike any other race because the track is the Strip itself. The 3.8-mile circuit runs right down Las Vegas Boulevard, past the Bellagio, the Venetian, and Wynn. That changes the hotel math completely: the best rooms are the ones inside the track with a window facing the circuit, so you never cross a closed road on race weekend.

## Stay inside the track

[Wynn](/hotels/wynn), the [Venetian](/hotels/venetian), and the [Cosmopolitan](/hotels/cosmopolitan) all sit trackside, with rooms that look down onto the circuit. A room facing the track means you can watch cars from your window and reach the grandstands without crossing closed roads — during F1 weekend, whole stretches of the Strip shut down, so being inside the track is worth far more than usual.

## The rest of the circuit corridor

The rest of the center- and north-Strip hotels along the route — Caesars Palace, the Flamingo, Resorts World, [Encore](/hotels/encore) — put you within walking distance of the circuit even without a trackside room. These are the fallback when the marquee trackside rooms sell out, which they do months ahead.

## Book early, expect the biggest spike of the year

F1 weekend is the single largest hotel-rate spike on the Vegas calendar. A trackside room can run four to five times its normal price, and the best ones book up months before the November race. If you want to be there, reserve as early as you can and lock the room before you buy anything else.

A trackside view also lets you skip a grandstand ticket if you'd rather watch from your room — for some fans that's the whole reason to book the room in the first place.

## Booking notes

Confirm your room actually faces the track before you pay the premium — not every room in a trackside hotel has the view. Nearly every hotel adds a nightly [resort fee](/things-to-do/resort-fees) of $35 to $55 on top of the rate, and F1-weekend rates are steep to begin with, so compare the all-in number.

See the full dates and details on our [F1 event page](/events/formula-1-las-vegas-grand-prix), and use the [hotel map](/map) to find a room on the circuit.''',
    },
    {
        "slug": "hotels-near-convention-center",
        "title": "Hotels Near the Las Vegas Convention Center | TheVegasHub",
        "desc": "The closest hotels to the Las Vegas Convention Center (LVCC) — Westgate, the north-Strip resorts, and every hotel on the Monorail line to the halls.",
        "h1": "Hotels Near the Convention Center",
        "pill": "HOTELS NEAR",
        "kicker": "Match your hotel to the LVCC and the Monorail, not just a spot on the Strip.",
        "body": '''The Las Vegas Convention Center (LVCC) on Paradise Road is the biggest venue in the city and the home of CES and most mega-shows. It sits a block east of the Strip, not on it, so the hotels that work best for a convention aren't always the famous ones — they're the ones near a Monorail stop or a short walk from the halls.

## Closest to the halls

Westgate is the closest hotel to the LVCC, connected by its own walkway, and the Las Vegas Hilton sits right beside it. If your show is at the LVCC and you want the shortest possible morning walk, these two are the pick — you're at the floor in minutes without a car.

## North-Strip hotels on the Monorail

The north-Strip resorts — [Wynn](/hotels/wynn), [Encore](/hotels/encore), and Resorts World — are a short ride from the LVCC and near the Monorail line. The Monorail is the key to a convention stay: it runs behind the east-side Strip hotels from the Convention Center station down to MGM Grand, skipping traffic entirely during a big show. A room near a Monorail stop beats a fancier room stuck in show-week gridlock.

## The rest of the Monorail line

Every hotel along the Monorail — the [Venetian](/hotels/venetian), Harrah's, the Flamingo, Bally's, [MGM Grand](/hotels/mgm-grand) — is a reasonable LVCC base because the train drops you at the Convention Center door. If you want to stay in the center of the Strip and still commute easily to the halls, pick a hotel with a Monorail station and buy a multi-day pass.

## Booking notes

Convention weeks are the most expensive, most sold-out weeks of the year — CES in early January fills the city, and rates spike months ahead. Book as soon as your dates are set. If your company isn't covering a room block, our [where-to-stay guide](/where-to-stay-in-las-vegas) helps you find a nearby room that isn't priced for the show. The quieter non-gaming towers, like the Signature at MGM and Vdara, are better for calls between sessions.

Use the [hotel map](/map) to see how far each hotel sits from the LVCC, and read our full [convention guide](/why-vegas/conventions) for the other venues — Mandalay Bay, the Venetian Expo, and Caesars Forum.''',
    },
]

def page_landmark(l):
    breadcrumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": "Hotels", "item": f"{SITE}/hotels"},
        {"@type": "ListItem", "position": 3, "name": l["h1"], "item": f"{SITE}/{l['slug']}"}]}
    jsonld = '<script type="application/ld+json">' + json.dumps(breadcrumb) + '</script>'
    body_html = md_to_html(l["body"])
    html = head(l["title"], l["desc"], f"/{l['slug']}", extra_jsonld=jsonld) + HEADER + f"""
<section class="section">
  <div class="container" style="max-width:820px;">
    <div class="section-head">
      <span class="pill pill-cyan">{l['pill']}</span>
      <h1 class="headline-glow" style="font-size:clamp(34px,6vw,60px); line-height:1.05; margin:12px 0 10px;">{l['h1'].upper()}</h1>
      <p class="kicker">{l['kicker']}</p>
    </div>
    <div class="guide">
{body_html}
    </div>
    <div style="text-align:center; margin-top:36px;">
      <a class="btn btn-cyan" href="/hotels">Find a Hotel</a>
      <a class="btn btn-ghost" href="/map" style="margin-left:12px;">Hotel Map</a>
    </div>
  </div>
</section>
""" + FOOTER
    write(f"{l['slug']}/index.html", html)

# ---------------------------- HALLOWEEN (seasonal marketing) ---------------------------- #

# (slug, tag, Halloween blurb) — featured hotels for Halloween weekend.
HALLOWEEN_HOTELS = [
    ("encore",       "XS · ENCORE BEACH CLUB", "XS and Encore Beach Club throw the Strip's biggest Halloween-weekend parties — costume contests, headline DJs, and the after-dark pool editions if the weather holds."),
    ("cosmopolitan", "MARQUEE",                "Marquee's Halloween party plus a Strip-view Terrace suite to pre-game in. Center-Strip, so every other club is a short walk away."),
    ("mgm-grand",    "HAKKASAN",               "Hakkasan goes all-out for Halloween weekend, and it's in your building. Costume-up, ride the elevator down, and skip the 2am rideshare line."),
    ("crockfords",   "ZOUK · RESORTS WORLD",   "Zouk runs one of the newest, loudest Halloween parties on the Strip — and Crockfords puts you in the quiet luxury tower right above it."),
    ("bellagio",     "CONSERVATORY",           "The Conservatory's harvest display, the fountains, and a central base for club-hopping. The grown-up Halloween-weekend pick."),
    ("luxor",        "VALUE PICK",             "A giant black pyramid is about as spooky as a hotel gets — and it's one of the cheapest big-name rooms for a weekend that won't be cheap."),
]

def page_halloween():
    cards = ""
    for slug, tag, blurb in HALLOWEEN_HOTELS:
        h = HOTELS_BY_SLUG.get(slug)
        if not h:
            continue
        link = h.get("link", "")
        book_href = link if link.startswith("http") else "/hotels/" + slug
        book_rel = 'rel="nofollow sponsored noopener" target="_blank"' if link.startswith("http") else ""
        cards += f"""      <div class="card hw-card">
        <a href="/hotels/{slug}"><img class="card-img" src="{h.get('image','/images/og/og-default.jpg')}" alt="{h['alt']}" loading="lazy" onerror="this.src='/images/og/og-default.jpg'"></a>
        <div class="card-body">
          <span class="hw-pill">{tag}</span>
          <h3 class="headline" style="font-size:24px; margin:10px 0 8px;">{h['name']}</h3>
          <p style="color:var(--text-muted); font-size:14px; line-height:1.6; margin:0 0 16px; flex:1;">{blurb}</p>
          <a href="{book_href}" {book_rel} class="btn btn-pink" style="width:100%; text-align:center; font-size:13px; padding:12px;">BOOK NOW →</a>
        </div>
      </div>
"""

    breadcrumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": "Las Vegas Halloween", "item": f"{SITE}/las-vegas-halloween"}]}
    jsonld = '<script type="application/ld+json">' + json.dumps(breadcrumb) + '</script>'

    style = """
<style>
  .hw-hero{ position:relative; text-align:center; padding:84px 20px 58px; overflow:hidden;
    background:
      radial-gradient(60% 65% at 18% 20%, rgba(155,48,255,.42), transparent 60%),
      radial-gradient(55% 60% at 84% 26%, rgba(255,122,24,.34), transparent 60%),
      linear-gradient(160deg,#1a0e2b 0%, #0b0713 72%);
    border-bottom:1px solid rgba(255,122,24,.25); }
  .hw-pumpkin{ font-size:clamp(40px,8vw,60px); line-height:1; filter:drop-shadow(0 0 18px rgba(255,122,24,.6)); }
  .hw-title{ font-family:'Bebas Neue','Oswald',sans-serif; font-size:clamp(44px,9vw,96px); line-height:.98; letter-spacing:.07em; margin:6px 0 14px; color:#fff;
    text-shadow:0 0 14px rgba(255,122,24,.5), 0 0 34px rgba(155,48,255,.45); }
  .hw-sub{ color:rgba(255,255,255,.88); max-width:660px; margin:0 auto 26px; font-size:clamp(16px,2vw,20px); line-height:1.6; }
  .hw-cta{ display:inline-block; font-family:'Bungee',sans-serif; font-size:14px; letter-spacing:.05em; color:#160a24 !important;
    background:linear-gradient(90deg,#ff7a18,#9b30ff); padding:15px 32px; border-radius:999px; text-decoration:none; box-shadow:0 0 26px rgba(255,122,24,.45); }
  .hw-cta:hover{ filter:brightness(1.08); color:#160a24 !important; }
  .hw-pill{ display:inline-block; font-family:'Bungee',sans-serif; font-size:10px; letter-spacing:.12em; padding:5px 11px; border-radius:999px;
    color:#b34e08; border:1px solid rgba(255,122,24,.55); background:rgba(255,122,24,.10); }
  .hw-h2{ font-family:'Bebas Neue','Oswald',sans-serif; font-size:clamp(26px,4vw,40px); letter-spacing:.05em; margin:48px 0 14px; color:#b34e08; }
  :root[data-theme="dark"] .hw-h2{ color:#ff934d; }
  :root[data-theme="dark"] .hw-pill{ color:#ff934d; }
  .hw-body p{ font-size:17px; line-height:1.8; margin:0 0 16px; }
  .hw-body ul{ margin:0 0 18px; padding-left:22px; }
  .hw-body li{ margin-bottom:11px; line-height:1.7; }
  .hw-hotels .card{ border-color:rgba(155,48,255,.42); }
  .hw-hotels .card:hover{ border-color:#ff7a18; }
  .hw-band{ text-align:center; margin:52px 0 8px; padding:36px 22px; border-radius:16px;
    background:linear-gradient(135deg, rgba(155,48,255,.14), rgba(255,122,24,.14)); border:1px solid rgba(155,48,255,.32); }
</style>
"""

    html = head(
        "Las Vegas Halloween 2026 — Where to Stay | TheVegasHub",
        "Halloween 2026 in Las Vegas falls on a Saturday. Where to stay for the Strip's biggest costume-party weekend — featured hotels, club parties, and booking links.",
        "/las-vegas-halloween",
        extra_jsonld=jsonld,
    ) + style + HEADER + f"""
<section class="hw-hero">
  <div class="container">
    <div class="hw-pumpkin">🎃</div>
    <h1 class="hw-title">HALLOWEEN IN LAS VEGAS</h1>
    <p class="hw-sub">Halloween 2026 lands on a Saturday — the biggest costume-party weekend the Strip does all year. Here's where to stay and what to do.</p>
    <a class="hw-cta" href="#stay">🦇 Find Your Halloween Hotel</a>
  </div>
</section>

<section class="section">
  <div class="container" style="max-width:900px;">
    <div class="hw-body">
      <p style="font-size:19px; line-height:1.8;">The nightclubs throw the largest Halloween parties in the country, the dayclubs run haunted pool editions while it's still warm, and rooms book up weeks ahead. Pick your hotel early — here's the plan.</p>

      <h2 class="hw-h2">Why Vegas owns Halloween</h2>
      <p>The nightclubs are the main event. XS at Encore, Hakkasan at MGM Grand, Marquee at the Cosmopolitan, and Zouk at Resorts World all throw huge Halloween-weekend parties with costume contests and headline DJs. Tables sell out early — book two to three weeks ahead for the Saturday.</p>
      <p>Late October in Vegas still hits the 70s and low 80s, so the dayclubs keep going. Encore Beach Club and Wet Republic run their Halloween pool editions when the weather holds. If you want the pool-party version of the weekend, this is your last window before the pools close for winter.</p>
      <p>Off the Strip, haunted houses run across the valley all October and draw the biggest crowds the two weekends before the 31st. Area15 and its Omega Mart lean fully into the season, and they're indoor and open all day — a good move for the afternoon before the clubs.</p>

      <h2 class="hw-h2" id="stay">Where to stay for Halloween weekend</h2>
      <p>Pick a hotel with a party in the building and you can costume-up, take the elevator down, and skip the rideshare line at 2am. These six put you at the door of the best Halloween-weekend parties on the Strip. Every one books through TheVegasHub with member rates.</p>
    </div>

    <div class="grid grid-3 hw-hotels" style="margin-top:24px;">
{cards}    </div>

    <div class="hw-body">
      <h2 class="hw-h2">Spooky things to do</h2>
      <ul>
        <li>The Strip lights up orange and purple, and the costume crowds make it the best free people-watching of the year. Walk it after dark.</li>
        <li>The <a href="/things-to-do/bellagio-fountains">Bellagio</a> Conservatory runs its harvest and fall display through October — pumpkins, giant scarecrows, and it's free to walk through.</li>
        <li><a href="/things-to-do/fremont-street-experience">Fremont Street</a> downtown fills with costumes and cheaper drinks. The light-canopy shows plus a costume crowd is a night on its own.</li>
        <li>Want daylight before the dark? A <a href="/tours">Grand Canyon or Hoover Dam day trip</a> gets you out of the city before the night starts.</li>
      </ul>
    </div>

    <div class="hw-band">
      <h2 class="hw-h2" style="margin:0 0 10px;">Book before it sells out</h2>
      <p style="max-width:620px; margin:0 auto 20px; color:var(--text-muted); line-height:1.7;">Halloween weekend is one of the fastest-booking weekends of the fall, and a Saturday-night Halloween makes it worse. Lock your room early. Every hotel adds a nightly <a href="/things-to-do/resort-fees">resort fee</a> of $35 to $55 on top of the rate.</p>
      <a class="hw-cta" href="/hotels">🎃 Browse All Hotels</a>
    </div>

    <div style="text-align:center; margin-top:28px;">
      <a class="btn btn-ghost" href="/where-to-stay-in-las-vegas">Where to Stay Guide</a>
      <a class="btn btn-ghost" href="/best-time-to-visit-las-vegas" style="margin-left:10px;">Best Time to Visit</a>
    </div>
  </div>
</section>
""" + FOOTER
    write("las-vegas-halloween/index.html", html)

# ---------------------------- HOLIDAY PAGES (seasonal marketing) ---------------------------- #

SEASONAL = [
    ("las-vegas-halloween",       "Halloween"),
    ("thanksgiving-in-las-vegas", "Thanksgiving"),
    ("christmas-in-las-vegas",    "Christmas"),
    ("new-years-in-las-vegas",    "New Year's"),
]

HOLIDAYS = [
    {
        "slug": "thanksgiving-in-las-vegas",
        "title": "Thanksgiving in Las Vegas 2026 | TheVegasHub",
        "desc": "Thanksgiving in Las Vegas 2026 — the best turkey-day buffets, football at the sportsbooks, Black Friday shopping, and where to stay on the Strip.",
        "h1": "Thanksgiving in Las Vegas", "hero_prefix": "Thanksgiving", "emoji": "🦃",
        "hero_sub": "Thanksgiving 2026 is a Thursday — turkey-day buffets, three NFL games, Black Friday deals, and a 60-degree holiday. Here's where to feast and stay.",
        "cta": "🍗 Find Your Thanksgiving Hotel",
        "hero_grad": "radial-gradient(60% 65% at 18% 20%, rgba(166,50,24,.40), transparent 60%), radial-gradient(55% 60% at 84% 26%, rgba(224,138,20,.34), transparent 60%), linear-gradient(160deg,#241206 0%, #120a04 72%)",
        "hero_border": "rgba(224,138,20,.25)", "glow": "rgba(224,138,20,.5)", "glow2": "rgba(166,50,24,.45)",
        "title_accent": "#ffb15a", "btn_bg": "#e08a14", "btn_ink": "#241206",
        "ink": "#9a4e0a", "ink_dark": "#ffa94d",
        "pill_border": "rgba(224,138,20,.55)", "pill_bg": "rgba(224,138,20,.10)",
        "card_border": "rgba(166,50,24,.38)", "card_hover": "#e08a14",
        "band_grad": "linear-gradient(135deg, rgba(166,50,24,.12), rgba(224,138,20,.13))", "band_border": "rgba(224,138,20,.30)",
        "intro": "Thanksgiving in Las Vegas is the easy holiday — someone else cooks the turkey, the football is on a hundred screens, and the weather sits in the low 60s. No dishes, no travel-day cooking, and the best buffets in the country are a short walk from your room. Here's where to feast and where to stay.",
        "sections": [
            ("The Vegas Thanksgiving, in three parts", '''<p><strong>The feast.</strong> Nearly every big hotel runs a Thanksgiving menu — carved turkey, stuffing, the whole spread — at its buffets and steakhouses. Bacchanal at Caesars and Wicked Spoon at the Cosmopolitan are the headline buffets; the fine-dining rooms at Wynn and Bellagio do plated turkey dinners. Book the restaurant two to three weeks out. Thanksgiving dinner reservations fill before the rooms do.</p>
<p><strong>The football.</strong> Three NFL games run all Thanksgiving Day, and the sportsbooks turn into the best sports bars in the country — stadium seating, wall-sized screens, and a bet on the game if you want one. Get to your book by late morning on Thursday to claim a seat.</p>
<p><strong>The shopping.</strong> Black Friday in Vegas means the outlet malls and the Strip shops open early with real markdowns. The Las Vegas North and South Premium Outlets and the Fashion Show mall are the big three. Go early, before the Strip wakes up.</p>'''),
        ],
        "stay_h2": "Where to stay for Thanksgiving weekend",
        "stay_intro": "Pick a hotel with a great kitchen in the building and the holiday runs itself — roll downstairs to the feast, catch the football, and never touch a dish. These six put you on top of the best Thanksgiving dinners on the Strip.",
        "hotels": [
            ("caesars-palace", "BACCHANAL BUFFET",      "Bacchanal Buffet is the best spread in the city, and it runs a full Thanksgiving feast. The Forum Shops handle your Black Friday run."),
            ("cosmopolitan",   "WICKED SPOON",          "Wicked Spoon's holiday service plus a Strip-view suite, dead center for walking to every other restaurant."),
            ("bellagio",       "DINING + CONSERVATORY", "Plated turkey dinners in the fine-dining rooms, and the Conservatory turns to its fall harvest display for the week."),
            ("wynn",           "WYNN RESTAURANTS",      "Some of the best Thanksgiving dinners on the Strip, steps from a quiet luxury room to nap it off."),
            ("mgm-grand",      "SPORTSBOOK + DINING",   "A dozen restaurants for the feast and a sportsbook built for the three-game Thursday."),
            ("mandalay-bay",   "FAMILY ROOMS",          "Big rooms for the family, a warm pool deck, and a calmer south-Strip base for the long weekend."),
        ],
        "close_h2": "Make a weekend of it",
        "close_p": '''Thanksgiving falls four days after the Formula 1 race in 2026, so the city is already in high gear. Stretch the trip into the weekend — the <a href="/things-to-do/bellagio-fountains">Bellagio fountains</a>, a show, or a <a href="/tours">Grand Canyon or Hoover Dam day trip</a> on the Friday while everyone else is shopping. Book the room early. A Thursday-holiday Thanksgiving fills the Strip fast, and every hotel adds a nightly <a href="/things-to-do/resort-fees">resort fee</a> of $35 to $55 on top of the rate.''',
    },
    {
        "slug": "christmas-in-las-vegas",
        "title": "Christmas in Las Vegas 2026 | TheVegasHub",
        "desc": "Christmas in Las Vegas 2026 — holiday light displays, the Bellagio Conservatory, the Cosmopolitan ice rink, shows, and where to stay on the Strip.",
        "h1": "Christmas in Las Vegas", "hero_prefix": "Christmas", "emoji": "🎄",
        "hero_sub": "Christmas 2026 falls on a Friday — a long weekend of holiday lights, an ice rink on the Strip, and a 60-degree Christmas. Here's where to stay.",
        "cta": "🎁 Find Your Christmas Hotel",
        "hero_grad": "radial-gradient(60% 65% at 18% 20%, rgba(46,139,87,.38), transparent 60%), radial-gradient(55% 60% at 84% 26%, rgba(212,47,47,.38), transparent 60%), linear-gradient(160deg,#0c1f14 0%, #0a0f0b 72%)",
        "hero_border": "rgba(212,47,47,.28)", "glow": "rgba(212,47,47,.5)", "glow2": "rgba(46,139,87,.45)",
        "title_accent": "#8fe3b0", "btn_bg": "#d42f2f", "btn_ink": "#ffffff",
        "ink": "#b01e2e", "ink_dark": "#ff8a8a",
        "pill_border": "rgba(46,139,87,.55)", "pill_bg": "rgba(46,139,87,.10)",
        "card_border": "rgba(46,139,87,.40)", "card_hover": "#d42f2f",
        "band_grad": "linear-gradient(135deg, rgba(212,47,47,.12), rgba(46,139,87,.13))", "band_border": "rgba(46,139,87,.32)",
        "intro": "Christmas 2026 falls on a Friday, which makes it a long holiday weekend — and Las Vegas does Christmas better than people expect. The hotels deck out their lobbies, the Strip glows, there's an ice rink on a pool deck, and the desert gives you a 60-degree Christmas instead of a shovel. Here's where to stay and what to see.",
        "sections": [
            ("The lights are the main event", '''<p>Las Vegas goes all-in on holiday decor, and most of it is free to walk through. The Bellagio Conservatory turns into a full Christmas scene — giant ornaments, a towering tree, and the fountains running holiday music out front. The Venetian decks its canal and painted-sky ceiling top to bottom. Wynn and Encore fill their atriums with carousels and hanging gardens of ornaments.</p>
<p>Off the Strip, two drive-through and walk-through light shows run all December — the Ethel M Holiday Cactus Garden in Henderson wraps its whole cactus garden in lights, and the bigger ticketed displays set up at the speedway and the park. They draw families every night in the two weeks before Christmas.</p>'''),
            ("A warm-weather Christmas", '''<p>A Vegas Christmas is a 60-degree day, not a snowstorm. The pools mostly close for winter, but the ice rink on the Cosmopolitan's Boulevard Pool deck opens for the season — outdoor skating with the Strip right there. The shows run through the holiday too, several of them in Christmas editions. Book those before you book the hotel; the good nights sell out.</p>'''),
        ],
        "stay_h2": "Where to stay for Christmas",
        "stay_intro": "These six put you inside or next to the best holiday displays in the city, so the lights are a walk from your room, not a drive.",
        "hotels": [
            ("bellagio",       "CONSERVATORY",   "The Conservatory's Christmas display and the fountains in holiday mode — the most photographed Christmas spot in Vegas is in your lobby."),
            ("venetian",       "HOLIDAY DECOR",  "Decked top to bottom, with a Christmas scene under the painted-sky ceiling and the Sphere glowing next door."),
            ("cosmopolitan",   "ICE RINK",       "The ice rink on the Boulevard Pool deck, Strip-view suites, and the best people-watching in town."),
            ("wynn",           "ATRIUM DISPLAY", "Wynn and Encore go all-out on holiday decor; the atrium alone is worth the walk over."),
            ("aria",           "CITYCENTER",     "A central CityCenter base with holiday art installations and quiet luxury for the week between the holidays."),
            ("caesars-palace", "FORUM SHOPS",    "The Forum Shops dressed for Christmas and Bacchanal Buffet for the holiday feast."),
        ],
        "close_h2": "Plan the week between the holidays",
        "close_p": '''The stretch from Christmas to New Year's is one of the busiest weeks of the year on the Strip, and it runs right into the biggest party night of all. Book early, pair your dates with a show, and read our <a href="/new-years-in-las-vegas">New Year's in Las Vegas</a> guide if you're staying through the 31st. Every hotel adds a nightly <a href="/things-to-do/resort-fees">resort fee</a> of $35 to $55 on top of the rate.''',
    },
    {
        "slug": "new-years-in-las-vegas",
        "title": "New Year's in Las Vegas 2026 | TheVegasHub",
        "desc": "New Year's Eve in Las Vegas 2026 — Strip fireworks, the biggest nightclub countdowns, and where to stay for the best midnight view. Book early.",
        "h1": "New Year's in Las Vegas", "hero_prefix": "New Year's", "emoji": "🎆",
        "hero_sub": "New Year's Eve 2026 — Strip fireworks off eight rooftops, the biggest countdowns on earth, and the best midnight view from your room. Book early.",
        "cta": "🥂 Find Your New Year's Hotel",
        "hero_grad": "radial-gradient(60% 65% at 18% 20%, rgba(155,48,255,.42), transparent 60%), radial-gradient(55% 60% at 82% 26%, rgba(224,186,64,.34), transparent 60%), linear-gradient(160deg,#17122b 0%, #0a0810 72%)",
        "hero_border": "rgba(224,186,64,.28)", "glow": "rgba(224,186,64,.5)", "glow2": "rgba(155,48,255,.45)",
        "title_accent": "#ffd86b", "btn_bg": "#e0ba40", "btn_ink": "#17122b",
        "ink": "#6a1fb8", "ink_dark": "#ffd86b",
        "pill_border": "rgba(155,48,255,.50)", "pill_bg": "rgba(155,48,255,.10)",
        "card_border": "rgba(155,48,255,.42)", "card_hover": "#e0ba40",
        "band_grad": "linear-gradient(135deg, rgba(155,48,255,.15), rgba(224,186,64,.16))", "band_border": "rgba(155,48,255,.34)",
        "intro": "New Year's Eve is the biggest night of the year in Las Vegas. The Strip closes to cars and fills with a few hundred thousand people, fireworks launch off eight hotel rooftops at midnight, and the nightclubs throw the loudest countdowns on earth. It's also the most expensive and fastest-booking night of the year — so the plan matters. Here's where to stay and how to do it.",
        "sections": [
            ("The fireworks are the whole show", '''<p>At midnight, fireworks fire from the rooftops of eight Strip hotels at once — an eight-minute show down the whole four-mile corridor. The street party is free: the Strip shuts to traffic in the evening and becomes one long pedestrian zone. If you just want to stand in it, you can, but get there early and know that once you're in, leaving is slow.</p>
<p>The better seat is up high. A Strip-view room or a balcony suite puts the fireworks outside your window with no crowd, no security line, and a warm place to stand. Those rooms book months ahead and command the year's top rates, so the earlier you lock one, the better.</p>'''),
            ("The club countdowns", '''<p>If midnight means a party, the nightclubs run the biggest ones anywhere. XS at Encore, Hakkasan at MGM Grand, Omnia at Caesars, and Zouk at Resorts World all throw New Year's Eve countdowns with headline DJs and a balloon drop at twelve. Tables and tickets go on sale months out and sell through — book as early as you can, and expect New Year's pricing on everything.</p>'''),
        ],
        "stay_h2": "Where to stay for New Year's Eve",
        "stay_intro": "The right room on New Year's Eve is worth more than any other night of the year — it's your fireworks seat, your warm base, and your skip-the-crowd pass. These six put you at the center of it.",
        "hotels": [
            ("cosmopolitan",   "BALCONY SUITES · MARQUEE", "Terrace suites with private balconies over the Strip — the best fireworks seat in the city, and Marquee's countdown is downstairs."),
            ("encore",         "XS COUNTDOWN",             "XS throws the biggest New Year's party on the Strip. Book the table months ahead and sleep steps from the door."),
            ("wynn",           "NEXT TO XS",               "Right next to XS and the fireworks, with the quieter luxury rooms to recover in on the 1st."),
            ("mgm-grand",      "HAKKASAN",                 "Hakkasan's countdown is in your building, and the south Strip has a clear line to the midnight show."),
            ("bellagio",       "FOUNTAIN VIEWS",           "Fountain-view rooms frame the fireworks and the water show together — the grown-up New Year's pick."),
            ("caesars-palace", "OMNIA · CENTER STRIP",     "Center-Strip and walking distance to Omnia and the heart of the party. Book early; this is the priciest night of the year."),
        ],
        "close_h2": "Book it now, not later",
        "close_p": '''Nothing in Vegas books earlier or sells out harder than New Year's Eve. Rooms, club tables, and dinner reservations all go months ahead, and prices only climb as the date fills. If New Year's on the Strip is the plan, lock the room first and build everything else around it. Every hotel adds a nightly <a href="/things-to-do/resort-fees">resort fee</a> of $35 to $55 on top of the rate, and holiday rates are steep to begin with, so compare the all-in price. Coming for the whole week? Start with our <a href="/christmas-in-las-vegas">Christmas in Las Vegas</a> guide.''',
    },
]

def page_holiday(h):
    cards = ""
    for slug, tag, blurb in h["hotels"]:
        ho = HOTELS_BY_SLUG.get(slug)
        if not ho:
            continue
        link = ho.get("link", "")
        book_href = link if link.startswith("http") else "/hotels/" + slug
        book_rel = 'rel="nofollow sponsored noopener" target="_blank"' if link.startswith("http") else ""
        cards += f"""      <div class="card hol-card">
        <a href="/hotels/{slug}"><img class="card-img" src="{ho.get('image','/images/og/og-default.jpg')}" alt="{ho['alt']}" loading="lazy" onerror="this.src='/images/og/og-default.jpg'"></a>
        <div class="card-body">
          <span class="hol-pill">{tag}</span>
          <h3 class="headline" style="font-size:24px; margin:10px 0 8px;">{ho['name']}</h3>
          <p style="color:var(--text-muted); font-size:14px; line-height:1.6; margin:0 0 16px; flex:1;">{blurb}</p>
          <a href="{book_href}" {book_rel} class="btn btn-pink" style="width:100%; text-align:center; font-size:13px; padding:12px;">BOOK NOW →</a>
        </div>
      </div>
"""
    sections_html = "".join(f'<h2 class="hol-h2">{t}</h2>\n{body}\n' for t, body in h["sections"])
    xlinks = "".join(f'<a class="btn btn-ghost" href="/{s}" style="margin:4px;">{lbl}</a>'
                     for s, lbl in SEASONAL if s != h["slug"])

    breadcrumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": h["h1"], "item": f"{SITE}/{h['slug']}"}]}
    jsonld = '<script type="application/ld+json">' + json.dumps(breadcrumb) + '</script>'

    style = f"""<style>
  .hol-hero{{ position:relative; text-align:center; padding:84px 20px 58px; overflow:hidden;
    background:{h['hero_grad']}; border-bottom:1px solid {h['hero_border']}; }}
  .hol-emoji{{ font-size:clamp(40px,8vw,60px); line-height:1; filter:drop-shadow(0 0 18px {h['glow']}); }}
  .hol-title{{ font-family:'Bebas Neue','Oswald',sans-serif; font-size:clamp(44px,9vw,96px); line-height:.98; letter-spacing:.07em; margin:6px 0 14px; color:#fff;
    text-shadow:0 0 14px {h['glow']}, 0 0 34px {h['glow2']}; }}
  .hol-sub{{ color:rgba(255,255,255,.88); max-width:660px; margin:0 auto 26px; font-size:clamp(16px,2vw,20px); line-height:1.6; }}
  .hol-cta{{ display:inline-block; font-family:'Bungee',sans-serif; font-size:14px; letter-spacing:.05em; color:{h['btn_ink']} !important;
    background:{h['btn_bg']}; padding:15px 32px; border-radius:999px; text-decoration:none; box-shadow:0 0 26px {h['glow']}; }}
  .hol-cta:hover{{ filter:brightness(1.08); color:{h['btn_ink']} !important; }}
  .hol-pill{{ display:inline-block; font-family:'Bungee',sans-serif; font-size:10px; letter-spacing:.12em; padding:5px 11px; border-radius:999px;
    color:{h['ink']}; border:1px solid {h['pill_border']}; background:{h['pill_bg']}; }}
  .hol-h2{{ font-family:'Bebas Neue','Oswald',sans-serif; font-size:clamp(26px,4vw,40px); letter-spacing:.05em; margin:48px 0 14px; color:{h['ink']}; }}
  :root[data-theme="dark"] .hol-h2{{ color:{h['ink_dark']}; }}
  :root[data-theme="dark"] .hol-pill{{ color:{h['ink_dark']}; }}
  .hol-body p{{ font-size:17px; line-height:1.8; margin:0 0 16px; }}
  .hol-hotels .card{{ border-color:{h['card_border']}; }}
  .hol-hotels .card:hover{{ border-color:{h['card_hover']}; }}
  .hol-band{{ text-align:center; margin:52px 0 8px; padding:36px 22px; border-radius:16px;
    background:{h['band_grad']}; border:1px solid {h['band_border']}; }}
</style>
"""

    html = head(h["title"], h["desc"], f"/{h['slug']}", extra_jsonld=jsonld) + style + HEADER + f"""
<section class="hol-hero">
  <div class="container">
    <div class="hol-emoji">{h['emoji']}</div>
    <h1 class="hol-title">{h['hero_prefix']} in <span style="color:{h['title_accent']};">Las Vegas</span></h1>
    <p class="hol-sub">{h['hero_sub']}</p>
    <a class="hol-cta" href="#stay">{h['cta']}</a>
  </div>
</section>

<section class="section">
  <div class="container" style="max-width:900px;">
    <div class="hol-body">
      <p style="font-size:19px; line-height:1.8;">{h['intro']}</p>
{sections_html}
      <h2 class="hol-h2" id="stay">{h['stay_h2']}</h2>
      <p>{h['stay_intro']}</p>
    </div>

    <div class="grid grid-3 hol-hotels" style="margin-top:24px;">
{cards}    </div>

    <div class="hol-band">
      <h2 class="hol-h2" style="margin:0 0 10px;">{h['close_h2']}</h2>
      <p style="max-width:640px; margin:0 auto 4px; color:var(--text-muted); line-height:1.7;">{h['close_p']}</p>
    </div>

    <div style="text-align:center; margin-top:28px;">
      <a class="btn btn-cyan" href="/hotels">Browse All Hotels</a>
      <a class="btn btn-ghost" href="/where-to-stay-in-las-vegas" style="margin-left:10px;">Where to Stay</a>
    </div>

    <div style="text-align:center; margin-top:38px; padding-top:26px; border-top:1px solid var(--card-border);">
      <p style="color:var(--text-muted); font-size:13px; margin:0 0 10px;">More Las Vegas holiday guides</p>
      {xlinks}
    </div>
  </div>
</section>
""" + FOOTER
    write(f"{h['slug']}/index.html", html)

def page_sitemap():
    """Regenerate sitemap.xml including all hotel pages."""
    import datetime
    today = datetime.date.today().isoformat()  # refreshed on every build
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
        ("/map",                                              "monthly", "0.8"),
        ("/events",                                           "weekly",  "0.8"),
        ("/tours",                                            "weekly",  "0.9"),
        ("/things-to-do",                                     "weekly",  "0.9"),
        ("/things-to-do/atomic-golf",                         "monthly", "0.8"),
    ])
    for slug, *_ in LISTICLES:
        urls.append((f"/things-to-do/{slug}", "monthly", "0.8"))
    for a in ATTRACTIONS:
        urls.append((f"/things-to-do/{a['slug']}", "monthly", "0.7"))
    for e in EVENTS:
        urls.append((f"/events/{e['slug']}", "weekly", "0.7"))
    for g in GUIDES:
        urls.append((f"/{g['slug']}", "monthly", "0.8"))
    for l in LANDMARKS:
        urls.append((f"/{l['slug']}", "monthly", "0.7"))
    urls.append(("/las-vegas-halloween", "monthly", "0.7"))
    for hol in HOLIDAYS:
        urls.append((f"/{hol['slug']}", "monthly", "0.7"))
    urls.append(("/why-vegas", "monthly", "0.8"))
    for slug, *_ in WHY:
        urls.append((f"/why-vegas/{slug}", "monthly", "0.7"))
    urls.extend([
        ("/packing-list",                       "monthly", "0.8"),
        ("/travel-insurance",                   "monthly", "0.8"),
        ("/newsletter",                         "yearly",  "0.5"),
        ("/things-to-do/resort-fees",           "monthly", "0.7"),
        ("/about",                              "yearly",  "0.5"),
        ("/contact",                            "yearly",  "0.5"),
        ("/privacy",                            "yearly",  "0.3"),
        ("/terms",                              "yearly",  "0.3"),
        ("/disclosure",                         "yearly",  "0.3"),
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
    page_map()
    page_events_index()
    for e in EVENTS:
        page_event(e)
    for g in GUIDES:
        page_guide(g)
    for l in LANDMARKS:
        page_landmark(l)
    page_halloween()
    for hol in HOLIDAYS:
        page_holiday(hol)
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

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
{extra_jsonld}
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_ID}');
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
        </ul>
      </div>
    </div>
    <div style="border-top:1px solid rgba(191,0,255,.15); padding-top:20px; display:flex; justify-content:space-between; flex-wrap:wrap; gap:16px; font-size:13px; color:var(--text-muted);">
      <div>© <span data-current-year>2026</span> TheVegasHub.com · Headquartered in Las Vegas</div>
      <div>Some links are affiliate links. We may earn a commission — at no extra cost to you.</div>
    </div>
  </div>
</footer>
<script src="/js/site.js"></script>
</body>
</html>
"""

def hotel_card(h):
    link = h.get("link", "#")
    is_todo = (not link) or link.startswith("TODO")
    href = link if not is_todo else "/contact"
    label = "COMING SOON" if is_todo else "BOOK HOT DEAL"
    rel = 'rel="nofollow sponsored" target="_blank"' if not is_todo else ""
    pill = '<span class="pill">COMING SOON</span>' if is_todo else '<span class="pill pill-pink">HOT DEAL</span>'
    img = h.get("image","/images/og/og-default.jpg")
    alt = h["alt"]
    note = h.get("note","")
    city = h.get("city","")
    return f"""      <a class="card" href="{href}" {rel} id="{h['slug']}">
        <img class="card-img" src="{img}" alt="{alt}" loading="lazy" onerror="this.src='/images/og/og-default.jpg'">
        <div class="card-body">
          {pill}
          <h3 class="headline" style="font-size:26px; margin:10px 0 4px;">{h['name']}</h3>
          <p style="color:var(--text-muted); font-size:13px; margin:0 0 12px;">{city}</p>
          <p style="margin:0 0 14px;">{note}</p>
          <span class="display neon-pink" style="font-size:13px;">{label} →</span>
        </div>
      </a>
"""

def write(rel_path, html):
    out = ROOT / rel_path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(f"  wrote {rel_path}")

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

def page_city(slug, title, desc, heading, filt):
    matches = [h for h in HOTELS if filt(h)]
    cards = "".join(hotel_card(h) for h in matches) or "<p>Hotels coming soon.</p>"
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
    <div class="grid grid-3">
{cards}    </div>
  </div>
</section>
""" + FOOTER
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
        "Compare top Las Vegas tours and day trips — Grand Canyon helicopters, Hoover Dam bus tours, Red Rock Canyon, Sphere shows, and more. Prices from Viator and Klook.",
        "/tours",
    ) + HEADER + """
<section class="section">
  <div class="container">
    <div class="section-head">
      <span class="pill pill-pink">TOURS & DAY TRIPS</span>
      <h1 class="headline-glow" style="font-size:clamp(44px,7vw,80px); margin:12px 0 8px;">VEGAS TOURS</h1>
      <p class="kicker">The best day trips from Las Vegas — compared across Viator and Klook so you get the best rate.</p>
    </div>

    <h2 class="headline neon-cyan" style="margin-top:32px;">TOP PICKS RIGHT NOW</h2>
    <p style="color:var(--text-muted); margin-bottom:24px;">Live pricing below — refreshed whenever this page loads.</p>

    <div style="background:rgba(255,255,255,.03); border:1px solid rgba(191,0,255,.2); border-radius:10px; padding:20px; margin-bottom:32px;">
      <div style="font-family:'Bungee',sans-serif; color:var(--neon-cyan); font-size:14px; margin-bottom:14px; letter-spacing:.12em;">FROM VIATOR →</div>
      <div data-vi-partner-id="U00009631" data-vi-widget-ref="W-e608db0e-5519-4eb8-a37f-01bb80769f0a"></div>
      <script async src="https://www.viator.com/orion/partner/widget.js"></script>
    </div>

    <div style="background:rgba(255,255,255,.03); border:1px solid rgba(255,46,176,.2); border-radius:10px; padding:20px; margin-bottom:32px;">
      <div style="font-family:'Bungee',sans-serif; color:var(--neon-pink); font-size:14px; margin-bottom:14px; letter-spacing:.12em;">FROM KLOOK →</div>
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
        <a href="//www.klook.com/">Klook.com</a>
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

def page_things_index():
    tiles = "".join(f"""      <a class="card" href="/things-to-do/{s}" style="padding:28px; text-decoration:none;">
        <span class="pill pill-cyan">LIST</span>
        <h3 class="headline" style="font-size:24px; margin:14px 0 6px;">{h1}</h3>
        <p style="margin:0; color:var(--text-muted);">{d}</p>
      </a>
""" for s,_,d,h1,_ in LISTICLES)
    html = head(
        "Things to Do in Las Vegas — Listicles by Locals | TheVegasHub",
        "Locals' ranked lists for Las Vegas — free things to do, best pools, best day trips, best shows, best cheap Strip hotels.",
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

# ---------------------------- README ---------------------------- #

README = """# TheVegasHub.com

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
"""

def page_readme():
    write("README.md", README)

# ---------------------------- MAIN ---------------------------- #

if __name__ == "__main__":
    print("Building TheVegasHub.com ...")
    page_hotels_index()
    for slug, title, desc, heading, filt in CITY_PAGES:
        page_city(slug, title, desc, heading, filt)
    page_tours()
    page_things_index()
    for slug, title, desc, h1, items in LISTICLES:
        page_listicle(slug, title, desc, h1, items)
    page_why_index()
    for slug, title, desc, h1, body in WHY:
        page_why(slug, title, desc, h1, body)
    page_packing_list()
    page_about()
    page_contact()
    page_readme()
    print("Done.")

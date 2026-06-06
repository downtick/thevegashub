// TheVegasHub.com — newsletter subscribe handler (Vercel serverless)
// Proxies to Sendy so the API key never touches the browser.
//
// Required env vars (set in Vercel Dashboard → Project Settings → Environment Variables):
//   SENDY_API_KEY   — your Sendy API key
//   SENDY_LIST_ID   — Sendy list ID (the hash shown in your Sendy list settings)
//   SENDY_URL       — base URL of your Sendy install, e.g. https://clubfluent.com/sendy

const rateLimits = new Map(); // IP → last-submit ms (resets on cold-start; fine for MVP)

function getIp(req) {
  const fwd = (req.headers['x-forwarded-for'] || '').split(',').map(s => s.trim()).filter(Boolean);
  return fwd[0] || req.socket?.remoteAddress || 'unknown';
}

function isValidEmail(email) {
  if (typeof email !== 'string' || email.length > 254) return false;
  return /^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/.test(email);
}

function sanitizeName(str) {
  if (typeof str !== 'string') return '';
  return str.replace(/<[^>]*>/g, '').replace(/[^\p{L}\p{N} .'\-]/gu, '').slice(0, 80).trim();
}

module.exports = async (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Cache-Control', 'no-store');
  // Allow the form to POST from the same origin
  res.setHeader('Access-Control-Allow-Origin', 'https://thevegashub.com');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.statusCode = 204;
    return res.end();
  }

  if (req.method !== 'POST') {
    res.statusCode = 405;
    return res.end(JSON.stringify({ error: 'Method not allowed.' }));
  }

  // ── Rate limit: one submission per IP per 30 s ──
  const ip = getIp(req);
  const now = Date.now();
  if (now - (rateLimits.get(ip) || 0) < 30_000) {
    res.statusCode = 429;
    return res.end(JSON.stringify({ error: 'Please wait a moment before trying again.' }));
  }

  // ── Parse body ──
  let body = req.body;
  if (!body || typeof body === 'string') {
    try {
      const raw = typeof body === 'string' ? body : await new Promise((resolve, reject) => {
        let data = '';
        req.on('data', c => { data += c; if (data.length > 4000) req.destroy(); });
        req.on('end', () => resolve(data));
        req.on('error', reject);
      });
      body = raw ? JSON.parse(raw) : {};
    } catch {
      res.statusCode = 400;
      return res.end(JSON.stringify({ error: 'Invalid request.' }));
    }
  }

  // ── Honeypot: silent success if bot fills the hidden field ──
  if (body.website || body.hp_field) {
    rateLimits.set(ip, now);
    return res.end(JSON.stringify({ ok: true }));
  }

  // ── Validate inputs ──
  const email = typeof body.email === 'string' ? body.email.slice(0, 254).trim().toLowerCase() : '';
  const name  = sanitizeName(body.name || '');

  if (!isValidEmail(email)) {
    res.statusCode = 400;
    return res.end(JSON.stringify({ error: 'Please enter a valid email address.' }));
  }

  // ── Pull secrets from env (never from request) ──
  const apiKey        = process.env.SENDY_API_KEY;
  const listId        = process.env.SENDY_LIST_ID;
  const sendyUrl      = (process.env.SENDY_URL || '').replace(/\/$/, '');
  const originSecret  = process.env.SENDY_ORIGIN_SECRET; // optional but strongly recommended

  if (!apiKey || !listId || !sendyUrl) {
    console.error('[subscribe] missing env vars — SENDY_API_KEY, SENDY_LIST_ID, or SENDY_URL not set');
    res.statusCode = 500;
    return res.end(JSON.stringify({ error: 'Newsletter signup is temporarily unavailable.' }));
  }

  // ── Call Sendy subscribe API ──
  // Sendy expects form-encoded, not JSON
  const params = new URLSearchParams({
    api_key:  apiKey,
    email:    email,
    list:     listId,
    boolean:  'true',  // return plain text response instead of redirect
    ...(name ? { name } : {}),
  });

  try {
    const sendyHeaders = { 'Content-Type': 'application/x-www-form-urlencoded' };
    // If SENDY_ORIGIN_SECRET is set, send it so .htaccess on SiteGround can
    // reject any request that didn't come through this proxy.
    if (originSecret) sendyHeaders['X-VH-Origin-Secret'] = originSecret;

    const r = await fetch(`${sendyUrl}/subscribe`, {
      method:  'POST',
      headers: sendyHeaders,
      body:    params.toString(),
    });

    const text = (await r.text()).trim();
    // Sendy responses: "1" = success, "Already subscribed." = duplicate, anything else = error
    if (text === '1') {
      rateLimits.set(ip, now);
      return res.end(JSON.stringify({ ok: true }));
    }
    if (text.toLowerCase().includes('already subscribed')) {
      rateLimits.set(ip, now);
      return res.end(JSON.stringify({ ok: true, alreadySubscribed: true }));
    }
    // Any other Sendy response is an error
    console.error('[subscribe] Sendy error:', text);
    res.statusCode = 502;
    return res.end(JSON.stringify({ error: 'Something went wrong. Please try again.' }));
  } catch (e) {
    console.error('[subscribe] fetch failed:', e?.message);
    res.statusCode = 500;
    return res.end(JSON.stringify({ error: 'Something went wrong. Please try again.' }));
  }
};

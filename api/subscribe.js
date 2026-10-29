// TheVegasHub.com — newsletter subscribe handler (Vercel serverless)
// Proxies to Sendy so the API key never touches the browser.
//
// Required env vars (set in Vercel Dashboard → Project Settings → Environment Variables):
//   SENDY_API_KEY   — your Sendy API key
//   SENDY_LIST_ID   — Sendy list ID (the hash shown in your Sendy list settings)
//   SENDY_URL       — base URL of your Sendy install, e.g. https://clubfluent.com/sendy
//   SMTP2GO_API_KEY — sends the "confirm you want back in" email to previously unsubscribed addresses
//
// Subscribes go through api/_lib/sendyConsent.js so an opt-out is never undone silently.

const { subscribeWithConsent, confirmEmailContent, sendViaSmtp2go } = require('./_lib/sendyConsent');

const SITE_URL = 'https://thevegashub.com';

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

  // ── Pull config from env (never from request) ──
  const listId = process.env.SENDY_LIST_ID;
  if (!process.env.SENDY_API_KEY || !listId || !process.env.SENDY_URL) {
    console.error('[subscribe] missing env vars — SENDY_API_KEY, SENDY_LIST_ID, or SENDY_URL not set');
    res.statusCode = 500;
    return res.end(JSON.stringify({ error: 'Newsletter signup is temporarily unavailable.' }));
  }

  // ── Subscribe without undoing an opt-out (see api/_lib/sendyConsent.js) ──
  // Previously unsubscribed addresses get an emailed confirm link instead.
  const outcome = await subscribeWithConsent({
    email,
    name: name || undefined,
    listId,
    mode: 'newsletter',
    siteUrl: SITE_URL,
    sendConfirmEmail: (to, url) => {
      const { subject, html, text } = confirmEmailContent('TheVegasHub', url);
      return sendViaSmtp2go({
        sender: process.env.CONTACT_FROM_EMAIL || 'no-reply@thevegashub.com',
        to, subject, html, text,
      });
    },
  });

  if (outcome === 'failed') {
    res.statusCode = 502;
    return res.end(JSON.stringify({ error: 'Something went wrong. Please try again.' }));
  }
  // Same response for every other outcome so the form never reveals who is or was on the list.
  rateLimits.set(ip, now);
  return res.end(JSON.stringify({ ok: true }));
};

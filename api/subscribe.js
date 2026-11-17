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

const { rateLimited, readJson, isEmail, sendJson } = require('./_lib/safe');

function sanitizeName(str) {
  if (typeof str !== 'string') return '';
  return str.replace(/<[^>]*>/g, '').replace(/[^\p{L}\p{N} .'\-]/gu, '').slice(0, 80).trim();
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return sendJson(res, 405, { error: 'Method not allowed.' });
  }

  // ── Rate limit: per IP, every attempt counts ──
  if (rateLimited(req, 'subscribe', 5, 10 * 60_000)) {
    return sendJson(res, 429, { error: 'Please wait a few minutes before trying again.' });
  }

  // ── Parse body ──
  const body = await readJson(req, 4000);
  if (!body) return sendJson(res, 400, { error: 'Invalid request.' });

  // ── Honeypot: silent success if bot fills the hidden field ──
  if (body.website || body.hp_field) return sendJson(res, 200, { ok: true });

  // ── Validate inputs ──
  const email = typeof body.email === 'string' ? body.email.slice(0, 254).trim().toLowerCase() : '';
  const name  = sanitizeName(body.name || '');

  if (!isEmail(email)) return sendJson(res, 400, { error: 'Please enter a valid email address.' });

  // ── Pull config from env (never from request) ──
  const listId = process.env.SENDY_LIST_ID;
  if (!process.env.SENDY_API_KEY || !listId || !process.env.SENDY_URL) {
    console.error('[subscribe] missing env vars — SENDY_API_KEY, SENDY_LIST_ID, or SENDY_URL not set');
    return sendJson(res, 503, { error: 'Newsletter signup is temporarily unavailable.' });
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

  if (outcome === 'failed') return sendJson(res, 502, { error: 'Something went wrong. Please try again.' });
  // Same response for every other outcome so the form never reveals who is or was on the list.
  return sendJson(res, 200, { ok: true });
};

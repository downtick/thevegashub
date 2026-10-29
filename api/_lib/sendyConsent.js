// Consent-aware Sendy subscribe (CommonJS port for plain Vercel functions).
// Canonical copy: websites/_reference/sendy-resubscribe-confirm/sendyConsent.ts
//
// Sendy's /subscribe silently re-activates an address that unsubscribed or
// complained, so any form (or a bot typing someone else's address) could undo
// an opt-out. This module checks the address's status first:
//
//   never on the list / unconfirmed  -> subscribe as normal
//   already subscribed               -> nothing to do
//   unsubscribed / complained        -> 'newsletter' mode: email a signed
//                                       "confirm you want back in" link;
//                                       'lead' mode: leave them off
//   bounced / soft bounced           -> leave them off
//
// Only the address owner can click the link, so a stranger can't re-subscribe
// them. The link opens a page with a button (POST), never a GET that
// subscribes, because mail scanners pre-fetch links.
//
// Env: SENDY_API_KEY (required; also keys the link signature), SENDY_URL
// (install base, default https://clubfluent.com/sendy), SENDY_ORIGIN_SECRET
// (optional header the install checks).
'use strict';
const { createHash, createHmac, timingSafeEqual } = require('node:crypto');

const LINK_DAYS = 7;
const REJOIN_STATUSES = new Set(['unsubscribed', 'complained']);
const NEVER_STATUSES = new Set(['bounced', 'soft bounced']);
const NEW_STATUSES = new Set(['email does not exist in list', 'unconfirmed']);

function base() {
  return (process.env.SENDY_URL || process.env.SENDY_BASE_URL || 'https://clubfluent.com/sendy').replace(/\/+$/, '');
}

function headers() {
  const originSecret = process.env.SENDY_ORIGIN_SECRET;
  return {
    'Content-Type': 'application/x-www-form-urlencoded',
    ...(originSecret ? { 'X-VH-Origin-Secret': originSecret } : {}),
  };
}

/** The address's status on a list, lower-cased, or null if it couldn't be read. */
async function sendyStatus(email, listId) {
  const apiKey = process.env.SENDY_API_KEY;
  if (!apiKey) return null;
  try {
    const res = await fetch(`${base()}/api/subscribers/subscription-status.php`, {
      method: 'POST',
      headers: headers(),
      body: new URLSearchParams({ api_key: apiKey, list_id: listId, email }).toString(),
    });
    const text = (await res.text()).trim().toLowerCase();
    const known = REJOIN_STATUSES.has(text) || NEVER_STATUSES.has(text) || NEW_STATUSES.has(text) || text === 'subscribed';
    return known ? text : null;
  } catch {
    return null;
  }
}

/** Calls Sendy /subscribe directly. Only call after a status check or a verified confirm link. */
async function rawSubscribe(email, listId, name, fields, brandId) {
  const form = new URLSearchParams({ email, list: listId, boolean: 'true' });
  if (name) form.set('name', name);
  if (brandId) form.set('brand_id', brandId);
  const apiKey = process.env.SENDY_API_KEY;
  if (apiKey) form.set('api_key', apiKey);
  for (const [k, v] of Object.entries(fields || {})) if (v) form.set(k, v);
  try {
    const res = await fetch(`${base()}/subscribe`, { method: 'POST', headers: headers(), body: form.toString() });
    const text = (await res.text()).trim().toLowerCase();
    const ok = text === '1' || text === 'true' || text.includes('already');
    if (!ok) console.error('[sendy] subscribe response:', text);
    return ok;
  } catch (e) {
    console.error('[sendy] subscribe failed', e && e.message);
    return false;
  }
}

// ── Signed confirm link ──────────────────────────────────────────────────────

function signingKey() {
  const apiKey = process.env.SENDY_API_KEY;
  return apiKey ? createHash('sha256').update(`sendy-resubscribe:${apiKey}`).digest() : null;
}

function sign(email, listId, exp) {
  const key = signingKey();
  if (!key) return null;
  return createHmac('sha256', key).update(`${email.toLowerCase()}\n${listId}\n${exp}`).digest('base64url');
}

function buildConfirmUrl(siteUrl, email, listId) {
  const exp = Math.floor(Date.now() / 1000) + LINK_DAYS * 86400;
  const s = sign(email, listId, exp);
  if (!s) return null;
  const q = new URLSearchParams({ e: email, l: listId, x: String(exp), s });
  return `${siteUrl.replace(/\/+$/, '')}/newsletter/confirm?${q.toString()}`;
}

/** Verifies the e/l/x/s values from a confirm link. Returns {ok:true,email,listId} or {ok:false,reason}. */
function verifyConfirm(e, l, x, s) {
  const email = String(e || '').trim();
  const listId = String(l || '').trim();
  const exp = Number(x);
  const sig = String(s || '');
  if (!email || !listId || !Number.isFinite(exp) || !sig) return { ok: false, reason: 'invalid' };
  const expected = sign(email, listId, exp);
  if (!expected) return { ok: false, reason: 'invalid' };
  const a = Buffer.from(sig);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !timingSafeEqual(a, b)) return { ok: false, reason: 'invalid' };
  if (exp < Date.now() / 1000) return { ok: false, reason: 'expired' };
  return { ok: true, email, listId };
}

// One confirm email per address per 10 minutes (per instance, best-effort).
const recentConfirms = new Map();
function confirmThrottled(email) {
  const now = Date.now();
  const key = email.toLowerCase();
  const last = recentConfirms.get(key);
  if (last && now - last < 10 * 60_000) return true;
  recentConfirms.set(key, now);
  if (recentConfirms.size > 5000) for (const [k, t] of recentConfirms) if (now - t > 10 * 60_000) recentConfirms.delete(k);
  return false;
}

/**
 * Subscribe with the opt-out respected. Resolves to 'subscribed' | 'already' |
 * 'confirm-sent' | 'skipped' | 'failed'. Show the visitor the same message for
 * every outcome except 'failed'.
 *
 * args: { email, name?, listId, fields?, mode: 'newsletter'|'lead',
 *         sendConfirmEmail?(to, url), siteUrl?, brandId? }
 */
async function subscribeWithConsent(args) {
  const { email, name, listId, fields, mode, brandId } = args;
  if (!listId || !email) return 'skipped';

  const status = await sendyStatus(email, listId);

  if (status === 'subscribed') return 'already';
  if (status && NEVER_STATUSES.has(status)) return 'skipped';

  if (status && NEW_STATUSES.has(status)) {
    return (await rawSubscribe(email, listId, name, fields, brandId)) ? 'subscribed' : 'failed';
  }

  // Previously opted out, or status unknown (API key missing / Sendy unreachable).
  if (mode === 'lead') return 'skipped';
  if (!args.sendConfirmEmail || !args.siteUrl) return 'skipped';
  if (confirmThrottled(email)) return 'confirm-sent';
  const url = buildConfirmUrl(args.siteUrl, email, listId);
  if (!url) return 'skipped';
  try {
    await args.sendConfirmEmail(email, url);
    return 'confirm-sent';
  } catch (e) {
    console.error('[sendy] confirm email failed', e && e.message);
    return 'failed';
  }
}

// ── Email copy ───────────────────────────────────────────────────────────────

const esc = (v) => v.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

/** Subject, HTML and text for the confirmation email. siteName is the site's own name (trusted). */
function confirmEmailContent(siteName, confirmUrl) {
  const subject = `Confirm you want to rejoin the ${siteName} newsletter`;
  const text = [
    `Someone (hopefully you) asked to rejoin the ${siteName} newsletter with this email address.`,
    `Because this address unsubscribed before, we won't add it back unless you confirm:`,
    confirmUrl,
    `The link works for ${LINK_DAYS} days. If this wasn't you, ignore this email and you'll stay unsubscribed.`,
  ].join('\n\n');
  const html = `<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.5;color:#222;max-width:560px">
<p>Someone (hopefully you) asked to rejoin the <strong>${esc(siteName)}</strong> newsletter with this email address.</p>
<p>Because this address unsubscribed before, we won't add it back unless you confirm.</p>
<p style="margin:24px 0"><a href="${esc(confirmUrl)}" style="background:#1a56db;color:#fff;text-decoration:none;padding:12px 22px;border-radius:6px;display:inline-block;font-weight:bold">Yes, resubscribe me</a></p>
<p style="color:#555;font-size:13px">The link works for ${LINK_DAYS} days. If this wasn't you, ignore this email and you'll stay unsubscribed.</p>
</div>`;
  return { subject, html, text };
}

/** Sends one email through the SMTP2GO HTTP API (SMTP2GO_API_KEY). Throws on failure. */
async function sendViaSmtp2go({ sender, to, subject, html, text }) {
  const apiKey = process.env.SMTP2GO_API_KEY;
  if (!apiKey) throw new Error('SMTP2GO_API_KEY not set');
  const r = await fetch('https://api.smtp2go.com/v3/email/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ api_key: apiKey, sender, to: [to], subject, html_body: html, text_body: text }),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok || (data && data.data && data.data.failed > 0)) throw new Error(`smtp2go ${r.status}`);
}

/** Reads a urlencoded/JSON POST body from a plain Vercel function request. */
async function readForm(req) {
  let body = req.body;
  if (body && typeof body === 'object' && !Buffer.isBuffer(body)) return body;
  let raw = typeof body === 'string' ? body : Buffer.isBuffer(body) ? body.toString('utf8') : '';
  if (!raw && !body) {
    raw = await new Promise((resolve, reject) => {
      let data = '';
      req.on('data', (c) => { data += c; if (data.length > 4000) req.destroy(); });
      req.on('end', () => resolve(data));
      req.on('error', reject);
    });
  }
  if (raw.trim().startsWith('{')) {
    try { return JSON.parse(raw); } catch { return {}; }
  }
  return Object.fromEntries(new URLSearchParams(raw));
}

/**
 * Handler for POST /api/newsletter-confirm: verifies the signed link values
 * from the confirm page's form and subscribes, then 303s back to the page.
 */
function confirmHandler(siteUrl) {
  return async (req, res) => {
    const back = (status) => {
      res.statusCode = 303;
      res.setHeader('Location', `${siteUrl}/newsletter/confirm?status=${status}`);
      res.setHeader('Cache-Control', 'no-store');
      res.end();
    };
    if (req.method !== 'POST') {
      res.statusCode = 405;
      res.setHeader('Allow', 'POST');
      return res.end();
    }
    let form;
    try {
      form = await readForm(req);
    } catch {
      return back('invalid');
    }
    const check = verifyConfirm(form.e, form.l, form.x, form.s);
    if (!check.ok) return back(check.reason);
    const ok = await rawSubscribe(check.email, check.listId);
    return back(ok ? 'ok' : 'error');
  };
}

module.exports = {
  sendyStatus,
  rawSubscribe,
  buildConfirmUrl,
  verifyConfirm,
  subscribeWithConsent,
  confirmEmailContent,
  sendViaSmtp2go,
  readForm,
  confirmHandler,
};

// Shared guards for the /api functions (underscore folder: not a route).
// Port of suretybondly api/_safe.js + runquotes lib/requestGuard.ts (CommonJS).
//
// rateLimited() is in-memory, so it is per function instance: it stops one
// client looping a form, not a distributed flood (Vercel Firewall handles that).
'use strict';

const hits = new Map();

function clientIp(req) {
  return String(req.headers['x-forwarded-for'] || req.headers['x-real-ip'] || req.socket?.remoteAddress || 'unknown')
    .split(',')[0].trim();
}

/** True when this IP has made more than `max` calls to `bucket` within `windowMs`. Counts every call. */
function rateLimited(req, bucket, max = 5, windowMs = 10 * 60_000) {
  const key = `${bucket}:${clientIp(req)}`;
  const now = Date.now();
  const recent = (hits.get(key) || []).filter((t) => now - t < windowMs);
  recent.push(now);
  hits.set(key, recent);
  if (hits.size > 5000) {
    for (const [k, v] of hits) if (!v.some((t) => now - t < windowMs)) hits.delete(k);
  }
  return recent.length > max;
}

/**
 * Reads a JSON (or urlencoded) POST body. Returns a plain object, or null when
 * the body is missing, too large, unparseable, or not an object.
 */
async function readJson(req, maxBytes = 20_000) {
  let body;
  try {
    body = req.body; // Vercel's getter throws on malformed JSON
  } catch {
    return null;
  }
  if (body && typeof body === 'object' && !Buffer.isBuffer(body)) return Array.isArray(body) ? null : body;
  let raw = typeof body === 'string' ? body : Buffer.isBuffer(body) ? body.toString('utf8') : null;
  if (raw === null) {
    if (body !== undefined || req.readableEnded || req.complete) return null; // already parsed/consumed (e.g. JSON null)
    try {
      raw = await new Promise((resolve, reject) => {
        let data = '';
        req.on('data', (c) => { data += c; if (data.length > maxBytes) reject(new Error('too large')); });
        req.on('end', () => resolve(data));
        req.on('error', reject);
      });
    } catch {
      return null;
    }
  }
  if (raw.length > maxBytes) return null;
  const t = raw.trim();
  if (!t) return null;
  try {
    const v = t.startsWith('{') ? JSON.parse(t) : Object.fromEntries(new URLSearchParams(t));
    return v && typeof v === 'object' && !Array.isArray(v) ? v : null;
  } catch {
    return null;
  }
}

/** A string field: trimmed and capped; non-strings become ''. */
function str(v, max = 200) {
  return typeof v === 'string' ? v.trim().slice(0, max) : '';
}

/** One line of text safe for an email subject/header: no CR/LF/control chars, capped. */
function oneLine(v, max = 150) {
  return String(v ?? '').replace(/[\u0000-\u001f\u007f]+/g, ' ').replace(/\s+/g, ' ').trim().slice(0, max);
}

/** HTML-escapes text for an email body. */
function escHtml(v) {
  return String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function isEmail(v) {
  return typeof v === 'string' && v.length <= 254 && /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(v);
}

/** Sends JSON with a status code. */
function sendJson(res, status, obj) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.end(JSON.stringify(obj));
}

module.exports = { clientIp, rateLimited, readJson, str, oneLine, escHtml, isEmail, sendJson };

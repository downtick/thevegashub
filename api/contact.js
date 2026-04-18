// TheVegasHub.com — contact form handler (Vercel serverless function)
// POST only. Sends via SMTP2GO API. Env vars required:
//   SMTP2GO_API_KEY   - set in Vercel project settings
//   CONTACT_TO_EMAIL  - recipient email for contact submissions

const rateLimits = new Map(); // IP -> last-submit timestamp (resets on cold-start; adequate for MVP)

function getClientIp(req) {
  const fwd = (req.headers['x-forwarded-for'] || '').split(',').map(s => s.trim()).filter(Boolean);
  return fwd[0] || req.socket?.remoteAddress || 'unknown';
}

function sanitize(str, maxLen = 2000) {
  if (typeof str !== 'string') return '';
  let out = str.slice(0, maxLen);
  // Strip HTML tags
  out = out.replace(/<[^>]*>/g, '');
  // Strip dangerous protocols
  out = out.replace(/javascript:/gi, '');
  out = out.replace(/data:/gi, '');
  out = out.replace(/vbscript:/gi, '');
  // Strip inline event handlers remnants
  out = out.replace(/on\w+\s*=/gi, '');
  // Escape HTML entities
  out = out
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;');
  return out.trim();
}

function isValidEmail(email) {
  if (typeof email !== 'string' || email.length > 254) return false;
  return /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(email);
}

module.exports = async (req, res) => {
  // Security headers
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Cache-Control', 'no-store');

  if (req.method !== 'POST') {
    res.statusCode = 405;
    return res.end(JSON.stringify({ error: 'Method not allowed' }));
  }

  // Rate limit: 30 seconds per IP
  const ip = getClientIp(req);
  const now = Date.now();
  const last = rateLimits.get(ip) || 0;
  if (now - last < 30_000) {
    console.error('[rate-limit] blocked ip=' + ip);
    res.statusCode = 429;
    return res.end(JSON.stringify({ error: 'Please wait a moment before submitting again.' }));
  }

  // Parse body (Vercel usually gives us req.body; handle both)
  let body = req.body;
  if (!body || typeof body === 'string') {
    try {
      let raw = '';
      if (typeof body === 'string') {
        raw = body;
      } else {
        raw = await new Promise((resolve, reject) => {
          let data = '';
          req.on('data', c => { data += c; if (data.length > 10000) req.destroy(); });
          req.on('end', () => resolve(data));
          req.on('error', reject);
        });
      }
      body = raw ? JSON.parse(raw) : {};
    } catch (e) {
      console.error('[contact] bad json');
      res.statusCode = 400;
      return res.end(JSON.stringify({ error: 'Invalid request body.' }));
    }
  }

  // Honeypot — silent success if triggered
  if (body.website || body.hp_field) {
    console.error('[contact] honeypot triggered ip=' + ip);
    rateLimits.set(ip, now);
    return res.end(JSON.stringify({ ok: true }));
  }

  // Sanitize + validate
  const name = sanitize(body.name, 120);
  const email = typeof body.email === 'string' ? body.email.slice(0, 254).trim() : '';
  const phone = sanitize(body.phone, 24);
  const subject = sanitize(body.subject, 180);
  const message = sanitize(body.message, 5000);
  const smsConsent = !!body.sms_consent;

  if (!name || name.length < 2) {
    res.statusCode = 400;
    return res.end(JSON.stringify({ error: 'Please provide your name.' }));
  }
  if (!isValidEmail(email)) {
    res.statusCode = 400;
    return res.end(JSON.stringify({ error: 'Please provide a valid email address.' }));
  }
  // Phone — keep digits only, require at least 7 digits
  const phoneDigits = phone.replace(/\D/g, '');
  if (phoneDigits.length < 7) {
    res.statusCode = 400;
    return res.end(JSON.stringify({ error: 'Please provide a valid phone number.' }));
  }
  if (!subject || subject.length < 2) {
    res.statusCode = 400;
    return res.end(JSON.stringify({ error: 'Please include a subject.' }));
  }
  if (!message || message.length < 5) {
    res.statusCode = 400;
    return res.end(JSON.stringify({ error: 'Please include a message.' }));
  }
  if (!smsConsent) {
    res.statusCode = 400;
    return res.end(JSON.stringify({ error: 'SMS consent is required to submit this form.' }));
  }

  const apiKey = process.env.SMTP2GO_API_KEY;
  const toEmail = process.env.CONTACT_TO_EMAIL || 'contact@thevegashub.com';
  const fromEmail = process.env.CONTACT_FROM_EMAIL || 'no-reply@thevegashub.com';

  if (!apiKey) {
    console.error('[contact] missing SMTP2GO_API_KEY env var');
    res.statusCode = 500;
    return res.end(JSON.stringify({ error: 'Something went wrong. Please try again later.' }));
  }

  const rawMessage = body.message?.slice(0, 5000) || '';
  const payload = {
    api_key: apiKey,
    to: [toEmail],
    sender: fromEmail,
    subject: `[TheVegasHub] ${subject}`,
    text_body: `From: ${name} <${email}>\nPhone: ${phone}\nSMS consent: YES — user agreed to receive a text message regarding this specific inquiry (standard message & data rates apply)\n\n${rawMessage}\n\n---\nIP: ${ip}\nUA: ${req.headers['user-agent'] || ''}`,
    html_body: `<p><strong>From:</strong> ${name} &lt;${email}&gt;</p><p><strong>Phone:</strong> ${phone}</p><p><strong>SMS consent:</strong> YES — user agreed to receive a text message regarding this specific inquiry (standard message &amp; data rates apply)</p><p>${message.replace(/\n/g, '<br>')}</p><hr><p style="font-size:11px;color:#888">IP: ${ip}</p>`,
  };

  try {
    const r = await fetch('https://api.smtp2go.com/v3/email/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await r.json().catch(() => ({}));
    if (!r.ok || data?.data?.failed > 0) {
      console.error('[contact] smtp2go error', r.status, JSON.stringify(data));
      res.statusCode = 502;
      return res.end(JSON.stringify({ error: 'Something went wrong. Please try again later.' }));
    }
    rateLimits.set(ip, now);
    return res.end(JSON.stringify({ ok: true }));
  } catch (e) {
    console.error('[contact] fetch failed', e?.message);
    res.statusCode = 500;
    return res.end(JSON.stringify({ error: 'Something went wrong. Please try again later.' }));
  }
};

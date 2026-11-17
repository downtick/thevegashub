// TheVegasHub.com — contact form handler (Vercel serverless function)
// POST only. Sends via SMTP2GO API. Env vars required:
//   SMTP2GO_API_KEY   - set in Vercel project settings
//   CONTACT_TO_EMAIL  - recipient email for contact submissions
//
// Fails loud: if the email can't be sent the visitor gets a 5xx and an error
// message, never a fake "thanks".

const { clientIp, rateLimited, readJson, str, oneLine, escHtml, isEmail, sendJson } = require('./_lib/safe');

const FAIL_MSG = "Sorry, we couldn't send your message right now. Please try again in a few minutes.";

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return sendJson(res, 405, { error: 'Method not allowed' });
  }

  const ip = clientIp(req);
  if (rateLimited(req, 'contact', 6, 10 * 60_000)) {
    console.error('[rate-limit] contact blocked ip=' + ip);
    return sendJson(res, 429, { error: 'Too many messages — please wait a few minutes and try again.' });
  }

  const body = await readJson(req, 20_000);
  if (!body) return sendJson(res, 400, { error: 'Invalid request body.' });

  // Honeypot — silent success if triggered (never tell bots)
  if (body.website || body.hp_field) {
    console.error('[contact] honeypot triggered ip=' + ip);
    return sendJson(res, 200, { ok: true });
  }

  const name = oneLine(str(body.name, 120), 120);
  const email = str(body.email, 254);
  const phone = oneLine(str(body.phone, 24), 24);
  const subject = oneLine(str(body.subject, 180), 180);
  const message = str(body.message, 5000);
  const smsConsent = body.sms_consent === true || body.sms_consent === 'on' || body.sms_consent === 'true';

  if (name.length < 2) return sendJson(res, 400, { error: 'Please provide your name.' });
  if (!isEmail(email)) return sendJson(res, 400, { error: 'Please provide a valid email address.' });
  const phoneDigits = phone.replace(/\D/g, '');
  if (phoneDigits.length < 7 || phoneDigits.length > 15) return sendJson(res, 400, { error: 'Please provide a valid phone number.' });
  if (subject.length < 2) return sendJson(res, 400, { error: 'Please include a subject.' });
  if (message.length < 5) return sendJson(res, 400, { error: 'Please include a message.' });
  if (!smsConsent) return sendJson(res, 400, { error: 'SMS consent is required to submit this form.' });

  const apiKey = process.env.SMTP2GO_API_KEY;
  const toEmail = process.env.CONTACT_TO_EMAIL || 'contact@thevegashub.com';
  const fromEmail = process.env.CONTACT_FROM_EMAIL || 'no-reply@thevegashub.com';

  if (!apiKey) {
    console.error('[contact] missing SMTP2GO_API_KEY env var');
    return sendJson(res, 503, { error: FAIL_MSG });
  }

  const payload = {
    api_key: apiKey,
    to: [toEmail],
    sender: fromEmail,
    custom_headers: [{ header: 'Reply-To', value: email }],
    subject: oneLine(`[TheVegasHub] ${subject}`, 200),
    text_body: `From: ${name} <${email}>\nPhone: ${phone}\nSMS consent: YES — user agreed to receive a text message regarding this specific inquiry (standard message & data rates apply)\n\n${message}\n\n---\nIP: ${ip}\nUA: ${oneLine(req.headers['user-agent'] || '', 300)}`,
    html_body: `<p><strong>From:</strong> ${escHtml(name)} &lt;${escHtml(email)}&gt;</p><p><strong>Phone:</strong> ${escHtml(phone)}</p><p><strong>SMS consent:</strong> YES — user agreed to receive a text message regarding this specific inquiry (standard message &amp; data rates apply)</p><p>${escHtml(message).replace(/\r?\n/g, '<br>')}</p><hr><p style="font-size:11px;color:#888">IP: ${escHtml(ip)}</p>`,
  };

  try {
    const r = await fetch('https://api.smtp2go.com/v3/email/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await r.json().catch(() => ({}));
    if (!r.ok || !data?.data || data.data.failed > 0 || !(data.data.succeeded > 0)) {
      console.error('[contact] smtp2go error', r.status, JSON.stringify(data?.data?.error || data?.data?.failures || ''));
      return sendJson(res, 502, { error: FAIL_MSG });
    }
    return sendJson(res, 200, { ok: true });
  } catch (e) {
    console.error('[contact] fetch failed', e?.message);
    return sendJson(res, 502, { error: FAIL_MSG });
  }
};

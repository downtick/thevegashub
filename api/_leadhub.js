// Lead Hub client — plain-JS twin of leadhub.ts, for static sites with Vercel
// `api/*.js` functions (SuretyBondly, HoodCleaner, etc.). Copy into the site's
// `api/` folder as `_leadhub.js` (leading underscore = not a route).
// CommonJS copy (this site's api/ files use require/module.exports).
//
// Never throws, never blocks the lead email: 4s timeout, one retry with the
// same externalId, no-op until LEADHUB_URL + LEADHUB_INGEST_KEY are set
// (not "Sensitive" in Vercel).
//
// ALWAYS send tracking.pageUrl and tracking.referrer (the page the form was
// on, and document.referrer captured client-side) — Lead Hub reports on both.

async function sendToLeadHub(payload) {
  const base = process.env.LEADHUB_URL;
  const key = process.env.LEADHUB_INGEST_KEY;
  if (!base || !key) return false;

  const body = JSON.stringify({
    ...payload,
    externalId: payload.externalId || (globalThis.crypto && crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random()),
  });
  const url = base.replace(/\/+$/, '') + '/api/ingest';

  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${key}` },
        body,
        signal: AbortSignal.timeout(4000),
      });
      if (res.ok) return true;
      if (res.status < 500) {
        console.error('Lead Hub rejected lead:', res.status, (await res.text()).slice(0, 500));
        return false;
      }
    } catch (err) {
      if (attempt === 1) console.error('Lead Hub unreachable:', err);
    }
  }
  return false;
}

/**
 * Build `sections` from a flat object when a site has no section builder.
 * rowsByTitle: { "Applicant": [["Name", "Jane"], ...], ... } — empty values dropped.
 */
function sectionsFrom(rowsByTitle) {
  return Object.entries(rowsByTitle)
    .map(([title, rows]) => ({
      title,
      rows: rows
        .filter(([, v]) => v !== undefined && v !== null && String(v).trim() !== '')
        .map(([k, v]) => [String(k), String(v)]),
    }))
    .filter((s) => s.rows.length);
}

module.exports = { sendToLeadHub, sectionsFrom };

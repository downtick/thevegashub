// TheVegasHub.com — finishes a newsletter re-subscribe after the owner clicked
// the emailed link and pressed the button on /newsletter/confirm. POST only.
const { confirmHandler } = require('./_lib/sendyConsent');
const { rateLimited } = require('./_lib/safe');

const handler = confirmHandler('https://thevegashub.com');

module.exports = (req, res) => {
  if (rateLimited(req, 'nl-confirm', 10, 10 * 60_000)) {
    res.statusCode = 429;
    res.setHeader('Cache-Control', 'no-store');
    return res.end('Too many requests');
  }
  return handler(req, res);
};

// TheVegasHub.com — finishes a newsletter re-subscribe after the owner clicked
// the emailed link and pressed the button on /newsletter/confirm. POST only.
const { confirmHandler } = require('./_lib/sendyConsent');

module.exports = confirmHandler('https://thevegashub.com');

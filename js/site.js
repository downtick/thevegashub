// TheVegasHub.com — shared site JS

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.site-nav');
  if (btn && nav) {
    btn.addEventListener('click', () => nav.classList.toggle('open'));
  }

  // Current-year in footer
  document.querySelectorAll('[data-current-year]').forEach(el => {
    el.textContent = new Date().getFullYear();
  });
});

// Share button — uses native Web Share API; falls back to clipboard + social links
window.VegasHub = window.VegasHub || {};
window.VegasHub.share = async function(title, text, url) {
  url = url || window.location.href;
  title = title || document.title;
  text = text || (document.querySelector('meta[name="description"]')?.content || '');

  if (navigator.share) {
    try {
      await navigator.share({ title, text, url });
      return;
    } catch (e) {
      if (e.name === 'AbortError') return;
      // fall through to fallback
    }
  }
  // Fallback: copy to clipboard + show toast
  try {
    await navigator.clipboard.writeText(url);
    const toast = document.createElement('div');
    toast.textContent = 'Link copied to clipboard!';
    toast.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#bf00ff;color:#fff;padding:12px 24px;border-radius:6px;z-index:9999;font-family:Bungee,sans-serif;box-shadow:0 0 16px #bf00ff;';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2500);
  } catch (e) {
    // final fallback: open a prompt
    window.prompt('Copy this link:', url);
  }
};

// Social share menu
window.VegasHub.shareMenu = function() {
  const url = encodeURIComponent(window.location.href);
  const title = encodeURIComponent(document.title);
  const wrap = document.getElementById('share-menu');
  if (!wrap) return;
  wrap.classList.toggle('hidden');
};

// Print helper
window.VegasHub.print = function() { window.print(); };

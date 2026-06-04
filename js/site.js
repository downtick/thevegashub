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

// ---- Accessibility Widget ----
(function() {
  const STORAGE_KEY = 'vh_a11y';
  const defaults = { fontSize: 0, contrast: 'default', spacing: false, dyslexia: false };

  function load() {
    try { return Object.assign({}, defaults, JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')); }
    catch(e) { return Object.assign({}, defaults); }
  }
  function save(prefs) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs)); } catch(e) {}
  }

  function apply(prefs) {
    const html = document.documentElement;
    // Font size: 0 = default, 1 = large (+20%), 2 = x-large (+40%)
    const scales = ['1', '1.2', '1.4'];
    html.style.fontSize = prefs.fontSize > 0 ? (16 * parseFloat(scales[prefs.fontSize])) + 'px' : '';
    // Contrast
    html.setAttribute('data-contrast', prefs.contrast);
    // Letter spacing
    html.classList.toggle('a11y-spacing', !!prefs.spacing);
    // Dyslexia font
    html.classList.toggle('a11y-dyslexia', !!prefs.dyslexia);
  }

  function buildWidget() {
    if (document.getElementById('vh-a11y-widget')) return;
    const prefs = load();

    const btn = document.createElement('button');
    btn.id = 'vh-a11y-btn';
    btn.setAttribute('aria-label', 'Accessibility options');
    btn.setAttribute('aria-expanded', 'false');
    btn.innerHTML = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/><circle cx="12" cy="5" r="1" fill="currentColor"/><path d="M9 11h6M10 16l-1 3M14 16l1 3"/></svg>';

    const panel = document.createElement('div');
    panel.id = 'vh-a11y-widget';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', 'Accessibility options');
    panel.setAttribute('aria-modal', 'false');
    panel.hidden = true;

    panel.innerHTML = `
      <div class="a11y-header">
        <span>Accessibility</span>
        <button class="a11y-close" aria-label="Close accessibility panel">&times;</button>
      </div>
      <div class="a11y-section">
        <div class="a11y-label">Text Size</div>
        <div class="a11y-row">
          <button class="a11y-fs-btn" data-size="0" aria-pressed="${prefs.fontSize===0}">Default</button>
          <button class="a11y-fs-btn" data-size="1" aria-pressed="${prefs.fontSize===1}">Large</button>
          <button class="a11y-fs-btn" data-size="2" aria-pressed="${prefs.fontSize===2}">X-Large</button>
        </div>
      </div>
      <div class="a11y-section">
        <div class="a11y-label">Colour Mode</div>
        <div class="a11y-row">
          <button class="a11y-contrast-btn" data-contrast="default" aria-pressed="${prefs.contrast==='default'}">Default</button>
          <button class="a11y-contrast-btn" data-contrast="high" aria-pressed="${prefs.contrast==='high'}">High Contrast</button>
          <button class="a11y-contrast-btn" data-contrast="dark" aria-pressed="${prefs.contrast==='dark'}">Dark+</button>
        </div>
      </div>
      <div class="a11y-section">
        <label class="a11y-toggle-row">
          <span>Extra Letter Spacing</span>
          <span class="a11y-switch">
            <input type="checkbox" id="a11y-spacing" ${prefs.spacing ? 'checked' : ''}>
            <span class="a11y-slider"></span>
          </span>
        </label>
        <label class="a11y-toggle-row" style="margin-top:10px;">
          <span>Dyslexia-Friendly Font</span>
          <span class="a11y-switch">
            <input type="checkbox" id="a11y-dyslexia" ${prefs.dyslexia ? 'checked' : ''}>
            <span class="a11y-slider"></span>
          </span>
        </label>
      </div>
      <button class="a11y-reset">Reset to Default</button>`;

    const wrap = document.createElement('div');
    wrap.id = 'vh-a11y-wrap';
    wrap.appendChild(btn);
    wrap.appendChild(panel);
    document.body.appendChild(wrap);

    // Toggle panel
    btn.addEventListener('click', () => {
      const open = panel.hidden;
      panel.hidden = !open;
      btn.setAttribute('aria-expanded', String(open));
    });
    panel.querySelector('.a11y-close').addEventListener('click', () => {
      panel.hidden = true;
      btn.setAttribute('aria-expanded', 'false');
    });

    // Font size buttons
    panel.querySelectorAll('.a11y-fs-btn').forEach(b => {
      b.addEventListener('click', () => {
        prefs.fontSize = parseInt(b.dataset.size);
        panel.querySelectorAll('.a11y-fs-btn').forEach(x => x.setAttribute('aria-pressed', 'false'));
        b.setAttribute('aria-pressed', 'true');
        apply(prefs); save(prefs);
      });
    });

    // Contrast buttons
    panel.querySelectorAll('.a11y-contrast-btn').forEach(b => {
      b.addEventListener('click', () => {
        prefs.contrast = b.dataset.contrast;
        panel.querySelectorAll('.a11y-contrast-btn').forEach(x => x.setAttribute('aria-pressed', 'false'));
        b.setAttribute('aria-pressed', 'true');
        apply(prefs); save(prefs);
      });
    });

    // Toggles
    panel.querySelector('#a11y-spacing').addEventListener('change', e => {
      prefs.spacing = e.target.checked; apply(prefs); save(prefs);
    });
    panel.querySelector('#a11y-dyslexia').addEventListener('change', e => {
      prefs.dyslexia = e.target.checked; apply(prefs); save(prefs);
    });

    // Reset
    panel.querySelector('.a11y-reset').addEventListener('click', () => {
      Object.assign(prefs, defaults);
      panel.querySelectorAll('.a11y-fs-btn').forEach(b => b.setAttribute('aria-pressed', b.dataset.size === '0' ? 'true' : 'false'));
      panel.querySelectorAll('.a11y-contrast-btn').forEach(b => b.setAttribute('aria-pressed', b.dataset.contrast === 'default' ? 'true' : 'false'));
      panel.querySelector('#a11y-spacing').checked = false;
      panel.querySelector('#a11y-dyslexia').checked = false;
      apply(prefs); save(prefs);
    });

    // Close on outside click
    document.addEventListener('click', e => {
      if (!wrap.contains(e.target)) panel.hidden = true;
    });

    apply(prefs);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildWidget);
  } else {
    buildWidget();
  }
})();

// ---- Cookie consent ----
(function() {
  const COOKIE_KEY = 'vh_cookie_consent';
  function get() { try { return localStorage.getItem(COOKIE_KEY); } catch(e){return null;} }
  function set(v) { try { localStorage.setItem(COOKIE_KEY, v); } catch(e){} }
  function showBanner() {
    const b = document.getElementById('vh-cookies');
    if (b) b.style.display = 'block';
  }
  function hideBanner() {
    const b = document.getElementById('vh-cookies');
    if (b) b.style.display = 'none';
  }
  function onReady() {
    const choice = get();
    if (choice === 'accept') {
      if (window.__loadGA) window.__loadGA();
    } else if (choice === 'reject') {
      // do nothing — essential only
    } else {
      // first visit — show banner
      showBanner();
    }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', onReady);
  } else {
    onReady();
  }
  window.VegasHub.cookies = function(choice) {
    set(choice);
    hideBanner();
    if (choice === 'accept' && window.__loadGA) window.__loadGA();
  };
})();

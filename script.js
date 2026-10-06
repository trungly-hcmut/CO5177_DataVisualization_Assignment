const menuToggle = document.querySelector('.menu-toggle');
const siteNav = document.querySelector('.site-nav');

menuToggle?.addEventListener('click', () => {
  const isOpen = siteNav.classList.toggle('open');
  menuToggle.setAttribute('aria-expanded', String(isOpen));
  menuToggle.querySelector('span').textContent = isOpen ? '−' : '+';
});

document.querySelectorAll('.site-nav a').forEach((link) => {
  link.addEventListener('click', () => {
    siteNav.classList.remove('open');
    menuToggle?.setAttribute('aria-expanded', 'false');
    const icon = menuToggle?.querySelector('span');
    if (icon) icon.textContent = '+';
  });
});

const revealItems = document.querySelectorAll('.reveal');
const revealObserver = new IntersectionObserver((entries, observer) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.14 });

revealItems.forEach((item) => revealObserver.observe(item));

// Light / dark mode: the <head> script sets data-theme before paint; this keeps it in sync.
const root = document.documentElement;
const themeToggle = document.querySelector('.theme-toggle');
const syncThemeLabel = () => {
  const dark = root.getAttribute('data-theme') === 'dark';
  themeToggle?.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
};
syncThemeLabel();

themeToggle?.addEventListener('click', () => {
  const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  root.setAttribute('data-theme', next);
  try { localStorage.setItem('g3-theme', next); } catch (e) { /* storage unavailable: theme lasts for this page only */ }
  syncThemeLabel();
});

// Follow the system setting until the visitor picks a theme themselves.
window.matchMedia?.('(prefers-color-scheme: dark)').addEventListener?.('change', (event) => {
  let saved = null;
  try { saved = localStorage.getItem('g3-theme'); } catch (e) { /* ignore */ }
  if (!saved) {
    root.setAttribute('data-theme', event.matches ? 'dark' : 'light');
    syncThemeLabel();
  }
});

(() => {
  'use strict';
  const root = document.documentElement;
  const storageKey = 'portfolio-theme';
  let currentTheme = 'dark';

  const readTheme = () => {
    try { return localStorage.getItem(storageKey) === 'light' ? 'light' : 'dark'; }
    catch { return 'dark'; }
  };
  const applyTheme = (theme) => {
    currentTheme = theme;
    root.dataset.theme = theme;
    const color = document.querySelector('meta[name="theme-color"]');
    if (color) color.content = theme === 'light' ? '#f6f6f2' : '#101113';
    const button = document.querySelector('.theme-toggle');
    if (button) {
      const label = theme === 'light' ? 'Включить тёмную тему' : 'Включить светлую тему';
      button.setAttribute('aria-label', label);
      button.title = label;
    }
  };

  // This small head script applies the saved choice before styles are painted.
  applyTheme(readTheme());
  document.addEventListener('DOMContentLoaded', () => {
    const button = document.querySelector('.theme-toggle');
    if (!button) return;
    applyTheme(currentTheme);
    button.hidden = false;
    button.addEventListener('click', () => {
      applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
      try { localStorage.setItem(storageKey, currentTheme); } catch {}
    });
  });
  // Keep cached pages and other open portfolio tabs in sync with the saved choice.
  window.addEventListener('pageshow', () => applyTheme(readTheme()));
  window.addEventListener('storage', (event) => {
    if (event.key === storageKey || event.key === null) applyTheme(readTheme());
  });
})();

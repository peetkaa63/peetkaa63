(() => {
  'use strict';

  const menuButton = document.querySelector('.menu-toggle');
  const menu = document.querySelector('#mobile-nav');
  const mobile = window.matchMedia('(max-width: 760px)');

  if (menuButton && menu) {
    menuButton.hidden = false;
    menu.hidden = true;

    const closeMenu = (restoreFocus = false) => {
      menu.hidden = true;
      menuButton.setAttribute('aria-expanded', 'false');
      menuButton.setAttribute('aria-label', 'Открыть меню');
      if (restoreFocus) menuButton.focus();
    };

    menuButton.addEventListener('click', () => {
      const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
      menu.hidden = isOpen;
      menuButton.setAttribute('aria-expanded', String(!isOpen));
      menuButton.setAttribute('aria-label', isOpen ? 'Открыть меню' : 'Закрыть меню');
    });
    menu.addEventListener('click', (event) => {
      if (event.target.closest('a')) closeMenu();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && !menu.hidden) closeMenu(true);
    });
    document.addEventListener('click', (event) => {
      if (!menu.hidden && !event.target.closest('.site-header')) closeMenu();
    });
    document.addEventListener('focusin', (event) => {
      if (!menu.hidden && !event.target.closest('.site-header')) closeMenu();
    });
    mobile.addEventListener('change', () => closeMenu());
  }

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const reveals = document.querySelectorAll('.reveal');
  let observer;

  const showEverything = () => {
    observer?.disconnect();
    document.documentElement.classList.remove('motion-ready');
    reveals.forEach((element) => element.classList.add('is-visible'));
  };

  const prepareReveals = () => {
    if (reducedMotion.matches || !('IntersectionObserver' in window)) {
      showEverything();
      return;
    }
    observer?.disconnect();
    observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.08, rootMargin: '0px 0px 32px 0px' });
    document.documentElement.classList.add('motion-ready');
    reveals.forEach((element) => observer.observe(element));
  };

  // Keep keyboard navigation visible even before a section enters the viewport.
  document.addEventListener('focusin', (event) => {
    event.target.closest('.reveal')?.classList.add('is-visible');
  });
  prepareReveals();
  reducedMotion.addEventListener('change', showEverything);

  const copyButton = document.querySelector('[data-copy]');
  const feedback = document.querySelector('.copy-feedback');
  if (copyButton && feedback && window.isSecureContext && navigator.clipboard?.writeText) {
    copyButton.hidden = false;
    copyButton.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(copyButton.dataset.copy);
        feedback.textContent = 'Скопировано: @rove63';
      } catch {
        feedback.textContent = 'Скопируйте имя вручную: @rove63';
      }
    });
  }
})();

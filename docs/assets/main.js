(() => {
  'use strict';
  document.documentElement.classList.add('js-ready');

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
  const motionButton = document.querySelector('.motion-toggle');
  let manualReducedMotion = false;
  try { manualReducedMotion = localStorage.getItem('portfolio-reduced-motion') === 'true'; } catch {}
  const reveals = document.querySelectorAll('.reveal');
  let observer;

  const showEverything = () => {
    observer?.disconnect();
    document.documentElement.classList.remove('motion-ready');
    reveals.forEach((element) => element.classList.add('is-visible'));
  };

  const prepareReveals = () => {
    if (reducedMotion.matches || manualReducedMotion || !('IntersectionObserver' in window)) {
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
  const applyMotionPreference = () => {
    document.documentElement.classList.toggle('reduce-motion', manualReducedMotion);
    if (motionButton) {
      motionButton.hidden = reducedMotion.matches;
      motionButton.setAttribute('aria-pressed', String(manualReducedMotion));
    }
    prepareReveals();
  };
  motionButton?.addEventListener('click', () => {
    manualReducedMotion = !manualReducedMotion;
    try { localStorage.setItem('portfolio-reduced-motion', String(manualReducedMotion)); } catch {}
    applyMotionPreference();
  });
  applyMotionPreference();
  reducedMotion.addEventListener('change', applyMotionPreference);

  if (window.isSecureContext && navigator.clipboard?.writeText) {
    document.querySelectorAll('[data-copy]').forEach((copyButton) => {
      const feedback = document.getElementById(copyButton.dataset.feedback);
      if (!feedback) return;
      copyButton.hidden = false;
      copyButton.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(copyButton.dataset.copy);
          feedback.textContent = copyButton.dataset.success;
        } catch {
          feedback.textContent = copyButton.dataset.copy === '@rove63'
            ? 'Скопируйте имя вручную: @rove63'
            : 'Копирование недоступно. Используйте пункты выше как шаблон.';
        }
      });
    });
  }

  const viewer = document.querySelector('.project-viewer');
  const previews = [...document.querySelectorAll('.project-media')];
  if (viewer && typeof viewer.showModal === 'function' && previews.length) {
    const image = viewer.querySelector('.viewer-image');
    const title = viewer.querySelector('#viewer-title');
    const counter = viewer.querySelector('.viewer-counter');
    let selected = 0;
    let opener;

    const showPreview = (index) => {
      selected = (index + previews.length) % previews.length;
      const preview = previews[selected];
      const source = preview.querySelector('img');
      image.src = preview.href;
      image.alt = source.alt;
      viewer.querySelector('.viewer-original').href = preview.href;
      title.textContent = preview.closest('.project-card').querySelector('.project-heading a').firstChild.textContent;
      counter.textContent = `${selected + 1} из ${previews.length}`;
    };
    previews.forEach((preview, index) => {
      preview.setAttribute('aria-haspopup', 'dialog');
      preview.setAttribute('aria-label', preview.getAttribute('aria-label').replace(' в новой вкладке', ''));
      preview.addEventListener('click', (event) => {
        // Preserve modified clicks, including opening the original image in a new tab.
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        opener = preview;
        showPreview(index);
        viewer.showModal();
        viewer.scrollTop = 0;
        document.documentElement.classList.add('viewer-open');
      });
    });
    viewer.querySelector('.viewer-close').addEventListener('click', () => viewer.close());
    viewer.querySelector('.viewer-prev').addEventListener('click', () => showPreview(selected - 1));
    viewer.querySelector('.viewer-next').addEventListener('click', () => showPreview(selected + 1));
    viewer.addEventListener('keydown', (event) => {
      if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
        event.preventDefault();
        showPreview(selected + (event.key === 'ArrowRight' ? 1 : -1));
      }
    });
    viewer.addEventListener('click', (event) => {
      const bounds = viewer.getBoundingClientRect();
      if (event.target === viewer && (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom)) viewer.close();
    });
    viewer.addEventListener('close', () => {
      document.documentElement.classList.remove('viewer-open');
      opener?.focus({ preventScroll: true });
    });
  }

  const header = document.querySelector('.site-header');
  const sections = [...document.querySelectorAll('main > section[id]')];
  const navLinks = [...document.querySelectorAll('.desktop-nav a, .mobile-nav a')];
  let scrollPending = false;
  const updateScroll = () => {
    scrollPending = false;
    const root = document.documentElement;
    const distance = root.scrollHeight - root.clientHeight;
    header?.style.setProperty('--reading-progress', distance > 0 ? String(Math.min(1, Math.max(0, window.scrollY / distance))) : '0');
    let current;
    sections.forEach((section) => {
      if (section.getBoundingClientRect().top <= (header?.offsetHeight || 88) + 100) current = section.id;
    });
    navLinks.forEach((link) => {
      if (link.hash === `#${current}`) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  };
  const queueScrollUpdate = () => {
    if (scrollPending) return;
    scrollPending = true;
    requestAnimationFrame(updateScroll);
  };
  window.addEventListener('scroll', queueScrollUpdate, { passive: true });
  window.addEventListener('resize', queueScrollUpdate, { passive: true });
  document.addEventListener('toggle', queueScrollUpdate, true);
  document.fonts?.ready.then(queueScrollUpdate);
  queueScrollUpdate();
})();

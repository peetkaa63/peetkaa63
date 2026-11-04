(() => {
  'use strict';
  document.documentElement.classList.add('js-ready');

  const profilePrint = document.querySelector('[data-print-profile]');
  if (profilePrint && typeof window.print === 'function') {
    profilePrint.hidden = false;
    profilePrint.addEventListener('click', () => window.print());
  }

  const menuButton = document.querySelector('.menu-toggle');
  const menu = document.querySelector('#mobile-nav');
  const mobile = window.matchMedia('(max-width: 760px)');

  const isPlainClick = (event) => event.button === 0 &&
    !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey;
  const focusTarget = (target) => {
    if (!target) return;
    if (!target.matches('a, button, input, select, textarea, summary, [tabindex]')) {
      target.setAttribute('tabindex', '-1');
      target.addEventListener('blur', () => target.removeAttribute('tabindex'), { once: true });
    }
    target.focus({ preventScroll: true });
  };

  // Native fragment navigation scrolls; also move keyboard focus into the section.
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[href^="#"]');
    if (!link || !isPlainClick(event) || event.defaultPrevented) return;
    let target;
    try { target = document.getElementById(decodeURIComponent(link.hash.slice(1))); } catch { return; }
    if (!target) return;
    requestAnimationFrame(() => focusTarget(target));
  });

  if (menuButton && menu) {
    menuButton.hidden = false;
    menu.hidden = true;
    let lastNavigationFocus;

    const closeMenu = (restoreFocus = false) => {
      lastNavigationFocus = undefined;
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
      if (isPlainClick(event) && event.target.closest('a')) closeMenu();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && !menu.hidden) closeMenu(true);
    });
    document.addEventListener('click', (event) => {
      if (!menu.hidden && !event.target.closest('.site-header')) closeMenu();
    });
    document.addEventListener('focusin', (event) => {
      lastNavigationFocus = event.target.closest('#mobile-nav a, .desktop-nav a');
      if (!menu.hidden && !event.target.closest('.site-header')) closeMenu();
    });
    mobile.addEventListener('change', () => {
      // CSS can blur a link before matchMedia's change event is dispatched.
      const active = document.activeElement === document.body
        ? (lastNavigationFocus || document.activeElement)
        : document.activeElement;
      const fromMobileMenu = menu.contains(active);
      const fromDesktopMenu = active.closest('.desktop-nav');
      closeMenu();
      if (!mobile.matches && fromMobileMenu) {
        const equivalent = [...document.querySelectorAll('.desktop-nav a')]
          .find((link) => link.hash === active.hash);
        (equivalent || document.querySelector('.header-contact') || menuButton).focus();
      } else if (mobile.matches && fromDesktopMenu) {
        menuButton.focus();
      }
    });
  }

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const motionButton = document.querySelector('.motion-toggle');
  let manualReducedMotion = false;
  let unsavedMotion = false;
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
    try {
      localStorage.setItem('portfolio-reduced-motion', String(manualReducedMotion));
      unsavedMotion = false;
    } catch { unsavedMotion = true; }
    applyMotionPreference();
  });
  applyMotionPreference();
  reducedMotion.addEventListener('change', applyMotionPreference);
  const restoreMotionPreference = () => {
    if (!unsavedMotion) {
      try { manualReducedMotion = localStorage.getItem('portfolio-reduced-motion') === 'true'; } catch {}
    }
    applyMotionPreference();
  };
  window.addEventListener('pageshow', restoreMotionPreference);
  window.addEventListener('storage', (event) => {
    if (event.key === 'portfolio-reduced-motion' || event.key === null) restoreMotionPreference();
  });

  if (window.isSecureContext && navigator.clipboard?.writeText) {
    const copyButtons = [...document.querySelectorAll('[data-copy]')];
    let copyPending = false;
    copyButtons.forEach((copyButton) => {
      const feedback = document.getElementById(copyButton.dataset.feedback);
      if (!feedback) return;
      copyButton.hidden = false;
      copyButton.addEventListener('click', async () => {
        // A pending OS write cannot be cancelled. Serialize writes across controls.
        if (copyPending || copyButton.getAttribute('aria-disabled') === 'true') return;
        copyPending = true;
        const disabledStates = copyButtons.map((button) => [button, button.getAttribute('aria-disabled')]);
        copyButtons.forEach((button) => button.setAttribute('aria-disabled', 'true'));
        copyButton.setAttribute('aria-busy', 'true');
        const label = copyButton.matches('.brief-copy') ? copyButton.textContent : null;
        if (label) copyButton.textContent = 'Копирование…';
        feedback.textContent = '';
        const copiedText = copyButton.dataset.copy;
        try {
          await navigator.clipboard.writeText(copiedText);
          feedback.textContent = copyButton.dataset.copy === copiedText
            ? copyButton.dataset.success
            : 'Сообщение изменилось. Скопируйте актуальный текст.';
        } catch {
          feedback.textContent = copyButton.dataset.error || (copiedText === '@rove63'
            ? 'Скопируйте имя вручную: @rove63'
            : 'Копирование недоступно. Используйте пункты выше как шаблон.');
          const fallback = document.getElementById(copyButton.dataset.copyFallback);
          fallback?.focus();
          fallback?.select();
        } finally {
          copyPending = false;
          disabledStates.forEach(([button, value]) => {
            if (value === null) button.removeAttribute('aria-disabled');
            else button.setAttribute('aria-disabled', value);
          });
          copyButton.removeAttribute('aria-busy');
          if (label) copyButton.textContent = label;
        }
      });
    });
  }

  const briefBuilder = document.querySelector('.brief-builder');
  const briefCopy = document.querySelector('.brief-copy');
  const briefMessage = document.getElementById('brief-message');
  const briefType = document.getElementById('brief-type');
  if (briefBuilder && briefCopy && briefMessage && briefType) {
    const fields = [...briefBuilder.querySelectorAll('[data-brief-label]')];
    const briefDetails = briefBuilder.closest('details');
    const emptyTemplate = briefCopy.dataset.copy;
    const feedback = document.getElementById(briefCopy.dataset.feedback);
    const updateBrief = () => {
      const lines = fields.flatMap((field) => {
        const value = field instanceof HTMLSelectElement
          ? (field.value ? field.selectedOptions[0].textContent : '')
          : field.value.trim();
        return value ? [`${field.dataset.briefLabel}: ${value}`] : [];
      });
      const message = lines.length
        ? `Здравствуйте, Пётр! Хочу обсудить проект.\n\n${lines.join('\n')}`
        : emptyTemplate;
      briefMessage.value = message;
      briefCopy.dataset.copy = message;
      if (feedback) feedback.textContent = '';
    };
    briefBuilder.addEventListener('input', updateBrief);
    briefBuilder.addEventListener('change', updateBrief);
    // Browsers may restore form values after deferred scripts have initialized.
    window.addEventListener('pageshow', updateBrief);
    updateBrief();
    briefBuilder.hidden = false;
    briefDetails.classList.add('brief-interactive');
    document.querySelector('.brief-instructions').hidden = true;
    briefCopy.textContent = 'Скопировать сообщение';
    briefCopy.dataset.success = 'Сообщение скопировано. Можно отправить его в Telegram.';
    const openBriefFromHash = () => {
      if (window.location.hash === '#project-brief') briefDetails.open = true;
    };
    openBriefFromHash();
    window.addEventListener('hashchange', openBriefFromHash);
    document.querySelectorAll('[data-brief-type], [data-open-brief]').forEach((link) => {
      link.addEventListener('click', (event) => {
        if (!isPlainClick(event)) return;
        // Handle this fragment here so generic navigation doesn't refocus the summary.
        event.preventDefault();
        if (link.dataset.briefType) briefType.value = link.dataset.briefType;
        briefDetails.open = true;
        updateBrief();
        if (window.location.hash !== link.hash) window.location.hash = link.hash;
        document.getElementById('project-brief').scrollIntoView({ block: 'start' });
        const goal = document.getElementById('brief-goal');
        goal.focus({ preventScroll: true });
        const bounds = goal.getBoundingClientRect();
        const headerBottom = document.querySelector('.site-header')?.getBoundingClientRect().bottom || 0;
        if (bounds.top < headerBottom || bounds.bottom > window.innerHeight) {
          goal.scrollIntoView({ block: 'center', behavior: 'instant' });
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
    const imageWrap = viewer.querySelector('.viewer-image-wrap');
    const placeholder = viewer.querySelector('.viewer-placeholder');
    const feedback = viewer.querySelector('.viewer-load-feedback');
    const status = viewer.querySelector('.viewer-status');
    const retry = viewer.querySelector('.viewer-retry');
    const project = viewer.querySelector('.viewer-project');
    let selected = 0;
    let opener;
    let loadVersion = 0;
    let gesture;

    const showPreview = (index) => {
      selected = (index + previews.length) % previews.length;
      const preview = previews[selected];
      const source = preview.querySelector('img');
      const card = preview.closest('.project-card');
      const caseLink = card.querySelector('.project-case-link');
      const projectSource = caseLink || card.querySelector('.project-heading a');
      project.href = projectSource.href;
      project.querySelector('span').textContent = caseLink ? 'Разбор проекта' : 'Репозиторий проекта';
      if (caseLink) {
        project.removeAttribute('target');
        project.removeAttribute('rel');
        project.removeAttribute('aria-label');
      } else {
        project.target = '_blank';
        project.rel = 'noopener noreferrer';
        project.setAttribute('aria-label', 'Репозиторий проекта, новая вкладка');
      }
      image.hidden = true;
      placeholder.hidden = false;
      image.alt = source.alt;
      viewer.querySelector('.viewer-original').href = preview.href;
      title.textContent = preview.closest('.project-card').querySelector('.project-heading a').firstChild.textContent;
      counter.textContent = `${selected + 1} из ${previews.length}`;
      const version = ++loadVersion;
      feedback.hidden = false;
      retry.hidden = true;
      status.textContent = 'Загружаю скриншот…';
      imageWrap.setAttribute('aria-busy', 'true');
      const loadingImage = new Image();
      const failLoad = () => {
        if (version !== loadVersion) return;
        imageWrap.setAttribute('aria-busy', 'false');
        status.textContent = 'Не удалось загрузить скриншот. Повторите попытку или откройте проект.';
        retry.hidden = false;
      };
      loadingImage.onload = async () => {
        if (version !== loadVersion) return;
        image.src = loadingImage.src;
        try {
          if (image.decode) await image.decode();
        } catch {
          failLoad();
          return;
        }
        if (version !== loadVersion) return;
        image.hidden = false;
        placeholder.hidden = true;
        imageWrap.setAttribute('aria-busy', 'false');
        status.textContent = '';
        feedback.hidden = true;
      };
      loadingImage.onerror = failLoad;
      loadingImage.src = preview.href;
    };
    retry.addEventListener('click', () => {
      showPreview(selected);
      // Retry disappears while loading; keep focus on a visible dialog control.
      viewer.querySelector('.viewer-close').focus();
    });
    imageWrap.addEventListener('pointerdown', (event) => {
      gesture = event.isPrimary && ['touch', 'pen'].includes(event.pointerType)
        ? { id: event.pointerId, x: event.clientX, y: event.clientY }
        : undefined;
    });
    imageWrap.addEventListener('pointercancel', () => { gesture = undefined; });
    imageWrap.addEventListener('pointerup', (event) => {
      const start = gesture;
      gesture = undefined;
      if (!start || start.id !== event.pointerId) return;
      const dx = event.clientX - start.x;
      const dy = event.clientY - start.y;
      if (Math.abs(dx) >= 50 && Math.abs(dx) > Math.abs(dy) * 1.5) {
        showPreview(selected + (dx < 0 ? 1 : -1));
      }
    });
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
      loadVersion += 1;
      gesture = undefined;
      imageWrap.setAttribute('aria-busy', 'false');
      document.documentElement.classList.remove('viewer-open');
      opener?.focus({ preventScroll: true });
    });
  }

  const header = document.querySelector('.site-header');
  const navLinks = [...document.querySelectorAll('.desktop-nav a, .mobile-nav a')];
  const sections = [...document.querySelectorAll('main > section[id]')]
    .filter((section) => navLinks.some((link) => link.hash === `#${section.id}`));
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

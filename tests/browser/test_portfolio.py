"""Real-browser checks; run separately from the dependency-free static checks."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import os
import json
import unittest

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
PAGES = tuple(path.relative_to(ROOT / 'docs').as_posix() for path in sorted((ROOT / 'docs').rglob('*.html')))


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class PortfolioBrowserChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Serve below /docs/ to exercise relative URLs under a Pages project path.
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}/docs/'
        cls.playwright = sync_playwright().start()
        options = {'headless': True}
        engine = os.environ.get('PORTFOLIO_BROWSER', 'chromium')
        if engine == 'chromium' and os.environ.get('PORTFOLIO_CHROMIUM'):
            options['executable_path'] = os.environ['PORTFOLIO_CHROMIUM']
        cls.browser = getattr(cls.playwright, engine).launch(**options)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))

    def tearDown(self):
        artifact_folder = os.environ.get('PORTFOLIO_ARTIFACTS')
        result = self._outcome.result
        if artifact_folder and any(test is self for test, _ in result.errors + result.failures):
            folder = Path(artifact_folder)
            folder.mkdir(parents=True, exist_ok=True)
            self.page.screenshot(path=str(folder / (self._testMethodName + '.png')), full_page=True)
        self.context.close()
        self.assertEqual(self.errors, [], 'Unexpected browser errors')

    def visit(self, path=''):
        self.page.goto(self.base + path, wait_until='networkidle')

    def assert_no_overflow(self):
        self.assertFalse(self.page.evaluate('document.documentElement.scrollWidth > innerWidth'))

    def assert_accessible(self):
        self.page.add_script_tag(path=str(ROOT / 'tests/browser/node_modules/axe-core/axe.min.js'))
        violations = self.page.evaluate('''async () => {
            const result = await axe.run(document, {
                runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa', 'best-practice']}
            });
            return result.violations.map(v => ({id: v.id, impact: v.impact,
                nodes: v.nodes.map(n => ({target: n.target, reason: n.failureSummary}))}));
        }''')
        self.assertEqual(violations, [], json.dumps(violations, ensure_ascii=False, indent=2))

    def test_accessibility_in_both_themes_and_dynamic_states(self):
        for width in (390, 1440):
            for path in PAGES:
                for theme in ('dark', 'light'):
                    with self.subTest(width=width, path=path, theme=theme):
                        self.page.set_viewport_size({'width': width, 'height': 900})
                        self.visit(path)
                        if self.page.locator('html').get_attribute('data-theme') != theme:
                            self.page.locator('.theme-toggle').click()
                        if path == 'index.html':
                            self.page.locator('[data-open-brief]').click()
                        self.assert_accessible()
                        if path == 'index.html' and width == 390:
                            self.page.locator('.project-media').first.click()
                            self.assert_accessible()

    def test_brief_task_field_is_visible_on_short_screen(self):
        self.page.set_viewport_size({'width': 390, 'height': 320})
        for preference in ('reduce', 'no-preference'):
            with self.subTest(motion=preference):
                self.page.emulate_media(reduced_motion=preference)
                self.visit()
                self.page.locator('[data-open-brief]').click()
                expect(self.page.locator('#brief-goal')).to_be_focused()
                self.assertTrue(self.page.locator('#brief-goal').evaluate('el => {const r=el.getBoundingClientRect(); return r.top >= 74 && r.bottom <= innerHeight;}'))

    def test_mobile_menu_scrolls_in_landscape(self):
        self.page.set_viewport_size({'width': 390, 'height': 240})
        self.visit()
        self.page.locator('.menu-toggle').click()
        self.page.locator('#mobile-nav a').last.scroll_into_view_if_needed()
        self.assertTrue(self.page.locator('#mobile-nav a').last.evaluate('el => el.getBoundingClientRect().bottom <= innerHeight'))
        self.page.locator('#mobile-nav a').last.click()
        expect(self.page.locator('#contact')).to_be_focused()

    def test_modified_menu_link_does_not_hide_current_navigation(self):
        self.page.set_viewport_size({'width': 390, 'height': 844})
        self.visit()
        self.page.locator('.menu-toggle').click()
        self.page.locator('#mobile-nav a').first.click(modifiers=['ControlOrMeta'])
        expect(self.page.locator('#mobile-nav')).to_be_visible()
        expect(self.page.locator('.menu-toggle')).to_have_attribute('aria-expanded', 'true')

    def test_saved_motion_is_applied_without_main_script(self):
        self.page.emulate_media(reduced_motion='no-preference')
        self.page.add_init_script('localStorage.setItem("portfolio-reduced-motion", "true")')
        self.page.route('**/assets/main.js', lambda route: route.abort())
        self.visit()
        self.assertEqual(self.page.locator('.hero-title').evaluate('el => getComputedStyle(el).animationName'), 'none')

    def test_motion_preference_syncs_across_tabs_and_restored_pages(self):
        self.page.emulate_media(reduced_motion='no-preference')
        self.visit()
        other = self.context.new_page()
        other.emulate_media(reduced_motion='no-preference')
        other.goto(self.base + 'projects/testops-copilot.html')
        other.locator('.motion-toggle').click()
        expect(self.page.locator('.motion-toggle')).to_have_attribute('aria-pressed', 'true')
        other.locator('.motion-toggle').click()
        expect(self.page.locator('.motion-toggle')).to_have_attribute('aria-pressed', 'false')
        self.page.evaluate('localStorage.setItem("portfolio-reduced-motion", "true"); window.dispatchEvent(new PageTransitionEvent("pageshow", {persisted: true}))')
        expect(self.page.locator('.motion-toggle')).to_have_attribute('aria-pressed', 'true')

    def test_restored_fields_refresh_the_message(self):
        self.visit('#project-brief')
        self.page.evaluate('document.getElementById("brief-goal").value="Восстановленная задача"; window.dispatchEvent(new PageTransitionEvent("pageshow", {persisted: true}))')
        self.assertIn('Восстановленная задача', self.page.locator('#brief-message').input_value())

    def test_newer_clipboard_attempt_owns_the_feedback(self):
        self.page.add_init_script('''
            window.copyResolvers = [];
            Object.defineProperty(navigator, 'clipboard', {value: {
                writeText: () => new Promise(resolve => window.copyResolvers.push(resolve))
            }});
        ''')
        self.visit('#project-brief')
        self.page.locator('#brief-goal').fill('Первый текст')
        self.page.locator('.brief-copy').click()
        self.page.locator('#brief-goal').fill('Второй текст')
        self.page.locator('.brief-copy').click()
        self.page.evaluate('window.copyResolvers[1]()')
        expect(self.page.locator('#brief-feedback')).to_contain_text('Сообщение скопировано')
        self.page.evaluate('window.copyResolvers[0]()')
        expect(self.page.locator('#brief-feedback')).to_contain_text('Сообщение скопировано')

    def test_active_case_navigation_survives_unlisted_section(self):
        self.visit('projects/testops-copilot.html')
        self.page.locator('#results').evaluate('el => el.scrollIntoView({block: "start"})')
        expect(self.page.locator('.desktop-nav a[href="#states"]')).to_have_attribute('aria-current', 'location')

    def test_brief_text_is_not_executed_persisted_or_sent(self):
        outgoing = []
        self.page.on('request', lambda request: outgoing.append({'url': request.url, 'body': request.post_data or ''}))
        self.visit('#project-brief')
        marker = '<img src=x onerror="window.injected=true">PRIVATE-AUDIT-TEXT'
        self.page.locator('#brief-goal').fill(marker)
        self.assertIn(marker, self.page.locator('#brief-message').input_value())
        self.assertFalse(self.page.evaluate('Boolean(window.injected)'))
        self.assertNotIn('PRIVATE-AUDIT-TEXT', self.page.evaluate('JSON.stringify(localStorage) + JSON.stringify(sessionStorage)'))
        self.assertNotIn('PRIVATE-AUDIT-TEXT', json.dumps(outgoing))
        self.assertEqual(self.page.locator('.brief-telegram').get_attribute('href'), 'https://t.me/rove63')

    def test_layout_and_assets_in_both_themes(self):
        failures = []
        self.page.on('response', lambda response: failures.append(response.url) if response.status >= 400 else None)
        for width in (320, 390, 760, 1440):
            for path in PAGES:
                with self.subTest(width=width, path=path):
                    self.page.set_viewport_size({'width': width, 'height': 1000})
                    self.visit(path)
                    for theme in ('light', 'dark'):
                        self.page.locator('.theme-toggle').click()
                        expect(self.page.locator('html')).to_have_attribute('data-theme', theme)
                        self.assert_no_overflow()
                    for image in self.page.locator('img[src]').all():
                        image.scroll_into_view_if_needed()
                        expect(image).to_have_js_property('complete', True)
                    self.assertTrue(self.page.evaluate('Array.from(document.images).every(img => !img.getAttribute("src") || img.naturalWidth > 0)'))
        self.assertEqual(failures, [])

    def test_testops_case_is_reachable_and_links_to_related_work(self):
        self.visit()
        self.page.locator('.project-case-link[href="./projects/testops-copilot.html"]').focus()
        self.page.keyboard.press('Enter')
        expect(self.page.locator('h1')).to_have_text('TestOpsCopilot.')
        self.page.locator('.desktop-nav a[href="#architecture"]').click()
        expect(self.page.locator('#architecture')).to_be_focused()
        expect(self.page.locator('#architecture .request-flow li')).to_have_count(4)
        self.page.locator('.case-related a').click()
        expect(self.page).to_have_url(self.base + 'projects/commit-to-learn.html')
        self.page.locator('.case-related a').click()
        expect(self.page).to_have_url(self.base + 'projects/testops-copilot.html')
        self.page.locator('.case-contact .button').click()
        expect(self.page).to_have_url(self.base + 'index.html#project-brief')
        expect(self.page.locator('.brief-builder')).to_be_visible()

    def test_testops_mobile_navigation_and_static_content_without_javascript(self):
        context = self.browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 844}, reduced_motion='reduce')
        try:
            page = context.new_page()
            page.goto(self.base + 'projects/testops-copilot.html')
            page.locator('#mobile-nav a[href="#states"]').click()
            expect(page.locator('.task-states dt')).to_have_count(4)
            expect(page.locator('.task-state[data-state="completed"]')).to_have_text('completed')
            expect(page.locator('.task-states')).to_be_visible()
            page.locator('.case-return').click()
            expect(page).to_have_url(self.base + 'index.html#projects')
            expect(page.locator('#projects')).to_be_visible()
        finally:
            context.close()

    def test_hero_opens_brief_and_focuses_task(self):
        self.visit()
        self.page.locator('[data-open-brief]').click()
        expect(self.page.locator('.contact-brief')).to_have_attribute('open', '')
        expect(self.page.locator('#brief-goal')).to_be_focused()
        self.assertEqual(self.page.url, self.base + '#project-brief')

    def test_service_preserves_details_and_preselects_format(self):
        self.visit()
        self.page.locator('[data-brief-type=web]').click()
        self.page.locator('#brief-goal').fill('Личный кабинет для команды')
        self.page.locator('[data-brief-type=bot]').click()
        expect(self.page.locator('#brief-type')).to_have_value('bot')
        expect(self.page.locator('#brief-goal')).to_be_focused()
        expect(self.page.locator('#brief-message')).to_have_value('Здравствуйте, Пётр! Хочу обсудить проект.\n\nФормат: Telegram-бот / интеграция\nЗадача: Личный кабинет для команды')
        self.page.locator('[data-open-brief]').click()
        expect(self.page.locator('#brief-type')).to_have_value('bot')
        expect(self.page.locator('#brief-goal')).to_have_value('Личный кабинет для команды')
        self.assertEqual(self.page.locator('.brief-telegram').get_attribute('href'), 'https://t.me/rove63')
        self.assertNotIn('Личный кабинет для команды', self.page.evaluate('JSON.stringify(localStorage)'))

    def test_direct_brief_link_opens_after_load_and_history_navigation(self):
        self.visit('#project-brief')
        expect(self.page.locator('.brief-builder')).to_be_visible()
        self.page.locator('#project-brief').click()
        self.page.evaluate('location.hash = "projects"')
        self.page.evaluate('location.hash = "project-brief"')
        expect(self.page.locator('.brief-builder')).to_be_visible()

    def test_mobile_keyboard_navigation_and_escape(self):
        self.page.set_viewport_size({'width': 390, 'height': 844})
        self.visit()
        button = self.page.locator('.menu-toggle')
        button.focus()
        self.page.keyboard.press('Enter')
        self.page.keyboard.press('Tab')
        expect(self.page.locator('#mobile-nav a').first).to_be_focused()
        self.page.keyboard.press('Enter')
        expect(self.page.locator('#mobile-nav')).to_be_hidden()
        expect(self.page.locator('#projects')).to_be_focused()
        self.page.keyboard.press('Tab')
        expect(self.page.locator('.project-media').first).to_be_focused()
        button.click()
        self.page.keyboard.press('Escape')
        expect(button).to_be_focused()
        expect(button).to_have_attribute('aria-expanded', 'false')

    def test_gallery_keyboard_navigation_and_focus_return(self):
        self.visit()
        preview = self.page.locator('.project-media').first
        preview.focus()
        self.page.keyboard.press('Enter')
        expect(self.page.locator('.project-viewer')).to_be_visible()
        expect(self.page.locator('.viewer-close')).to_be_focused()
        self.page.keyboard.press('ArrowRight')
        expect(self.page.locator('.viewer-counter')).to_have_text('2 из 3')
        self.page.keyboard.press('Escape')
        expect(self.page.locator('.project-viewer')).to_be_hidden()
        expect(preview).to_be_focused()

    def test_clipboard_failure_offers_manual_selection(self):
        self.page.add_init_script('Object.defineProperty(navigator, "clipboard", {value: {writeText: () => Promise.reject(new Error("Denied"))}})')
        self.visit()
        self.page.locator('[data-open-brief]').click()
        self.page.locator('#brief-goal').fill('Автоматизация отчётов')
        self.page.locator('.brief-copy').click()
        expect(self.page.locator('#brief-feedback')).to_contain_text('скопируйте вручную')
        expect(self.page.locator('#brief-message')).to_be_focused()
        self.assertTrue(self.page.locator('#brief-message').evaluate('el => el.selectionEnd - el.selectionStart === el.value.length'))

    def test_copy_uses_current_message_and_detects_later_edits(self):
        self.page.add_init_script('''
            Object.defineProperty(navigator, 'clipboard', {value: {
                writeText: text => {window.copiedMessage = text; return new Promise(resolve => {window.finishCopy = resolve;});}
            }});
        ''')
        self.visit()
        self.page.locator('[data-open-brief]').click()
        self.page.locator('#brief-goal').fill('Первая версия задачи')
        self.page.locator('.brief-copy').click()
        self.assertEqual(self.page.evaluate('window.copiedMessage'), self.page.locator('#brief-message').input_value())
        self.page.locator('#brief-goal').fill('Уточнённая задача')
        self.page.evaluate('window.finishCopy()')
        expect(self.page.locator('#brief-feedback')).to_contain_text('Сообщение изменилось')
        self.page.locator('.brief-copy').click()
        self.page.evaluate('window.finishCopy()')
        expect(self.page.locator('#brief-feedback')).to_contain_text('Сообщение скопировано')
        self.assertIn('Уточнённая задача', self.page.evaluate('window.copiedMessage'))

    def test_without_clipboard_the_message_can_still_be_selected(self):
        self.page.add_init_script('Object.defineProperty(navigator, "clipboard", {value: undefined})')
        self.visit()
        self.page.locator('[data-open-brief]').click()
        expect(self.page.locator('.brief-copy')).to_be_hidden()
        expect(self.page.locator('#brief-message')).to_be_visible()
        expect(self.page.locator('.brief-telegram')).to_be_visible()

    def test_theme_survives_reload_and_navigation(self):
        self.visit()
        self.page.locator('.theme-toggle').click()
        self.page.reload()
        expect(self.page.locator('html')).to_have_attribute('data-theme', 'light')
        self.visit('projects/commit-to-learn.html')
        expect(self.page.locator('html')).to_have_attribute('data-theme', 'light')
        expect(self.page.locator('meta[name=theme-color]')).to_have_attribute('content', '#f6f6f2')

    def test_theme_survives_pageshow_when_storage_is_blocked(self):
        for block_reads in (False, True):
            with self.subTest(block_reads=block_reads):
                self.page.add_init_script('Storage.prototype.setItem = () => {throw new Error("Blocked")};' + ('Storage.prototype.getItem = () => {throw new Error("Blocked")};' if block_reads else ''))
                self.visit()
                self.page.locator('.theme-toggle').click()
                self.page.evaluate('window.dispatchEvent(new PageTransitionEvent("pageshow", {persisted: true}))')
                expect(self.page.locator('html')).to_have_attribute('data-theme', 'light')

    def test_theme_syncs_between_open_pages(self):
        self.visit()
        other = self.context.new_page()
        other.goto(self.base + 'projects/commit-to-learn.html')
        self.page.locator('.theme-toggle').click()
        expect(other.locator('html')).to_have_attribute('data-theme', 'light')
        other.locator('.theme-toggle').click()
        expect(self.page.locator('html')).to_have_attribute('data-theme', 'dark')

    def test_motion_can_be_disabled_without_hiding_content(self):
        self.page.emulate_media(reduced_motion='no-preference')
        self.visit()
        self.page.locator('.motion-toggle').click()
        expect(self.page.locator('html')).to_have_class('js-ready reduce-motion')
        self.assertTrue(self.page.locator('.reveal').evaluate_all('items => items.every(el => getComputedStyle(el).opacity === "1")'))
        self.page.reload()
        expect(self.page.locator('.motion-toggle')).to_have_attribute('aria-pressed', 'true')

    def test_without_javascript_navigation_and_code_explorer_work(self):
        context = self.browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 844}, reduced_motion='reduce')
        try:
            page = context.new_page()
            page.goto(self.base)
            expect(page.locator('#mobile-nav')).to_be_visible()
            page.locator('label[for=backend-data]').click()
            expect(page.locator('#backend-panel-data')).to_be_visible()
            expect(page.locator('#backend-panel-route')).to_be_hidden()
            page.locator('[data-open-brief]').click()
            page.locator('#project-brief').press('Enter')
            expect(page.locator('.brief-instructions')).to_be_visible()
            expect(page.locator('.contact-actions a')).to_be_visible()
        finally:
            context.close()


if __name__ == '__main__':
    unittest.main()

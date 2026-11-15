"""Render the local HTML share-card source; uses the browser-test dependencies."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as playwright:
            options = {'headless': True}
            if os.environ.get('PORTFOLIO_CHROMIUM'):
                options['executable_path'] = os.environ['PORTFOLIO_CHROMIUM']
            browser = playwright.chromium.launch(**options)
            try:
                page = browser.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=1)
                page.goto(f'http://127.0.0.1:{server.server_port}/scripts/social-cover.html', wait_until='networkidle')
                page.evaluate('document.fonts.ready')
                if page.evaluate('document.documentElement.scrollWidth > 1200 || document.documentElement.scrollHeight > 630'):
                    raise ValueError('Share-card content exceeds the 1200 × 630 canvas')
                page.screenshot(path=str(ROOT / 'docs/assets/social-profile.png'))
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    print('Rendered docs/assets/social-profile.png (1200 × 630)')


if __name__ == '__main__':
    main()

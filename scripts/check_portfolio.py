#!/usr/bin/env python3
"""Dependency-free pre-deploy sanity checks for the GitHub Pages portfolio."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys

DOCS = Path(__file__).resolve().parent.parent / "docs"
INDEX = DOCS / "index.html"
errors = []


def report(message: str) -> None:
    errors.append(message)


def check_local_path(raw: str, source: Path) -> None:
    if not raw or raw.startswith(("#", "data:", "mailto:", "tel:", "//")):
        return
    parsed = urlsplit(raw)
    if parsed.scheme:
        if parsed.scheme not in ("https", "http"):
            report(f"{source.name}: unsupported URL scheme in {raw!r}")
        return
    if parsed.path.startswith("/"):
        report(f"{source.name}: use relative asset path for project GitHub Pages: {raw!r}")
        return
    candidate = (source.parent / unquote(parsed.path)).resolve()
    if not candidate.is_relative_to(DOCS.resolve()):
        report(f"{source.name}: asset points outside docs/: {raw!r}")
    elif not candidate.is_file():
        report(f"{source.name}: linked local asset not found: {raw!r}")


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.anchors = []
        self.refs = []
        self.titles = 0
        self.mains = 0
        self.lang = None
        self.description = False

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "title":
            self.titles += 1
        if tag == "main":
            self.mains += 1
        if tag == "meta" and attrs.get("name", "").lower() == "description":
            self.description = bool(attrs.get("content", "").strip())
        if attrs.get("id"):
            if attrs["id"] in self.ids:
                report(f"Duplicate id: {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag == "img" and not attrs.get("alt", "").strip():
            report(f"Image without meaningful alt: {attrs.get('src', '?')}")
        if tag == "a":
            href = attrs.get("href", "")
            if not href:
                report("Anchor without href")
            else:
                self.anchors.append(href)
            if attrs.get("target") == "_blank":
                rel = set((attrs.get("rel") or "").split())
                if "noopener" not in rel:
                    report(f"External/new-window link missing rel=noopener: {href}")
        for key in ("href", "src"):
            if attrs.get(key):
                self.refs.append(attrs[key])
        if tag == "meta" and attrs.get("property") == "og:image" and attrs.get("content"):
            self.refs.append(attrs["content"])

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


def main():
    errors.clear()
    if not INDEX.is_file():
        report("docs/index.html not found")
    pages = {}
    for path in sorted(DOCS.rglob("*.html")):
        parser = SiteParser()
        parser.feed(path.read_text(encoding="utf-8"))
        parser.close()
        pages[path.resolve()] = parser
        label = str(path.relative_to(DOCS))
        if not parser.lang:
            report(f"{label}: missing html lang")
        if parser.titles != 1:
            report(f"{label}: expected one <title>, found {parser.titles}")
        if parser.mains != 1:
            report(f"{label}: expected one <main>, found {parser.mains}")
        if not parser.description:
            report(f"{label}: missing meta description")
        for url in parser.refs:
            check_local_path(url, path)

    # Resolve fragments after all pages have been parsed, including links back
    # from a nested case page to a section on the homepage.
    for path, parser in pages.items():
        for href in parser.anchors:
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc or not parsed.fragment:
                continue
            target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            target_page = pages.get(target)
            if target_page and unquote(parsed.fragment) not in target_page.ids:
                report(f"{path.relative_to(DOCS.resolve())}: broken internal anchor: {href}")

    # Check files referenced by url(...) in CSS, including web fonts.
    for css in DOCS.rglob("*.css"):
        text = css.read_text(encoding="utf-8")
        for raw in re.findall(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", text):
            check_local_path(raw.strip(), css)

    if errors:
        print("Portfolio checks FAILED:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"Portfolio checks passed: {len(pages)} HTML pages, anchors, local assets, link safety, CSS assets")
    return 0


if __name__ == "__main__":
    sys.exit(main())

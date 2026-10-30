"""Regression checks for nested project pages and cross-page links."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import check_portfolio


def page(content):
    return ('<!doctype html><html lang="ru"><head><title>Test</title>'
            '<meta name="description" content="Portfolio test"></head>'
            f'<body><main id="main"><h1>Test page</h1>{content}</main></body></html>')


class MultipageChecks(unittest.TestCase):
    def check_site(self, nested_content):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "projects").mkdir()
            index = root / "index.html"
            index.write_text(page('<section id="projects"><a href="./projects/case.html#overview">Case</a></section>'))
            (root / "projects/case.html").write_text(page('<section id="overview">' + nested_content + '</section>'))
            with patch.object(check_portfolio, "DOCS", root), patch.object(check_portfolio, "INDEX", index), contextlib.redirect_stdout(io.StringIO()):
                result = check_portfolio.main()
            return result, list(check_portfolio.errors)

    def test_valid_nested_page_and_return_link(self):
        result, errors = self.check_site('<a href="../index.html#projects">Back</a>')
        self.assertEqual(result, 0, errors)

    def test_missing_asset_on_nested_page_is_reported(self):
        result, errors = self.check_site('<img src="./missing.webp" alt="Example screen">')
        self.assertEqual(result, 1)
        self.assertTrue(any("missing.webp" in error for error in errors))

    def test_unknown_fragment_on_another_page_is_reported(self):
        result, errors = self.check_site('<a href="../index.html#unknown">Back</a>')
        self.assertEqual(result, 1)
        self.assertTrue(any("#unknown" in error for error in errors))

    def test_duplicate_ids_are_scoped_to_each_document(self):
        result, errors = self.check_site('<a href="#main">Top</a><a href="../index.html#main">Home</a>')
        self.assertEqual(result, 0, errors)

    def test_query_only_links_point_to_current_document(self):
        result, errors = self.check_site('<a href="?view=compact#overview">View</a>')
        self.assertEqual(result, 0, errors)

    def test_directory_links_resolve_to_index(self):
        result, errors = self.check_site('<a href="../#projects">Home</a>')
        self.assertEqual(result, 0, errors)

    def test_directory_link_fragments_are_checked(self):
        result, errors = self.check_site('<a href="../#missing">Home</a>')
        self.assertEqual(result, 1)
        self.assertTrue(any('broken internal anchor' in error for error in errors))

    def test_missing_aria_reference_is_reported(self):
        result, errors = self.check_site('<button type="button" aria-controls="missing">Open</button>')
        self.assertEqual(result, 1)
        self.assertTrue(any('aria-controls references missing id' in error for error in errors))

    def test_missing_label_target_is_reported(self):
        result, errors = self.check_site('<label for="missing">Name</label>')
        self.assertEqual(result, 1)
        self.assertTrue(any('label for references missing id' in error for error in errors))

    def test_multiple_aria_references_are_supported(self):
        result, errors = self.check_site('<span id="name">Name</span><span id="help">Help</span><button type="button" aria-labelledby="name help">Open</button>')
        self.assertEqual(result, 0, errors)

    def test_multiple_primary_headings_are_reported(self):
        result, errors = self.check_site('<h1>Another title</h1>')
        self.assertEqual(result, 1)
        self.assertTrue(any('expected one <h1>' in error for error in errors))


class SitemapChecks(unittest.TestCase):
    def check_map(self, xml):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'sitemap.xml').write_text(xml)
            parser = check_portfolio.SiteParser()
            parser.canonical = 'https://example.com/'
            check_portfolio.errors.clear()
            with patch.object(check_portfolio, 'DOCS', root):
                check_portfolio.check_sitemap({root / 'index.html': parser})
            return list(check_portfolio.errors)

    def test_sitemap_matches_canonical_urls(self):
        self.assertEqual(self.check_map('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/</loc></url></urlset>'), [])

    def test_unknown_sitemap_page_is_reported(self):
        self.assertTrue(self.check_map('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/missing</loc></url></urlset>'))

    def test_invalid_xml_is_reported(self):
        self.assertTrue(self.check_map('<urlset>'))


if __name__ == "__main__":
    unittest.main()

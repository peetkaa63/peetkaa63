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
            f'<body><main id="main">{content}</main></body></html>')


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


if __name__ == "__main__":
    unittest.main()

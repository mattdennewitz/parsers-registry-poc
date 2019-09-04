"""
Basis for byline parsing
"""

from typing import Callable, List

from lxml import html


class BaseParser:
    byline_extractors = None
    domains = None
    patterns = None

    def _convert_html_to_tree(self, html_document: str) -> html.HtmlElement:
        """Converts HTML string to living document"""

        return html.fromstring(html_document)

    def get_domains(self) -> List[str]:
        return self.domains or []

    def get_byline_extractors(self) -> List[Callable]:
        """Returns a collection of extractors"""

        return self.byline_extractors or []

    def get_patterns(self):
        """Returns a list of URL pattern regexes or callables
        to allow or reject parsing a given URL
        """

        return self.patterns or []

    def extract(self, html_document: str) -> List[str]:
        """Attempts to extract author names
        """

        tree = self._convert_html_to_tree(html_document)

        # find byline strings
        for extractor in self.get_byline_extractors():
            author_names = extractor(tree, html_document, self)
            if author_names:
                return author_names

        return []


class CSSSelectorMixin:
    authors_selector = None

    def get_authors_selector(self) -> str:
        """Returns a CSS selector for author extraction from an HTML document"""

        return self.authors_selector

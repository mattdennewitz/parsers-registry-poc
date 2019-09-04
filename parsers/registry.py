"""
Parser registration and distillation
"""

import collections
import re
from typing import List, Pattern, Tuple
from urllib import parse

import tldextract

__all__ = ("registry",)

from .base import BaseParser, CSSSelectorMixin


class DomainNotRegisteredException(KeyError):
    pass


class NoMatchingParserException(ValueError):
    pass


class ParserRegistry(object):
    def __init__(self):
        self._registry = collections.defaultdict(list)

    def __contains__(self, key):
        if key in self._registry:
            return self._registry[key]

        return super().__contains__(key)

    def register(self, parser_cls):
        parser = parser_cls()

        for domain in parser.get_domains():
            self._registry[domain].append(parser)

    def _register_simple(
        self,
        name: str,
        domains: List[str],
        patterns: List[Pattern],
        bases: Tuple = None,
        **attrs,
    ) -> BaseParser:
        """Creates and registers a parser"""

        name = "SimpleParser"

        attrs.update({"domains": domains, "patterns": patterns})

        cls_bases = (BaseParser,)
        if bases:
            cls_bases += tuple(bases)

        parser_cls = type(name, cls_bases, attrs)

        self.register(parser_cls)

    def register_simple_css_parser(self, domains, patterns, authors_selector):
        """Fast-tracks creating a CSS selector-based parser"""

        name = "CSSParser"

        self._register_simple(
            name,
            domains,
            patterns,
            bases=(CSSSelectorMixin,),
            authors_selector=authors_selector,
        )

    def get_for_url(self, url, ignore_subdomain=False):
        bits = parse.urlparse(url)
        parsed = tldextract.extract(bits.netloc)
        domain = (
            bits.netloc if not ignore_subdomain else f"{parsed.domain}.{parsed.suffix}"
        )
        candidates = self._registry.get(domain)

        if not candidates:
            raise DomainNotRegisteredException(f"Domain not found: {domain}")

        for candidate in candidates:
            patterns = candidate.get_patterns()
            for pattern in patterns:
                if callable(pattern) and pattern(url):
                    return candidate
                if re.search(pattern, url):
                    return candidate

        raise NoMatchingParserException(f"No registered parser matches URL: {url}")


registry = ParserRegistry()

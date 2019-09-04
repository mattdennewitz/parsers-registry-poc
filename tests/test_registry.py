import re
from typing import List, Dict, Pattern, Type

import pytest

from parsers import BaseParser
from parsers.registry import DomainNotRegisteredException, NoMatchingParserException


class WashingtonPostFoodParser(BaseParser):
    domains = ["washingtonpost.com"]
    patterns = [r"/food/"]


class WashingtonPostNationalNewsParser(BaseParser):
    domains = ["washingtonpost.com"]
    patterns = [r"/national/"]


def test_registry_is_object(registry):
    assert isinstance(registry, object)


def test_internal_registry_is_dict(registry):
    assert isinstance(registry._registry, dict)


def test_register_parser(registry):
    """Parsers should be registered by their domain"""

    registry.register(WashingtonPostNationalNewsParser)

    assert len(registry._registry["washingtonpost.com"]) == 1
    assert isinstance(
        registry._registry["washingtonpost.com"][0], WashingtonPostNationalNewsParser
    )


def test_multiple_registrations_for_same_domain(registry):
    """Multiple parsers may be registered for the same domain"""

    registry.register(WashingtonPostFoodParser)
    registry.register(WashingtonPostNationalNewsParser)

    assert len(registry._registry["washingtonpost.com"]) == 2


@pytest.mark.parametrize(
    "expected_parser_cls,url,ignore_subdomain",
    [
        [
            WashingtonPostFoodParser,
            "https://www.washingtonpost.com/lifestyle/food/a-salad-with-figs-prosciutto-and-a-sweet-sour-dressing-hits-all-the-right-notes/2019/08/28/185115d8-c912-11e9-be05-f76ac4ec618c_story.html",
            True,
        ],
        [
            WashingtonPostNationalNewsParser,
            "https://www.washingtonpost.com/national/as-dorian-approaches-flood-fears-grip-the-southeast/2019/09/03/a4c34414-ce94-11e9-87fa-8501a456c003_story.html",
            True,
        ],
    ],
)
def test_get_for_url(registry, expected_parser_cls, url, ignore_subdomain):
    """Parsers can be fetched by URL"""

    registry.register(WashingtonPostFoodParser)
    registry.register(WashingtonPostNationalNewsParser)

    parser = registry.get_for_url(url, ignore_subdomain=ignore_subdomain)
    assert isinstance(parser, expected_parser_cls)


def test_get_for_url_unknown_domain(registry):
    """Missing domains are raised with DomainNotRegisteredException"""

    with pytest.raises(DomainNotRegisteredException):
        registry.get_for_url("https://muckrack.com")


def test_get_for_url_include_subdomain(registry):
    """Must-match subdomain mismatches are raised with DomainNotRegisteredException"""

    registry.register(WashingtonPostFoodParser)

    with pytest.raises(DomainNotRegisteredException):
        registry.get_for_url("https://www.washingtonpost.com", ignore_subdomain=False)


def test_get_for_url_no_candidates(registry):
    """Searches missing any candidates are raised with NoMatchingParserException"""

    registry.register(WashingtonPostFoodParser)

    with pytest.raises(NoMatchingParserException):
        registry.get_for_url(
            "https://www.washingtonpost.com/news/voraciously/wp/2019/09/03/this-lighter-fettuccine-still-delivers-the-cheesy-creamy-goodness-we-crave/",
            ignore_subdomain=True,
        )


def test_register_css_parser(registry):
    """Quick registration should register a subclass of BaseParser"""

    authors_selector = ".byline"
    domains = ["bloomberg.com"]
    patterns = [r"/news/"]

    registry.register_simple_css_parser(
        domains=domains, patterns=patterns, authors_selector=authors_selector
    )

    parser = registry.get_for_url(
        "https://www.bloomberg.com/news/articles/2019-09-03/uber-argues-driver-names-are-closely-guarded-trade-secrets?srnd=premium",
        ignore_subdomain=True,
    )

    assert isinstance(parser, BaseParser)
    assert parser.get_domains() == domains
    assert parser.get_patterns() == patterns
    assert parser.get_authors_selector() == authors_selector

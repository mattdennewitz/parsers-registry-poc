"""
Various byline string extraction functions
"""

from typing import List, TypeVar

from lxml.html import HtmlElement


def split_author_names(value):
    """Our magical name splitting algorithm"""

    return value.strip()


def extract_with_xpath(tree: HtmlElement, xpath_selector: str) -> List[str]:
    """Extracts using given XPath selector"""

    return tree.xpath(xpath_selector)


def extract_from_meta_author_tag(
    tree: HtmlElement, html_document: str, parser: TypeVar("BaseParser")
) -> List[str]:
    """Extracts author name from `meta[name="author"]` tag"""

    return extract_with_xpath(tree, '//meta[@name="author"]/@content')


def extract_from_opengraph_article_author_tag(
    tree: HtmlElement, html_document: str, parser: TypeVar("BaseParser")
) -> List[str]:
    """Extracts from OpenGraph `meta[property="og:article:author"] tag`"""

    return extract_with_xpath(tree, '//meta[@property="article:author"]/@content')


def extract_with_css_selector(
    tree: HtmlElement, html_document: str, parser: TypeVar("BaseParser")
) -> List[str]:
    """Extracts using a CSS selector"""

    nodes = tree.cssselect(parser.get_authors_selector())
    names = []

    for node in nodes:
        names.append(split_author_names(node.text_content()))

    return names

import pytest

from parsers import BaseParser, CSSSelectorMixin
from parsers.extractors import (
    extract_from_meta_author_tag,
    extract_from_opengraph_article_author_tag,
    extract_with_css_selector,
)


def test_extract_with_css():
    html = """
    <div class="byline-wrapper">
        <div class="byline">
            Matt Dennewitz
        </div>
    </div>
    """

    class Parser(BaseParser, CSSSelectorMixin):
        authors_selector = ".byline"
        byline_extractors = [extract_with_css_selector]

    author_names = Parser().extract(html)
    assert author_names == ["Matt Dennewitz"]


def test_extract_with_css_with_multiple_nodes():
    html = """
    <div class="byline-wrapper">
        by
        <span role="author">
            Matt Dennewitz
        </span>
        and
        <span role="author">
            his cat, Daniel
        </span>
    </div>
    """

    class Parser(BaseParser, CSSSelectorMixin):
        authors_selector = '.byline-wrapper span[role="author"]'
        byline_extractors = [extract_with_css_selector]

    author_names = Parser().extract(html)
    assert author_names == ["Matt Dennewitz", "his cat, Daniel"]


@pytest.mark.parametrize(
    "extractor,tags,expected_names",
    [
        [
            extract_from_meta_author_tag,
            '<meta name="author" content="Matt" />',
            ["Matt"],
        ],
        [
            extract_from_meta_author_tag,
            '<meta name="author" content="Matt" /><meta name="author" content="Matthew" />',
            ["Matt", "Matthew"],
        ],
        [
            extract_from_opengraph_article_author_tag,
            '<meta property="article:author" content="Matt" />',
            ["Matt"],
        ],
        [
            extract_from_opengraph_article_author_tag,
            '<meta property="article:author" content="Matt" /><meta property="article:author" content="Matthew" />',
            ["Matt", "Matthew"],
        ],
    ],
)
def test_extract_with_xpath_tags(extractor, tags, expected_names):
    html = f"""
    <html>
        <head>
            {tags}
        </head>
    </html>
    """

    class Parser(BaseParser):
        byline_extractors = [extractor]

    author_names = Parser().extract(html)
    assert author_names == expected_names


def test_custom_extractor():
    html = """
    <div>
        <dl>
            <dt>Author</dt>
            <dd>Matt Dennewitz</dd>
            <dt>Published on</dt>
            <dd>Dec 3, 1983</div>
        </dl>
    </div>
    """

    class Parser(BaseParser):
        def extract_from_dl(self, tree, html_document, parser):
            author_names = tree.xpath("./dl/dd[1]/text()")
            return author_names

        def get_byline_extractors(self):
            return [self.extract_from_dl]

    author_names = Parser().extract(html)
    assert author_names == ["Matt Dennewitz"]


def test_extractors_continue_until_value_is_found():
    """Parsers should continue trying extractors until a value is found"""

    html = """
    <html>
        <head>
            <meta property="article:author" content="Matt" />
        </head>
    </html>
    """

    class Parser(BaseParser):
        byline_extractors = [
            extract_from_meta_author_tag,  # nope
            extract_from_opengraph_article_author_tag,  # yep
        ]

    author_names = Parser().extract(html)
    assert author_names == ["Matt"]


def test_returns_empty_list_when_no_value_found():
    """Parsers should return an empty list if no value is foudn"""

    html = """
    <html>
        <body>
            <div>404 page not found :(</div>)
        </body>
    </html>
    """

    class Parser(BaseParser):
        byline_extractors = [
            extract_from_meta_author_tag,  # nope
            extract_from_opengraph_article_author_tag,  # still nope
        ]

    author_names = Parser().extract(html)
    assert author_names == []

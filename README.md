# Parsers in a registry

This POC demonstrates another option for our custom parsers:
registering and finding each through a central repository,
and using a composable pipeline for extracting author names.

## Setup

Clone this repo, create a new virtual env, and install its dependencies:

```shell
$ git clone git@bitbucket.org:mdtz/parsers-registry.git
$ cd parsers-registry
$ python3 -m venv .  # or however you prefer
$ source bin/activate
$ pip install -r requirements.txt
```

## Running tests

This document is useful, but you'll get an even better idea by reading and running
the test suite:

```shell
$ python -m pytest tests/
```

## What is a parser?

At its most simple, a parser is a class that defines one or more domains,
patterns for one or more paths shared across those domains that
the parser can handle, and a means for extraction (our extraction pipeline).

This parser identifies itself as meant for `bloomberg.com`, and capable of
extracting author names

```python
from parsers import BaseParser, CSSSelectorMixin, registry


class BloombergParser(BaseParser, CSSSelectorMixin):
    authors_selector = '.byline
    domains = ['bloomberg.com']
    patterns = [r'/news/articles/']
```

## Registration

A parser is registered with the registry by its domain, e.g., "bloomberg.com".
One domain may have many parsers associated - this is useful for cases where
large editorial sites have many subsections, each with different designs.

```python
registry.register(BloombergParser)
```

or

```python
@registry.register
class BloombergParser(BaseParser):
    pass  # and so on
```

The type of parser above - something that extracts names from a CSS-selected node -
is very common. Instead of creating a class for each, CSS-based parsers can be
registered directly:

```python
# same as BloombergParser
registry.register_simple_css_parser(
    domains=['bloomberg.com'], patterns=[r'/news/articles/'], authors_selector='.byline'
)
```

### Finding parsers once registered

Parsers can be found for a URL by the registry:

```python
parser = registry.get_for_url(
    "https://www.bloomberg.com/news/articles/2019-09-03/uber-argues-driver-names-are-closely-guarded-trade-secrets",
    ignore_subdomain=True,  # ignore "www"
)
```

## Extraction pipeline

Back to composability for a moment - not every extraction is as simple as looking at a selector
or an XPath. Parsers are able to try in serial many extraction methods, stopping only
when there data is found.

Here's an example from the test suite:

```python
from parsers.extractors import extract_from_meta_author_tag, extract_from_opengraph_article_author_tag


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
```

In this example, the HTML document being mined has a `meta[property="article:author"]` tag.
Our pipeline, though, is configured to try first `meta[name="author"]` tag, and then continue
if no results were returned.

## Defining custom parsers

While this package defines three common extractors, you will eventually need your own.
Overriding `BaseParser.get_byline_extractors` allows you to specify your own extraction pipeline.

Here's another example from the test suite:

```python
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
```

Here, we define a custome method on the parser to extract names from the rather awkward HTML example.

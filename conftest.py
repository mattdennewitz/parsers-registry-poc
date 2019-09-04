import pytest

from parsers.registry import ParserRegistry


@pytest.fixture
def registry():
    return ParserRegistry()

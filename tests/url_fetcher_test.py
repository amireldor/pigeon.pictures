"""Test that pigeon pictures' URLs are fetched nicely"""
import pytest
from pigeons import URLFetcher


@pytest.fixture(scope="module")
def fetcher():
    """Creates the actual URLFetcher"""
    return URLFetcher()


def test_fetch_urls(fetcher):
    """Test a successful request to the extenral API"""
    urls = fetcher.fetch_urls()
    assert urls


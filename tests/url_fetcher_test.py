"""Test that pigeon pictures' URLs are fetched nicely"""
# pylint: disable=redefined-outer-name

import pytest
from pigeons import URLFetcher, NoPigeonURLs

@pytest.fixture(scope="module")
def fetcher():
    """Creates the actual URLFetcher"""
    return URLFetcher()


def test_fetch_urls_success(fetcher):
    """Test a successful request to the extenral API"""
    urls = fetcher.fetch_urls()
    assert type(urls) == type([])


def test_fetch_urls_failure(fetcher):
    """Test a successful request to the extenral API"""
    with pytest.raises(NoPigeonURLs):
        _ = fetcher.fetch_urls()

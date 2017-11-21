"""Test that pigeon pictures' URLs are fetched nicely"""
# pylint: disable=redefined-outer-name

import pytest
from pigeons import GoogleCustomSearchFetcher, NoPigeonURLs

@pytest.fixture
def fetcher():
    """Creates the actual URLFetcher"""
    return GoogleCustomSearchFetcher("xxx", "ooo")

def empty_call_google(_):
    """"Mock an empty response from Google"""
    return '''{"items": []}'''

def test_empty_urls_exception(fetcher, monkeypatch):
    """An exception should be raised when no pigeon URLs were found"""
    monkeypatch.setattr(fetcher, 'call_google', empty_call_google)
    with pytest.raises(NoPigeonURLs):
        fetcher.fetch_urls()

"""
TODO:

 [ ] Check exception raising when no results
 [ ] Check that retry works
   [ ] And that it fails after some attempts, to not spam the Google API

"""

"""This will fetch URLs of pigeons for the goodness of time"""
import urllib.request
import urllib.parse
from .search_term_generator import generate


class NoPigeonURLs(Exception):
    """Oh my, no pigeons were found!"""
    pass


class URLFetcher:
    """Fetch the damned URLs from somewhere"""
    def fetch_urls(self):
        """Damned this pylint thing making me write docstrings everywhere"""
        print("...fetch URLs one day>")


class GoogleCustomSearchFetcher:
    """Use the Google Custom Search 'something' (CSE) to find nice images"""
    SEARCH_URL =  "https://www.googleapis.com/customsearch/v1" \
                  "?q={}&cx={}&imgType=photo" \
                  "&safe=medium&searchType=image&fields=items%2Flink&key={}"

    def __init__(self, cse_id, api_key):
        self.cse_id = cse_id
        self.api_key = api_key

    def fetch_urls(self):
        search_term = generate()
        print("hi", self.make_search_url(search_term))

    def make_search_url(self, search_term, page=1):
        search_term = urllib.parse.quote(search_term)
        return self.SEARCH_URL.format(search_term, self.cse_id, self.api_key)

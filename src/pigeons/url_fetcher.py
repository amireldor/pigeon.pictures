"""This will fetch URLs of pigeons for the goodness of time"""
import urllib.request
import urllib.parse
import json
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
    SEARCH_URL = "https://www.googleapis.com/customsearch/v1" \
                 "?q={}&cx={}&imgType=photo" \
                 "&safe=medium&searchType=image&fields=items%2Flink&key={}"

    def __init__(self, cse_id, api_key):
        self.cse_id = cse_id
        self.api_key = api_key

    def fetch_urls(self):
        """You wanna call this and play with the returned value"""
        search_term = generate()
        google_response = self.call_google(search_term)
        return self.get_urls_from_google_response(google_response)

    def call_google(self, search_term):
        """Interact with Google"""
        url = self.make_search_url(search_term)
        with urllib.request.urlopen(url) as response:
            raw = response.read()
            return raw.decode("latin-1")

    def make_search_url(self, search_term):
        """Create the API URL to call"""
        search_term = urllib.parse.quote(search_term)
        return self.SEARCH_URL.format(search_term, self.cse_id, self.api_key)

    def get_urls_from_google_response(self, google_response):
        """Just plays with the actual response from Google and extracts items"""
        response_json = json.loads(google_response)
        return [item["link"] for item in response_json["items"]]

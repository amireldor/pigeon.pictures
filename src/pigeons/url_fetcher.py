"""This will fetch URLs of pigeons for the goodness of time"""
import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
from random import randint
import settings
import logging
from .search_term_generator import generate_pigeon_search_term


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
                 "?q={search_term}&cx={cse_id}&imgType=photo" \
                 "&sort=date:d:s" \
                 "&safe=medium&searchType=image&fields=items%2Flink&key={api_key}"

    def __init__(self, cse_id, api_key):
        self.cse_id = cse_id
        self.api_key = api_key

    def fetch_urls(self):
        """You wanna call this and play with the returned value"""
        logging.info("Starting to fetch your precious URLs")
        search_term = generate_pigeon_search_term()
        logging.info('Search term: "%s"', search_term)
        google_response = self.call_google(search_term)
        urls = self.get_urls_from_google_response(google_response)
        logging.info("Got %d results", len(urls))
        if not urls:
            raise NoPigeonURLs
        else:
            return urls

    def call_google(self, search_term):
        """Interact with Google"""
        url = self.make_search_url(search_term)
        logging.info("Calling %s", url)
        with urllib.request.urlopen(url) as response:
            raw = response.read()
            return raw.decode("latin-1")

    def make_search_url(self, search_term):
        """Create the API URL to call"""
        search_term = urllib.parse.quote(search_term)
        from_date, to_date = self.make_randomized_search_times()
        from_date, to_date = self.make_datetime_to_google_format(
            from_date, to_date)
        return self.SEARCH_URL.format(
            search_term=search_term,
            cse_id=self.cse_id,
            api_key=self.api_key
        )

    @staticmethod
    def make_randomized_search_times():
        """Searches use a random timeframe in the past in an attempt to
        diversify search result. This creates the timespans"""
        days_back = randint(0, settings.MAX_SEARCH_DAYS_BACK)
        to_date = datetime.now() - timedelta(days=days_back)
        from_date = to_date - timedelta(days=settings.SEARCH_DAYS_TIMEFRAME)
        return from_date, to_date

    @staticmethod
    def make_datetime_to_google_format(from_date, to_date):
        """Make the datetime object like google wants"""
        date_format = "%Y%m%d"
        return from_date.strftime(date_format), to_date.strftime(date_format)

    @staticmethod
    def get_urls_from_google_response(google_response):
        """Just plays with the actual response from Google and extracts items"""
        response_json = json.loads(google_response)
        try:
            urls = [item["link"] for item in response_json["items"]]
            return urls
        except KeyError:
            logging.warning("Can't find items in response from Google. Bad stuff")
            logging.warning("JSON: %s", google_response)

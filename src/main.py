"""Pigeon Pictures - pictures of pigeons every X minutes"""

import logging
import settings
from pigeons import URLFetcher, HTMLWriter


def setupLogger():
    """Pretty self-explanatory..."""
    logging.basicConfig(filename=settings.LOG_FILENAME, level=settings.LOG_LEVEL)


def main():
    """Main entry point of the program. I don't know what it will do.
    Hopefully fetch pigeon pictures' URLs and spit them into an HTML"""

    setupLogger()

    fetcher = URLFetcher()
    pigeon_urls = fetcher.fetch_urls()

    writer = HTMLWriter()
    writer.write(settings.HTML_FILE, pigeon_urls)


if __name__ == "__main__":
    main()

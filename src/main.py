"""
Pigeon Pictures - https://pigeon.pictures
  - a site with pictures of pigeons that change every X minutes
"""
import logging
import settings
from pigeons import GoogleCustomSearchFetcher, Jinja2HTMLWriter


def main():
    """Main entry point of the program. I don't know what it will do.
    Hopefully fetch pigeon pictures' URLs and spit them into an HTML."""
    setup_logger()
    logging.info("Hello from Pigeon Pictures!")
    do_pigeon_pictures_magic()
    logging.info("Goodbye.")


def setup_logger():
    """Pretty self-explanatory..."""
    logging.basicConfig(filename=settings.LOG_FILENAME,
                        level=settings.LOG_LEVEL)


def do_pigeon_pictures_magic():
    """By "magic", I mean doing what's this all about. Fetching pigeon URLs
    and writing them nicely to an HTML."""
    fetcher = GoogleCustomSearchFetcher(settings.GOOGLE_CSE_ID, settings.GOOGLE_API_KEY)
    # pigeon_urls = fetcher.fetch_urls()
    pigeon_urls = ["one", "two", "three", "pigeon"]
    writer = Jinja2HTMLWriter(settings.JINJA2_TEMPLATE)
    writer.write(settings.HTML_FILE, pigeon_urls)

if __name__ == "__main__":
    main()

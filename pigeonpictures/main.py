"""
Pigeon Pictures - https://pigeon.pictures
  - a site with pictures of pigeons that change every X minutes
"""
import logging
from pigeonpictures import GoogleCustomSearchFetcher, Jinja2HTMLWriter
from pigeonpictures import settings


def run():
    """Main entry point of the program. I don't know what it will do.
    Hopefully fetch pigeon pictures' URLs and spit them into an HTML."""
    setup_logger()
    logging.info("Hello from Pigeon Pictures!")
    do_pigeon_pictures_magic()
    logging.info("Goodbye.")


def setup_logger():
    """Pretty self-explanatory..."""
    logging.basicConfig(
        filename=settings.LOG_FILENAME,
        level=settings.LOG_LEVEL,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def do_pigeon_pictures_magic():
    """By "magic", I mean doing what's this all about. Fetching pigeon URLs
    and writing them nicely to an HTML."""
    pigeon_urls = fetch_urls()
    write_file(pigeon_urls)


def fetch_urls():
    fetcher = GoogleCustomSearchFetcher(settings.GOOGLE_CSE_ID, settings.GOOGLE_API_KEY)
    pigeon_urls = fetcher.fetch_urls()
    return pigeon_urls


def write_file(pigeon_urls):
    writer = create_writer()
    writer.write(settings.HTML_OUTPUT_FILE, pigeon_urls)


def create_writer():
    return Jinja2HTMLWriter(settings.JINJA2_TEMPLATE, settings.JAVASCRIPT_SNIPPET)


if __name__ == "__main__":
    run()

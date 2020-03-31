"""
Pigeon Pictures - https://pigeon.pictures
  - a site with pictures of pigeons that change every 30 minutes
"""
import logging
from pprint import pprint
from pigeonpictures import Jinja2HTMLWriter
from pigeonpictures.providers import FlickrPigeonPicturesProvider
from pigeonpictures import settings


def main():
    """Main entry point of the program. I don't know what it will do.
    Hopefully fetch pigeon pictures' URLs and spit them into an HTML."""
    setup_logger()
    logging.info("Hello from Pigeon Pictures!")
    run_pigeon_pictures_logic()
    logging.info("Goodbye.")


def setup_logger():
    """Pretty self-explanatory..."""
    logging.basicConfig(
        filename=settings.LOG_FILENAME,
        level=settings.LOG_LEVEL,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def run_pigeon_pictures_logic():
    """Doing what's this all about. Fetching pigeon URLs and writing them
    nicely to an HTML."""
    pigeon_urls = fetch_urls()
    pprint(pigeon_urls)
    # write_file(pigeon_urls)


def fetch_urls():
    fetcher = FlickrPigeonPicturesProvider()
    pigeon_urls = fetcher.get_pigeon_pictures()
    return pigeon_urls


def write_file(pigeon_urls):
    writer = create_writer()
    writer.write(settings.HTML_OUTPUT_FILE, pigeon_urls)


def create_writer():
    return Jinja2HTMLWriter(settings.JINJA2_TEMPLATE, settings.JAVASCRIPT_SNIPPET)


if __name__ == "__main__":
    main()

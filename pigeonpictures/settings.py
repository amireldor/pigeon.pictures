"""Various interesting Pigeon Pictures settings"""
from os import getenv, path

import logging

LOG_FILENAME = "log.pigeon.log"
LOG_LEVEL = logging.INFO

dirname = path.dirname(__file__)
HTML_OUTPUT_FILE = path.join(dirname, "../public/index.html")
JAVASCRIPT_SNIPPET = path.join(dirname, "../frontend/index.js")
JINJA2_TEMPLATE = path.join(dirname, "template.j2")

MAX_SEARCH_DAYS_BACK = 200
SEARCH_DAYS_TIMEFRAME = 180

GOOGLE_CSE_ID = getenv("GOOGLE_CSE_ID")
GOOGLE_API_KEY = getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY is None or GOOGLE_API_KEY is None:
    logging.error(
        "Please provide environment variables GOOGLE_CSE_ID, GOOGLE_API_KEY for fetching pigeon pictures"
    )

    exit(1)

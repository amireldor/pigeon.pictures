"""Various interesting Pigeon Pictures settings"""
import logging
from private import *  # pylint: disable=wildcard-import,unused-wildcard-import

LOG_FILENAME = "pigeon.log"
LOG_LEVEL = logging.INFO

HTML_FILE = "../public/index.html"
JINJA2_TEMPLATE = "template.j2"

MAX_SEARCH_DAYS_BACK = 200
SEARCH_DAYS_TIMEFRAME = 30

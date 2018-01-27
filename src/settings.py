"""Various interesting Pigeon Pictures settings"""
import logging
try:
    from private import *  # pylint: disable=wildcard-import,unused-wildcard-import
except ImportError:
    logging.warn("No 'private' module! You might be doing some silly. See 'private.template.py'.")

LOG_FILENAME = "log.pigeon.log"
LOG_LEVEL = logging.INFO

HTML_OUTPUT_FILE = "../public/index.html"
JAVASCRIPT_SNIPPET = "frontend/index.js"
JINJA2_TEMPLATE = "template.j2"

MAX_SEARCH_DAYS_BACK = 200
SEARCH_DAYS_TIMEFRAME = 30

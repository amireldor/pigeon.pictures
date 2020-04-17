"""Various interesting Pigeon Pictures settings"""
from os import getenv, path

import logging

LOG_FILENAME = "log.pigeon.log"
LOG_LEVEL = logging.INFO

dirname = path.dirname(__file__)
HTML_OUTPUT_FILE = path.join(dirname, "../public/index.html")
JAVASCRIPT_SNIPPET = path.join(dirname, "../frontend/index.js")
JINJA2_TEMPLATE = path.join(dirname, "template.j2")

# TODO: adapt to flickr search
MAX_SEARCH_DAYS_BACK = 200
SEARCH_DAYS_TIMEFRAME = 180

# TODO :remove when Google is dead from this project
GOOGLE_CSE_ID = getenv("GOOGLE_CSE_ID")
GOOGLE_API_KEY = getenv("GOOGLE_API_KEY")
S3_BUCKET_NAME = getenv("S3_BUCKET_NAME", "pigeon.pictures")
FLICKR_API_KEY = getenv("FLICKR_API_KEY")
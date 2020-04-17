import json
import logging
from typing import List
from urllib.request import urlopen
from urllib.parse import quote
from urllib.error import URLError, HTTPError
from random import randint, shuffle
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import copy

from pigeonpictures.settings import FLICKR_API_KEY
from . import PigeonPicture, PigeonPicturesBaseProvider, InvalidPigeonPicture

FLICKR_API_ENDPOINT: str = "https://www.flickr.com/services/rest/"

# for photos returned from flickr API, not in relative size order, you should randomize this every time for best results
photo_keys_to_try = ["url_t", "url_s", "url_q", "url_c", "url_l", "url_m", "url_n", "url_z",]


def parse_json_from_response(response):
    raw = response.read()
    as_string = raw.decode("utf-8")
    logging.info("Attempt to read JSON from response")
    return json.loads(as_string)


class FlickrPigeonPicturesProvider(PigeonPicturesBaseProvider):
    def __init__(self):
        if FLICKR_API_KEY is None:
            message = "No FLICKR_API_KEY but trying to use the flickr provider! Define a FLICKR_API_KEY environment variable!"
            logging.error(message)
            raise RuntimeError(message)

    def get_pigeon_pictures(self) -> List[PigeonPicture]:
        url = self.build_search_url()
        logging.info(f"Opening URL to find out how many pages of pigeons there are: {url}")
        response = urlopen(url, timeout=10)

        parsed_response = parse_json_from_response(response)
        pages = parsed_response["photos"]["pages"]

        page_we_want = randint(1, min(pages, 200))  # I think flickr got bugs with high page numbers returning the same results
        url = self.build_search_url(page_we_want)
        logging.info(f"Opening URL with page {page_we_want}: {url}")
        response = urlopen(url, timeout=10)

        parsed_response = parse_json_from_response(response)
        photos = parsed_response["photos"]["photo"]

        logging.info(f"Got {len(photos)} photos")

        def ignore_photo_if_invalid(photo):
            try:
                return make_pigeon_picture_from_flickr_photo(photo)
            except InvalidPigeonPicture:
                return None

        pigeon_pictures: List[PigeonPicture] = [
            ignore_photo_if_invalid(photo) for photo in photos
        ]

        pigeon_pictures = [
            picture for picture in pigeon_pictures if picture is not None
        ]

        return pigeon_pictures

    @staticmethod
    def build_search_url(page: int = 1) -> str:
        method = "flickr.photos.search"
        public_photos = 1  # flickr 'enum'
        licenses = "10,9,6,5,4,3,2,1"
        # <licenses>
        #   <license id="0" name="All Rights Reserved" url="" />
        #   <license id="1" name="Attribution-NonCommercial-ShareAlike License" url="https://creativecommons.org/licenses/by-nc-sa/2.0/" />
        #   <license id="2" name="Attribution-NonCommercial License" url="https://creativecommons.org/licenses/by-nc/2.0/" />
        #   <license id="3" name="Attribution-NonCommercial-NoDerivs License" url="https://creativecommons.org/licenses/by-nc-nd/2.0/" />
        #   <license id="4" name="Attribution License" url="https://creativecommons.org/licenses/by/2.0/" />
        #   <license id="5" name="Attribution-ShareAlike License" url="https://creativecommons.org/licenses/by-sa/2.0/" />
        #   <license id="6" name="Attribution-NoDerivs License" url="https://creativecommons.org/licenses/by-nd/2.0/" />
        #   <license id="7" name="No known copyright restrictions" url="https://www.flickr.com/commons/usage/" />
        #   <license id="8" name="United States Government Work" url="http://www.usa.gov/copyright.shtml" />
        #   <license id="9" name="Public Domain Dedication (CC0)" url="https://creativecommons.org/publicdomain/zero/1.0/" />
        #   <license id="10" name="Public Domain Mark" url="https://creativecommons.org/publicdomain/mark/1.0/" />
        # </licenses>
        # See https://www.flickr.com/services/api/flickr.photos.licenses.getInfo.html)
        # max_upload_date =  # unix unixtimestamp (for 'randomization')
        params = {
            "api_key": FLICKR_API_KEY,
            "method": method,
            "format": "json",
            "nojsoncallback": "1",
            "license": licenses,
            "public_photos": 1,
            "extras": "owner_name,license,media," + ",".join(photo_keys_to_try),
            "per_page": 20,
            "tag_mode": "any",
            "tags": "pigeon,pigeons",
            "page": str(page),
        }
        query_string = "&".join(f"{key}={value}" for key, value in params.items())
        return f"{FLICKR_API_ENDPOINT}?{query_string}"

def make_pigeon_picture_from_flickr_photo(photo) -> PigeonPicture:
    try:
        photo_url = None
        photos_key_sizes_to_try = copy(photo_keys_to_try)
        shuffle(photos_key_sizes_to_try)
        for photo_key in photos_key_sizes_to_try:
            try:
                photo_url = photo[photo_key]
                break
            except KeyError:
                pass

        if photo_url is None:
            raise InvalidPigeonPicture("No photo URL found for flickr photo")

        author = photo["ownername"]
        author_url = make_flickr_author_url(photo["owner"])
        picture_page_url = make_flickr_picture_page_url(photo["owner"], photo["id"])
        license = "TBD"
        license_url = "TBD"

        return PigeonPicture(
            picture_url=photo_url,
            picture_page_url=picture_page_url,
            author=author,
            author_url=author_url,
            license=license,
            license_url=license_url,
            pigeon_pictures_provider="flickr",
        )
    except KeyError as error:
        logging.error(f"Can't find key in flickr photo f{error}")
        raise InvalidPigeonPicture

def make_flickr_author_url(owner_id: str):
    return f"https://www.flickr.com/people/{owner_id}/"

def make_flickr_picture_page_url(owner_id: str, photo_id: str):
    return f"https://www.flickr.com/photos/{owner_id}/{photo_id}/"

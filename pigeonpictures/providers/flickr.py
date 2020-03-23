import json
from typing import List
from urllib.request import urlopen
from urllib.parse import quote
from urllib.error import URLError, HTTPError
from logging import Logger
from random import randint
from concurrent.futures import ThreadPoolExecutor, as_completed

from pigeonpictures.settings import FLICKR_API_KEY
from pigeonpictures.search_term_generator import generate_pigeon_search_term
from . import PigeonPicture, PigeonPicturesBaseProvider

logger = Logger("FlickrPigeonPicturesProvider")
FLICKR_API_ENDPOINT: str = "https://www.flickr.com/services/rest/"


def parse_json_from_response(response):
    raw = response.read()
    as_string = raw.decode("utf-8")
    logger.info("Attempt to read JSON from response")
    return json.loads(as_string)


class FlickrPigeonPicturesProvider(PigeonPicturesBaseProvider):
    def __init__(self):
        if FLICKR_API_KEY is None:
            message = "No FLICKR_API_KEY but trying to use the flickr provider! Define a FLICKR_API_KEY environment variable!"
            logger.error(message)
            raise RuntimeError(message)

    def get_pigeon_pictures(self) -> List[PigeonPicture]:
        search_term = generate_pigeon_search_term()
        url = self.build_search_url(search_term)

        logger.info(f"Will call flickr API with search_term '{search_term}'")
        logger.info(f"Opening URL: {url}")
        response = urlopen(url, timeout=3)

        photos = parse_json_from_response(response)["photos"]["photo"]
        logger.info(f"Got {len(photos)} photos")

        enriched = self.enrich_photos(photos)
        print("enriched", enriched)
        print("KKEN", len(enriched))

        return []

    @staticmethod
    def build_search_url(query: str) -> str:
        method = "flickr.photos.search"
        search = quote(query)
        public_photos = 1  # flickr 'enum'
        page = 1
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
        params = f"api_key={FLICKR_API_KEY}&method={method}&format=json&nojsoncallback=1&text={search}&privacy_filter={public_photos}&per_page=20&page={page}&license={licenses}&private_filter=1"
        return f"{FLICKR_API_ENDPOINT}?{params}"

    def enrich_photos(self, photos):
        photo_ids_to_photos = {photo["id"]: photo for photo in photos}
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures_to_photo_id = {
                executor.submit(self.call_enricher, photo_id): photo_id
                for photo_id in photo_ids_to_photos.keys()
            }

            for future in as_completed(futures_to_photo_id):
                photo_id = futures_to_photo_id[future]
                photo_info = future.result()
                photo_ids_to_photos[photo_id]["photo_info"] = photo_info

        return photo_ids_to_photos.values()

    def call_enricher(self, photo_id):
        enricher = FlickrPhotoEnricher()
        try:
            return enricher.get_photo_info(photo_id)
        except (URLError, HTTPError) as error:
            logger.error(f"Error while enriching photo_info: {error}")
            print(error)


class FlickrPhotoEnricher:
    def get_photo_info(self, photo_id):
        url = self.build_photo_info_url(photo_id)
        response = urlopen(url, timeout=3)
        as_json = parse_json_from_response(response)
        photo_info = as_json["photo"]
        return photo_info

    def build_photo_info_url(self, photo_id) -> str:
        method = "flickr.photos.getInfo"
        params = f"api_key={FLICKR_API_KEY}&method={method}&photo_id={photo_id}&format=json&nojsoncallback=1"
        return f"{FLICKR_API_ENDPOINT}?{params}"

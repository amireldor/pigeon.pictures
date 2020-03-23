from abc import ABC, abstractmethod
from typing import NamedTuple, List


class PigeonPicture(NamedTuple):
    picture_url: str
    author: str
    pigeon_pictures_provider: str
    license: str
    license_url: str


class PigeonPicturesBaseProvider(ABC):
    @abstractmethod
    def get_pigeon_pictures(self) -> List[PigeonPicture]:
        raise NotImplemented


class InvalidPigeonPicture(Exception):
    pass

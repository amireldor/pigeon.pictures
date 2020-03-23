from abc import ABC, abstractmethod
from typing import NamedTuple, List


class PigeonPicture(NamedTuple):
    image_url: str
    author: str
    pigeon_pictures_provider: str


class PigeonPicturesBaseProvider(ABC):
    @abstractmethod
    def get_pigeon_pictures(self) -> List[PigeonPicture]:
        raise NotImplemented

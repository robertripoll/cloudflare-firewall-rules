from json import load as json_load, dump as json_dump
from os.path import exists as path_exists

from cache.base import DEFAULT_CACHE, Cache

DEFAULT_PATH = "/tmp/cloudflare_ips.json"


class FileCache(Cache):
    """
    This class is an implementation of the Cache abstract base class that
    stores the cache data in a file.

    The data is stored in JSON format in the file located at the path
    provided in the constructor.
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self.cache = {}
        self.__load()

    def __init(self) -> None:
        with open(self.path, 'w', encoding='utf-8') as file:
            json_dump(DEFAULT_CACHE, file)

    def __load(self) -> None:
        if not path_exists(self.path):
            self.__init()

        with open(self.path, 'r', encoding='utf-8') as file:
            self.cache = json_load(file)

    def _save(self) -> None:
        with open(self.path, 'w', encoding='utf-8') as file:
            json_dump(self.cache, file)

    def has(self, key: str) -> bool:
        return key in self.cache

    def get(self, key: str) -> str | list[str]:
        if not self.has(key):
            raise KeyError

        return self.cache[key]

    def set(self, key: str, value: str | list[str]) -> None:
        self.cache[key] = value

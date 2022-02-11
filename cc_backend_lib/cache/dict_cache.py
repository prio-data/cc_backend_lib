
from typing import TypeVar
from pymonad.maybe import Maybe, Just, Nothing
from . import base_cache

T = TypeVar("T")

class DictCache(base_cache.BaseCache[T]):
    def __init__(self):
        self._dict = {}

    def get(self, key: str) -> Maybe[T]:
        try:
            return Just(self._dict[key])
        except KeyError:
            return Nothing

    def set(self, key: str, val: T) -> None:
        self._dict[key] = val

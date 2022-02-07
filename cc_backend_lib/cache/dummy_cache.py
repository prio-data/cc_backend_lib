
from typing import Any
from pymonad.maybe import Nothing, Maybe, Just
from . import cache

class DummyCache(cache.Cache[Any]):
    def __init__(self):
        self._dict = {}

    def _get(self, key: str) -> Maybe[Any]:
        try:
            return Just(self._dict[key])
        except KeyError:
            return Nothing

    def _set(self, key: str, value: Any):
        self._dict[key] = value

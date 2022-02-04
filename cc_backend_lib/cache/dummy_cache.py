
from typing import Any
from pymonad.maybe import Nothing
from . import cache

class DummyCache(cache.Cache):
    def __getitem__(self, _: Any) -> Nothing:
        return Nothing

    def __setitem__(self, _, __):
        pass


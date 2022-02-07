
import unittest
from cc_backend_lib.cache import dummy_cache

class TestDummyCache(unittest.TestCase):

    def test_basic_caching(self):

        @dummy_cache.DummyCache.cache()
        def caching_fn(x: int, y: int):
            return x + y

        caching_fn(10, 10)
        caching_fn(20, 10)

        print(caching_fn._dict)


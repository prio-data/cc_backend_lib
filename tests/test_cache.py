
import asyncio
import unittest
from cc_backend_lib.cache import cache, dict_cache, signature

class TestCache(unittest.TestCase):
    def test_sig(self):
        cases = [
                (None, None),
                (["a"], None),
                ([1,2,3], {"a": "b"}),
            ]
        for args, kwargs in cases:
            self.assertEqual(
                    signature.make_signature(args, kwargs),
                    signature.make_signature(args, kwargs)
                )

    def test_dict_cache(self):
        called = {"n": 0}

        @cache.cache(dict_cache.DictCache)
        def my_function(a,b):
            called["n"] += 1
            return a+b

        my_function(1,1)
        my_function(2,2)
        my_function(3,3)
        my_function(2,2)
        my_function(1,1)

        self.assertEqual(called["n"], 3)

    def test_conditional(self):
        called = {"n": 0}

        @cache.cache(dict_cache.DictCache, lambda a,b: a == 1)
        def my_function(a,b):
            called["n"] += 1
            return a+b

        my_function(1,1)
        my_function(2,2)
        my_function(3,3)
        my_function(2,2)
        my_function(1,1)

        self.assertEqual(called["n"], 4)

    def test_async_cache(self):
        called = {"n": 0}
        @cache.cache(dict_cache.DictCache)
        async def my_function(a,b):
            called["n"] += 1
            return a+b

        async def _test():
            await my_function(1,1)
            await my_function(1,1)
            await my_function(2,1)

        asyncio.run(_test())
        self.assertEqual(called["n"], 2)

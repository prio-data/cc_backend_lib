
from typing import Optional
import redis
from . import base_cache

class RedisCache(base_cache.BaseCache[str]):
    def __init__(self,
            host: str,
            expiry_time: Optional[int] = 10,
            port: int = 6379,
            db: int = 0):

        super().__init__()

        self._redis = redis.Redis(host = host, port = port, db = db)
        self._expiry_time = expiry_time

    def get(self, key: str) -> str:
        return self._redis.get(self._key(key)).decode()

    def set(self, key: str, val: str) ->  None:
        self._redis.set(self._key(key), val, ex = self._expiry_time)

    def _key(self, key: int):
        return self._name + "/" + str(key)

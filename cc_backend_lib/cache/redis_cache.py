
from typing import Optional
import redis
from . import base_cache

class RedisCache(base_cache.BaseCache[str]):
    def __init__(self, host: str, port: int, db: int, expiry_time: Optional[int] = 10):
        self._redis = redis.Redis(host = host, port = port, db = db)
        self._expiry_time = expiry_time

    def get(self, key: str) -> str:
        return self._redis.get(key).decode()

    def set(self, key: str, val: str) ->  None:
        self._redis.set(key, val, ex = self._expiry_time)


from typing import Any
import pickle
import redis
from . import cache

class RedisCache(cache.Cache[Any]):
    def __init__(self, redis_client: redis.Redis, expiration_time: int):
        self._client = redis_client
        self._ex = expiration_time

    def _get(self, key: str) -> Any:
        return pickle.loads(self._client.get(key))

    def _set(self, key: str, value: Any):
        self._client.set(key, pickle.dumps(value), ex = self._ex)

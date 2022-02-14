
import logging
from typing import Optional
from pymonad.maybe import Just, Nothing, Maybe
import redis
from . import base_cache

logger = logging.getLogger(__name__)

class RedisCache(base_cache.BaseCache[str]):
    def __init__(self,
            host: str,
            expiry_time: Optional[int] = 10,
            port: int = 6379,
            db: int = 0):

        super().__init__()

        self._redis = redis.Redis(host = host, port = port, db = db)
        self._expiry_time = expiry_time
        logger.debug(f"Initialized redis cache: redis://{host}:{port}/{db}")

    def get(self, key: str) -> Maybe[str]:
        value = self._redis.get(self._key(key))
        if value is None:
            return Nothing
        else:
            logger.info(f"Returning {self._key(key)} from cache")
            return Just(value.decode())

    def set(self, key: str, val: str) ->  None:
        logger.info(f"Setting {self._key(key)} in cache")
        self._redis.set(self._key(key), val, ex = self._expiry_time)

    def _key(self, key: int):
        return self._name + "/" + str(key)

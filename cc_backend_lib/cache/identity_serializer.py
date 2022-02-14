
from . import cache_serializer

class IdentitySerializer(cache_serializer.CacheSerializer[bytes]):
    def loads(self, data: bytes) -> bytes:
        return data

    def dumps(self, value: bytes) -> bytes:
        return value

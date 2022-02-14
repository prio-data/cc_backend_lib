
from typing import TypeVar, Generic
import abc

T = TypeVar("T")

class CacheSerializer(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def loads(self, data: bytes) -> T:
        pass

    @abc.abstractmethod
    def dumps(self, value: T) -> bytes:
        pass

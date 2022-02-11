
from pymonad.maybe import Maybe
from typing import Generic, TypeVar
from abc import ABC, abstractmethod

T = TypeVar("T")

class BaseCache(ABC, Generic[T]):
    """
    BaseCache
    =========

    Base class for caches.
    """

    @abstractmethod
    def get(self, key: int) -> Maybe[T]:
        pass

    @abstractmethod
    def set(self, key: int, val: T) -> None:
        pass


from typing import Generic, TypeVar
from abc import ABC, abstractmethod
from pymonad.maybe import Maybe

T = TypeVar("T")

class BaseCache(ABC, Generic[T]):
    """
    BaseCache
    =========

    Base class for caches.
    """
    def __init__(self):
        self._name = None

    @abstractmethod
    def get(self, key: int) -> Maybe[T]:
        pass

    @abstractmethod
    def set(self, key: int, val: T) -> None:
        pass

    def _key(self, key:int):
        return self._name + "/" + str(key) if self._name is not None else str(key)

    def set_name(self, name: str):
        self._name = name


import abc
from typing import TypeVar, Generic
from pymonad.maybe import Maybe

T = TypeError("T")
U = TypeVar("U")

class Cache(abc.ABC, Generic[T,U]):

    @abc.abstractmethod
    def __getitem__(self, key: T) -> Maybe[U]:
        pass

    @abc.abstractmethod
    def __setitem__(self, key: T, value: U):
        pass

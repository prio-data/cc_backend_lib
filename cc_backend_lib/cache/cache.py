
import abc
import hashlib
from typing import Generic, Any, List, Dict, TypeVar
from pymonad.maybe import Maybe

T = TypeVar("T")

class Cache(abc.ABC, Generic[T]):
    _fn = None

    @abc.abstractmethod
    def _get(self, key: str) -> Maybe[T]:
        pass

    @abc.abstractmethod
    def _set(self, key: str, value: T):
        pass

    def decorate(self, fn):
        if self._fn is not None:
            raise ValueError((
                    "Tried to decorate twice with the same cache. "
                    "Each instance can only decorate one function!"))
        self._fn = fn

    def _args_to_identifier(self, args: List[Any], kwargs: Dict[str, Any]) -> str:
        kwargs = list(kwargs.items())
        return hashlib.sha256(
                (str(hash(args)) + str(hash(kwargs))).encode()).hexdigest()

    def __call__(self, *args, **kwargs):
        if self._fn is None:
            raise AttributeError("Not assigned to a function. Have you called 'decorate'?")

        key = self._args_to_identifier(args, kwargs)
        value = self._get(key)

        if value.is_nothing():
            value = self._fn(*args, **kwargs)
            self._set(key, value)

        return value

    @classmethod
    def cache(cls, *args, **kwargs):
        instance = cls(*args, **kwargs)
        def wrapper(fn):
            instance.decorate(fn)
            return instance
        return wrapper

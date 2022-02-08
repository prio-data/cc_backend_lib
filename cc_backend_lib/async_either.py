from typing import Callable, TypeVar, Coroutine
from pymonad.either import Either

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")

class AsyncEither(Either):
    """
    AsyncEither
    ===========

    A proposed extension of the excellent pymonad library, which is widely used
    in this library. This extension lets you map asynchronously, which is
    necessary to avoid convoluted syntax when making many async requests that
    return eithers.
    """
    async def async_map(self, function: Callable[[Either[T,U]],Coroutine[Either[V,W], None, None]]) -> Coroutine[Either[V,W], None, None]:
        if self.is_left():
            return self
        else:
            result = await function(self.value)
            return self.__class__(result, (None, True))

    async def async_then(self, function: Callable[[Either[T,U]],Coroutine[Either[V,W], None, None]]) -> Coroutine[Either[V,W], None, None]:
        result = await self.async_map(function)
        try:
            return result.join()
        except (TypeError, AttributeError):
            return result

    @classmethod
    def from_either(cls, regular_either: Either[T,U]) -> "AsyncEither[T,U]":
        return cls(regular_either.value, regular_either.monoid)

    def to_either(self: "AsyncEither[T,U]") -> Either[T,U]:
        return Either(self.value, self.monoid).join()

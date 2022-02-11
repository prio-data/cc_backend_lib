
import inspect
import functools
from typing import TypeVar, Callable, Any, List, Dict
from toolz.functoolz import curry, compose
from . import base_cache, signature

T = TypeVar("T")

def _always_true(*_, **__):
    return True

def _sync_wrapper(cache_class, conditional, fn: Callable[[Any], T]):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if conditional(*args, **kwargs):
            sig = signature.make_signature(args, kwargs)
            fn_then_cache = compose(curry(cache_class.set, sig), fn)
            proc = cache_class.get(sig).maybe(lambda: fn_then_cache(*args, **kwargs), lambda x: lambda: x)
            return proc()
        else:
            return fn(*args, **kwargs)
    return inner

def _async_wrapper(cache_class, conditional, fn: Callable[[Any], T]):
    @functools.wraps(fn)
    async def inner(*args, **kwargs):
        if conditional(*args, **kwargs):
            sig = signature.make_signature(args, kwargs)
            if (cached := cache_class.get(sig)).is_just():
                return cached.value
            else:
                value = await fn(*args, **kwargs)
                cache_class.set(sig, value)
                return value
        else:
            return await fn(*args, **kwargs)
    return inner

def _wrapper(cache_class, conditional, fn):
    wrapper_fn = _sync_wrapper if not inspect.iscoroutinefunction(fn) else _async_wrapper
    cache_class.set_name(fn.__name__)
    return wrapper_fn(cache_class, conditional, fn)

def cache(
        cache_class: base_cache.BaseCache[T],
        conditional: Callable[[List[Any], Dict[str, Any]], bool] = _always_true):
    """
    cache
    =====

    parameters:
        cache_class (base_cache.BaseCache)
        conditional (Callable[[List[Any], Dict[str, Any]])

    Decorator that caches function results using the provided class. The class
    must be a subclass of base_cache, providing get and set methods with
    appropriate signatures.

    An optional conditional can be passed, which receives the *args and
    **kwargs of the called function. This function determines whether or not to
    cache, or to always recompute, based on whether it returns True or False.
    """
    return curry(_wrapper, cache_class, conditional)


import logging
import inspect
import functools
from typing import TypeVar, Callable, Any, List, Dict
from toolz.functoolz import curry, compose
from . import base_cache, signature, cache_serializer

logger = logging.getLogger(__name__)
T = TypeVar("T")

def _always_true(*_, **__):
    return True

def _sync_wrapper(cache_class, serializer_class, conditional, fn: Callable[[Any], T]):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if conditional(*args, **kwargs):
            logger.info(f"Conditional returned True with *{str(args)} / **{str(kwargs)}")
            sig = signature.make_signature(args, kwargs)
            fn_then_cache = compose(curry(cache_class.set, sig), serializer_class.dumps, fn)
            get_from_cache = compose(lambda r: r.then(serializer_class.loads), cache_class.get)
            proc = get_from_cache(sig).maybe(lambda: fn_then_cache(*args, **kwargs), lambda x: lambda: x)
            return proc()
        else:
            logger.info(f"Conditional returned False with *{str(args)} / **{str(kwargs)}")
            return fn(*args, **kwargs)
    return inner

def _async_wrapper(cache_class, serializer_class, conditional, fn: Callable[[Any], T]):
    @functools.wraps(fn)
    async def inner(*args, **kwargs):
        if conditional(*args, **kwargs):
            logger.info(f"Conditional returned True with *{str(args)} / **{str(kwargs)}")
            sig = signature.make_signature(args, kwargs)
            if (cached := cache_class.get(sig)).is_just():
                return serializer_class.loads(cached.value)
            else:
                value = await fn(*args, **kwargs)
                cache_class.set(sig, serializer_class.dumps(value))
                return value
        else:
            logger.info(f"Conditional returned False with *{str(args)} / **{str(kwargs)}")
            return await fn(*args, **kwargs)
    return inner

def _wrapper(cache_class, serializer_class, conditional, fn):
    wrapper_fn = _sync_wrapper if not inspect.iscoroutinefunction(fn) else _async_wrapper
    cache_class.set_name(fn.__name__)
    return wrapper_fn(cache_class, serializer_class, conditional, fn)

def cache(
        cache_class: Callable[[], base_cache.BaseCache[T]],
        serializer: Callable[[], cache_serializer.CacheSerializer],
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
    serializer_instance = serializer()
    cache_instance = cache_class()
    return curry(_wrapper, cache_instance, serializer_instance, conditional)

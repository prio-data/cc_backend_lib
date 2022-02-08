"""
helpers
=======

A module containing various helper functions that are useful when doing
functional programming with toolz.functoolz and pymonad.
"""
from operator import add
from typing import TypeVar, Union, List
from toolz.functoolz import reduce
from pymonad.either import Either, Left, Right

from cc_backend_lib.errors import http_error

T = TypeVar("T")
U = TypeVar("U")

def dictadd(a,b):
    return dict(list(a.items()) + list(b.items()))

def combine_http_errors(results: List[Either[http_error.HttpError, T]]) -> Either[http_error.HttpError, List[T]]:
    errors = [extract_either(r) for r in results if r.is_left()]
    if errors:
        return Left(reduce(add, errors))
    else:
        return Right([extract_either(r) for r in results])

def extract_either(e: Either[T,U]) -> Union[T,U]:
    return e.either(lambda x:x, lambda x:x)

def expand_kwargs(fn, kwargs):
    return fn(**kwargs)

def expand_args(fn, args):
    return fn(*args)

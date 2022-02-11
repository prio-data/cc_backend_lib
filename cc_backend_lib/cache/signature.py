import logging
import pickle
from typing import List, Dict, Any, Optional

def make_signature(args: Optional[List[Any]] = None, kwargs: Optional[Dict[str, Any]] = None):
    """
    make_signature
    ==============

    Turns *args and **kwargs into a hash. Used to make unique cache keys from
    function arguments.
    """
    sig = tuple()
    if args:
        sig += tuple(args)
    if kwargs:
        sig += tuple(kwargs.items())
    return hash(pickle.dumps(sig))

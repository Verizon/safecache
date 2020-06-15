# Copyright 2020 Verizon Inc.
# Licensed under the terms of the Apache License 2.0.
# See LICENSE file in project root for terms.

"""
safecache.safecache
===================

This module implements safecache.
"""

from collections import deque
from collections import namedtuple
from copy import deepcopy
from functools import wraps
from hashlib import sha1
from threading import Lock
from threading import RLock
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Text
from typing import Tuple
from typing import Type

import builtins
import math
import time
import types
import weakref

try:
    import cPickle as pickle
except ImportError:
    import pickle

from .exceptions import CacheExpired
from .exceptions import CacheMiss


IMMUTABLE_TYPES: Tuple[Type] = (
    builtins.bool,
    builtins.bytes,
    builtins.complex,
    builtins.float,
    builtins.frozenset,
    builtins.int,
    builtins.range,
    builtins.slice,
    builtins.str,
    builtins.tuple,
    builtins.type(Ellipsis),
    builtins.type(None),
    builtins.type(NotImplemented),
    builtins.type,
    types.BuiltinFunctionType,
    types.FunctionType,
    weakref.ref,
)


is_immutable: Callable = lambda obj: builtins.isinstance(obj, IMMUTABLE_TYPES)

is_mutable: Callable = lambda obj: not is_immutable(obj)


def mutabletypeguard(function) -> Any:
    @wraps(function)
    def wrapper(*a, **kw) -> Any:
        result: Any = function(*a, **kw)
        if is_mutable(obj=result):
            # escalate a copy of the mutable objects to protect
            # them from mutation (by indirect operations).
            return deepcopy(result)
        return result
    return wrapper


#
# Cache information
#


class CacheDescriptor(object):
    """safecache description"""

    __slots__ = "hits", "misses", "maxsize", "currsize"

    def __init__(self, hits: int, misses: int, currsize: int, maxsize: int, **kw):
        self.currsize = currsize
        self.hits = hits
        self.maxsize = maxsize
        self.misses = misses

    def __repr__(self):
        # preserve similar semantics as lru_cache's info.
        return f"{self.__class__.__name__}(%s)" % (
            ", ".join((
                f"{slot}={repr(getattr(self, slot))}"
                for slot in iter(self.__slots__)
            ))
        )


class CacheInfo(CacheDescriptor):
    """`CacheDescriptor` alias for @lru_cache compatibility"""

    def __init__(self, *a, **kw):
        super(CacheInfo, self).__init__(*a, **kw)

    def __repr__(self):
        return super().__repr__()


#
# Cache timing (TTL)
#


now = lambda: time.time() // 1


#
# safecache
#


Cache = namedtuple("Cache", ("expiry", "value"))


def safecache(
        maxsize: int = None,
        ttl: float = math.inf,
        miss_callback: Callable = lambda _: _,
        *a, **kw):
    """safecache decorator implementation.

    Args
    ====
    maxsize -- maximum cache entry size.
    ttl -- maximum freshness of cache entry (in seconds).
    miss_callback -- custom cache-miss callback function.
    """
    if maxsize is None:
        # static upper bound for None
        maxsize = math.inf

    elif maxsize <= 0:
        # negative is normalized to 1
        maxsize = 1

    if ttl <= .0:
        # negative time-to-live (ttl) is normalized to "always-revalidate" state.
        # This results in zero caching and 100% fetching from origin function.
        ttl = .0

    r_mutex = RLock()  # lock for cache read
    w_mutex = Lock()   # lock for cache write

    cache: Dict = {}   # cache buffer
    hits = misses = 0  # cache stats

    pq: deque = (  # LRU priority queue
        deque() if maxsize == math.inf
        else deque(maxlen=maxsize)
    )

    def _pq_inpl_swap(i: int, j: int) -> None:
        pq[i], pq[j] = pq[j], pq[i]

    def _cache_info() -> CacheInfo:
        nonlocal hits, maxsize, misses
        # if `cache` is accessed by multiple threads then `currsize`,
        # although atomic, will represent near-approximate cache size.
        currsize: int = len(cache)
        return CacheInfo(**locals())

    def impl(function):
        @wraps(function)
        @mutabletypeguard
        def wrapper(*entry, **kw):
            nonlocal hits, misses
            # normalize parameters to hashable strings.
            key: Text = sha1(pickle.dumps((*entry, kw), protocol=3)).hexdigest()
            try:
                if key not in cache:
                    raise CacheMiss
                # check if cache has expired. Expiration is determined from the
                # heuristics of current time and pre-determined expiration date.
                elif ttl != math.inf and cache.__getitem__(key).expiry <= now():
                    raise CacheExpired
                with r_mutex:
                    # this swap behavior is not completely compliant with the LRU
                    # algorithm, but was decided since intermediate "priorities"
                    # are not as important as the end nodes (highest/lowest).
                    _pq_inpl_swap(pq.index(key), -1)
                    pq.appendleft(pq.pop())
                    hits += 1
            except CacheMiss:
                result: Any = miss_callback(function(*entry, **kw))
                node = Cache(value=result, expiry=now() + ttl)
                with w_mutex:
                    if len(pq) == maxsize:
                        cache.__delitem__(pq.pop())
                    cache.__setitem__(key, node)
                    pq.appendleft(key)
                    misses += 1
            except CacheExpired:
                # for expired caches, pull a version that's expected to be
                # fresh and update the existing cache's attributes/values.
                result: Any = function(*entry, **kw)
                node = Cache(value=result, expiry=now() + ttl)
                with w_mutex:
                    cache.__setitem__(key, node)
                    _pq_inpl_swap(pq.index(key), -1)
                    pq.appendleft(pq.pop())
                    hits += 1
            return cache.__getitem__(key).value
        wrapper.cache_info = _cache_info
        return wrapper
    return impl

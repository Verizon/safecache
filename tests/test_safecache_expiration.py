# Copyright 2020 Verizon Inc.
# Licensed under the terms of the Apache License 2.0.
# See LICENSE file in project root for terms.

import pytest
import time

from safecache import CacheExpired
from safecache import safecache


def test_bug_expiration_ttl():
    """Bug expiration equality check was reversed and immutable
       object (cache hit) was tried to be modified.

    Reference:  https://github.com/Verizon/safecache/pull/3
    """
    @safecache(ttl=3)  # seconds
    def f(x):
        return [x]

    f(10)
    assert f.cache_info().misses == 1

    f(10)
    assert f.cache_info().misses == 1

    time.sleep(3)
    f(10)  # should be expired
    assert f.cache_info().misses == 2

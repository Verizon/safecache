# Copyright 2020 Verizon Inc.
# Licensed under the terms of the Apache License 2.0.
# See LICENSE file in project root for terms.

"""
safecache
=========
"""

from .exceptions import CacheExpired
from .exceptions import CacheMiss

from .safecache import IMMUTABLE_TYPES
from .safecache import is_immutable
from .safecache import is_mutable
from .safecache import mutabletypeguard
from .safecache import safecache

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution("safecache").version
except ImportError:
    # Set the version to 0.0.0 if the pkg_resources module is not working
    __version__ = '0.0.0'

# Copyright 2020 Verizon Inc.
# Licensed under the terms of the Apache License 2.0.
# See LICENSE file in project root for terms.

"""
safecache.exceptions
====================

This module implements custom exception classes.
"""


class CacheError(Exception):
    """Cache generic error"""


class CacheExpired(CacheError, ValueError):
    """Cache expired from buffer"""


class CacheMiss(CacheError, KeyError):
    """Cache missed from buffer"""

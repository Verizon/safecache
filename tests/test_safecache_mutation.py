# Copyright 2020 Verizon Inc.
# Licensed under the terms of the Apache License 2.0.
# See LICENSE file in project root for terms.

from typing import MutableMapping
from typing import MutableSequence
from typing import MutableSet

import pytest

from safecache import IMMUTABLE_TYPES
from safecache import is_immutable
from safecache import is_mutable
from safecache import mutabletypeguard

"""
tests.safecache_mutation
========================
"""


_SAMPLES_BINARY = (b"", b"10")
_SAMPLES_BOOLEAN = (True, False)
_SAMPLES_DICT = (dict(), {1: 2})
_SAMPLES_FLOAT = (1.0, 0.1, 1e10)
_SAMPLES_LIST = ([], [1])
_SAMPLES_NUMERIC = (0, 1, 10, 1 << 32, 1 << 64)
_SAMPLES_SET = (set(), {1})
_SAMPLES_STRINGS = ("", "1")
_SAMPLES_TUPLE = ((), (1,))


#
# is_immutable, is_mutable
#


def test_IMMUTABLE_TYPES_is_immutable_using_typing():
    for T in IMMUTABLE_TYPES:
        assert not isinstance(T, (MutableMapping, MutableSequence, MutableSet))


def test_IMMUTABLE_TYPES_is_immutable_using_safecache():
    # Note that this test is redundant but needed to guarantee
    # that `is_immutable` and `is_mutable` are deterministic.
    for T in IMMUTABLE_TYPES:
        assert is_immutable(T) and not is_mutable(T)


@pytest.mark.parametrize("value", (
    *_SAMPLES_BINARY,
    *_SAMPLES_BOOLEAN,
    *_SAMPLES_FLOAT,
    *_SAMPLES_NUMERIC,
    *_SAMPLES_STRINGS,
    *_SAMPLES_TUPLE,
))
def test_immutable_type_samples(value):
    assert is_immutable(value)


@pytest.mark.parametrize("value", (
    *_SAMPLES_DICT,
    *_SAMPLES_LIST,
    *_SAMPLES_SET,
))
def test_mutable_type_samples(value):
    assert is_mutable(value)


#
# mutabletypeguard
#


@mutabletypeguard
def f(x):
    return x


@pytest.mark.parametrize("value", (
    *_SAMPLES_BINARY,
    *_SAMPLES_BOOLEAN,
    *_SAMPLES_FLOAT,
    *_SAMPLES_NUMERIC,
    *_SAMPLES_STRINGS,
    *_SAMPLES_TUPLE,
))
def test_mutabletypeguard_immutable_memid_checks(value):
    assert id(value) == f(value)


@pytest.mark.parametrize("value", (
    *_SAMPLES_DICT,
    *_SAMPLES_LIST,
    *_SAMPLES_SET,
))
def test_mutabletypeguard_immutable_memid_checks(value):
    assert id(value) != f(value)

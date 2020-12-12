[![PyPI](https://img.shields.io/badge/package-pypi-blue.svg)](https://pypi.org/project/safecache/)
![GitHub Actions: python-pytest](https://github.com/Verizon/safecache/workflows/python-pytest/badge.svg)

<div align="center">
  <h1>safecache</h1>
  <p><strong>A thread-safe and mutation-safe LRU cache for Python.</strong></p>
</div>

## Features

- Zero third-party dependencies.
- All cached entries are **mutation-safe**.
- All cached entries are **thread-safe**.
- Customizable cache-miss behavior.
- Disk caching (*in development*).

## Installation

```bash
~$ pip install safecache
```

## Usage

**safecache** works just like the [functool's lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache) where you decorate a callable with [optional configurations](#cache-configurations).

```python
from safecache import safecache

@safecache()
def fib(n):
    x, y, z = 0, 0, 1
    while n:
        n -= 1
        x, y = y, z
        z = x + y
    return y
```

Once decorated, the callable will inherit the [functionality](#features) of **safecache** and begin safely caching returned results.

## Cache Configurations

| Parameter | Description | Default |
|:----------|:------------|:--------|
| `maxsize`| maximum cache entry size. | `None` |
| `ttl`| maximum freshness of cache entry (in seconds). | `math.inf` |
| `miss_callback` | custom cache-miss callback function (e.g. [Redis](https://redis.io) client). | `lambda _: _` |

## Cache Statistics

To view cache hit/miss statistics, you would simply call `.cache_info()` on the decorated function.

For example, using a recursive Fibonacci implementation to maximize cache hit/miss:

```python
from safecache import safecache

@safecache()
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

fib(100)
fib.cache_info()  # CacheInfo(hits=98, misses=101, maxsize=128, currsize=101)
```
## Why safecache?

[Caching](https://en.wikipedia.org/wiki/Cache_(computing)) using native Python can be useful to minimize the caching latency (e.g. [dynamic programming problems](https://en.wikipedia.org/wiki/Dynamic_programming#Examples:_Computer_algorithms)), but it could be used or implemented incorrectly to result in inconsistent caching behaviors and bugs. For example, here is a scenario where one needs object integrity - but does not have that guarantee due to cache contamination.

```python
from functools import lru_cache

@lru_cache()
def convert_to_list(x):
    return [x]

converted = convert_to_list(1)  # [1]

# if we mutate the variable:
converted.append(2)  # [1, 2]

# then the referenced, origin cache is also mutated.
# We naturally expect this result to still be [1].
convert_to_list(1)  # [1, 2]

# this is because both `converted` and the function
# object references the same memory address.
assert hex(id(convert_to_list(1))) == hex(id(converted))  # 0x7be3da4ca7c8
```

As you can see, `.append` has contaminated our mutable cache storage inside the [lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache) (which is due to the fundamentals of [Python object referencing](https://docs.python.org/2.0/ref/objects.html)). **safecache** solves this by heuristically identifying which cached object are mutable and guarding them by returning their (deep)copies. As expected, immutable caches are not copied as they do not need to be.

In most cases, [lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache) is a great way to cache expensive results in Python; but if you need stringent thread-safe cache integrity preservation , you will definitely find **safecache** useful.

## License

**safecache** is under [Apache 2.0 license](./LICENSE).

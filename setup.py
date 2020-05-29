# Copyright 2020 Verizon Inc.
# Licensed under the terms of the Apache License 2.0.
# See LICENSE file in project root for terms.

from setuptools import find_packages, setup

import safecache

setup(
    name="safecache",
    description="safecache is a thread-safe and mutation-safe LRU cache for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Verizon/safecache",
    author="Herbert Shin",
    author_email="herbert.shin@verizon.com",
    version=safecache.__version__,
    license="Apache 2.0",
    python_requires=">=3.4",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
)

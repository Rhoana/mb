#!/usr/bin/env python
import os

from setuptools import setup, find_packages

VERSION = 0.1
version = os.path.join('mbeam', '__init__.py')
execfile(version)

README = open('README.md').read()

setup(
    name='mbeam',
    version=VERSION,
    packages=find_packages(),
    package_data={'mbeam': ['web/*.*']},
    author='Daniel Haehn',
    author_email='haehn@seas.harvard.edu',
    url="https://github.com/haehn/mb",
    description="mb",
    long_description=README,
    include_package_data=True,
    install_requires=[
        "argparse>=1.4.0",
        "scandir>=1.1",
        "numpy>=1.9.3",
        "tornado>=4.3",
        "PyYAML>=3.10",
        "lru-dict>=1.1.3",
        "Pympler>=0.4.3",
    ],
    entry_points=dict(console_scripts=['mbeam = mbeam.cli:main']),
    zip_safe=False
)

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
    author='Daniel Haehn',
    author_email='haehn@seas.harvard.edu',
    url="https://github.com/haehn/mb",
    description="mb",
    long_description=README,
    install_requires=[
        "numpy>=1.9.3",
        "tornado>=4.3",
    ],
    entry_points=dict(console_scripts=['mbeam = mbeam.cli:main']),
    zip_safe=False
)

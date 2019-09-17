#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
import os

packages = []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)


# Probably should be changed, __init__.py is no longer required for Python 3
for dirpath, dirnames, filenames in os.walk('sanitycheck'):
    # Ignore dirnames that start with '.'
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)    


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


setup(
    name='sanitycheck',
    version="0.1",
    packages=packages,
    author="Ben Evans",
    author_email="b.evans@yale.edu",
    license="BSD 3-clause",
    entry_points = {
        'console_scripts': [
            'sanitycheck = sanitycheck.__main__:main',
        ]
    },
    url="https://github.com/ycrc/sanitycheck",
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    description='sanitycheck - checking HPC cluster environment for expected configurations.',
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Education :: Testing',
        'Topic :: Software Development :: Testing :: Unit',
    ],
)

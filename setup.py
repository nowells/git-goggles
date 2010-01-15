#!/usr/bin/env python

import sys
from distutils.core import setup
import os

version = '0.1'

setup(
    name='git-goggles',
    version=version,
    description="A series of GIT utilities to streamline working with remote branches and reviewing code. Just install and run 'git goggles'",
    long_description=open('README.rst', 'r').read(),
    author='Nowell Strite',
    author_email='nowell@strite.org',
    url='http://github.com/nowells/git-goggles/',
    packages=['gitgoggles'],
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
    scripts=['bin/git-goggles'],
    )

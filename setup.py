#!/usr/bin/env python

import sys
from distutils.core import setup
import os

version = '0.2.5'

setup(
    name='git-goggles',
    version=version,
    description="A series of GIT utilities to streamline working with remote branches and reviewing code. You can think of git-goggles as 'git branch -a' on steroids. Just install and run 'git goggles'",
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
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Version Control',
        'Topic :: Utilities',
        ],
    scripts=['bin/git-goggles'],
    )

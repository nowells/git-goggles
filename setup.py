import sys
from distutils.core import setup
import os

version = '0.1'

setup(
    name='git-goggles',
    version=version,
    description='',
    long_description="""""",
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

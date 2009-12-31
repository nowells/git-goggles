import os
from setuptools import setup, find_packages

version = '0.1'

setup(
    name='git-utilities',
    version=version,
    description='',
    long_description="""""",
    author='Nowell Strite',
    author_email='nowell@strite.org',
    url='http://github.com/nowells/git-utilities/',
    packages=find_packages(),
    zip_safe=False,
    platforms=["*nix"],
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
    )

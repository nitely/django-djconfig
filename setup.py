#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
from setuptools import setup, find_packages


BASE_DIR = os.path.join(os.path.dirname(__file__))
URL = 'https://github.com/nitely/django-djconfig'
README = "For more info, go to: {}".format(URL)


def get_version(package):
    """Get version without importing the lib"""
    with io.open(os.path.join(BASE_DIR, package, '__init__.py'), encoding='utf-8') as fh:
        return [
            l.split('=', 1)[1].strip().strip("'").strip('"')
            for l in fh.readlines()
            if '__version__' in l][0]


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-djconfig',
    version=get_version('djconfig'),
    description='DjConfig is a Django app for storing dynamic configurations.',
    author='Esteban Castro Borsani',
    author_email='ecastroborsani@gmail.com',
    long_description=README,
    url=URL,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    license='MIT License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

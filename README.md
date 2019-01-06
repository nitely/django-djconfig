# DjConfig

[![Build Status](https://img.shields.io/travis/nitely/django-djconfig.svg?style=flat-square)](https://travis-ci.org/nitely/django-djconfig)
[![Coverage Status](https://img.shields.io/coveralls/nitely/django-djconfig.svg?style=flat-square)](https://coveralls.io/r/nitely/django-djconfig)
[![pypi](https://img.shields.io/pypi/v/django-djconfig.svg?style=flat-square)](https://pypi.python.org/pypi/django-djconfig)
[![licence](https://img.shields.io/pypi/l/django-djconfig.svg?style=flat-square)](https://raw.githubusercontent.com/nitely/django-djconfig/master/LICENSE)

djconfig is a library to define dynamic global settings
that can be set within a regular django form and edited
within django's admin panel, or a custom regular view.

## How it works

Set the config values using a regular form.
Those values are persisted in the database (one per row)
and stored in an in-memory cache for later access.

## Requirements

* Python 2.7, 3.4, 3.5, 3.6 or 3.7
* Django 1.11 LTS, 2.0 or 2.1

## Documentation

[Read The Docs](http://django-djconfig.readthedocs.org)

## License

MIT

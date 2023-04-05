# DjConfig

[![Build Status](https://img.shields.io/github/workflow/status/nitely/django-djconfig/ci.yml?branch=main&style=flat-square)](https://github.com/nitely/django-djconfig/actions?query=workflow%3ACI)
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

## Compatibility

* Python +3.8
* Django 3.2 LTS, 4.2 LTS

## Documentation

[Read The Docs](http://django-djconfig.readthedocs.org)

## License

MIT

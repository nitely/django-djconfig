.. _installation:

Installation
============

Requirements
------------

* Python 2.7, 3.3, 3.4 or 3.5 (recommended)
* Django 1.8 LTS

Pip
---

Latest version can be installed via pip::

    $ pip install django-djconfig

Configuration
-------------

::

    # settings.py

    INSTALLED_APPS = [
        # ...

        'djconfig',
    ]

    MIDDLEWARE_CLASSES = [
        # ...

        'djconfig.middleware.DjConfigMiddleware',
    ]

    TEMPLATES = [
        {
            # ...
            'OPTIONS': {
                'context_processors': [
                    # ...
                    'djconfig.context_processors.config',
                ],
            },
        },
    ]

.. note:: Use **MIDDLEWARE** instead of **MIDDLEWARE_CLASSES** in Django >= 1.10

Afterwards, run::

    $ python manage.py migrate

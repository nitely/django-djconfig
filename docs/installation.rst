.. _installation:

Installation
============

Requirements
------------

* Python 2.7, 3.4, 3.5 or 3.6 (recommended)
* Django 1.8 LTS, 1.9, 1.10, 1.11 LTS or 2.0

Pip
---

::

    pip install django-djconfig

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

    python manage.py migrate

All done.

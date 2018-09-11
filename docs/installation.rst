.. _installation:

Installation
============

Requirements
------------

* Python 2.7, 3.4, 3.5, 3.6 or 3.7
* Django 1.11 LTS, 2.0 or 2.1

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

# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from functools import wraps

from . import conf


def override_djconfig(**new_cache_values):
    """
    Temporarily override config values.

    This is similar to :py:func:`django.test.override_settings`,\
    use it in testing.

    :param \*\*new_cache_values: Keyword arguments,\
    the key should match one in the config,\
    a new one is created otherwise,\
    the value is overridden within\
    the decorated function
    """
    def decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kw):
            old_cache_values = {
                key: getattr(conf.config, key)
                for key in new_cache_values
            }

            conf.config._set_many(new_cache_values)

            try:
                return func(*args, **kw)
            finally:
                conf.config._set_many(old_cache_values)

        return func_wrapper

    return decorator

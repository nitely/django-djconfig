#-*- coding: utf-8 -*-

from __future__ import unicode_literals
from functools import wraps

from . import config


def override_djconfig(**new_cache_values):
    """
    This is similar to Django's @override_settings, use it in testing.
    """
    def decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kw):
            old_cache_values = {key: getattr(config, key) for key in new_cache_values}

            for key, value in new_cache_values.items():
                config._set(key, value)

            try:
                return func(*args, **kw)
            finally:
                for key, value in old_cache_values.items():
                    config._set(key, value)

        return func_wrapper

    return decorator

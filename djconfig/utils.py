# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from functools import wraps


def override_djconfig(**new_cache_values):
    """
    This is similar to Django's @override_settings, use it in testing.
    """
    from . import conf  # avoids circular dependency

    def decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kw):
            old_cache_values = {key: getattr(conf.config, key) for key in new_cache_values}

            conf.config._set_many(new_cache_values)

            try:
                return func(*args, **kw)
            finally:
                conf.config._set_many(old_cache_values)

        return func_wrapper

    return decorator

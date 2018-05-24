# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from functools import wraps
import json

from django.db import models
from django import forms

from . import conf

__all__ = [
    'override_djconfig',
    'serialize']


def override_djconfig(**new_cache_values):
    """
    Temporarily override config values.

    This is similar to :py:func:`django.test.override_settings`,\
    use it in testing.

    :param new_cache_values: Keyword arguments,\
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
                for key in new_cache_values}

            conf.config._set_many(new_cache_values)

            try:
                # todo: make a note about this in the docs:
                #       don't populate the config within migrations

                # This works coz the config table is empty,
                # so even if the middleware gets called,
                # it won't update the config (_updated_at
                # will be None), this is assuming the table
                # is not populated by the user (ie: within
                # a migration), in which case it will load
                # all the default values
                return func(*args, **kw)
            finally:
                conf.config._set_many(old_cache_values)

        return func_wrapper

    return decorator

# todo: add DateField
def serialize(value, field):
    """
    Form values serialization

    :param object value: A value to be serialized\
    for saving it into the database and later\
    loading it into the form as initial value
    """
    assert isinstance(field, forms.Field)
    if isinstance(field, forms.ModelMultipleChoiceField):
        return json.dumps([v.pk for v in value])
    # todo: remove
    if isinstance(value, models.Model):
        return value.pk
    return value

#-*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.cache import get_cache
from django.conf import settings as django_settings

from . import models
from .settings import BACKEND
from .utils import prefixer

_registered_forms = set()


def register(form_class):
    """
    Register config forms

    :param form_class: The form to be registered.
    :type form_class: ConfigForm.
    """
    from . import forms  # avoids circular dependency

    global _registered_forms

    assert issubclass(form_class, forms.ConfigForm), \
        "The form does not inherit from ConfigForm"

    _registered_forms.add(form_class)
    _check_backend()


def load():
    """
    Loads every registered form into the cache.
    If a field name is found in the db, it will load it from there.
    Otherwise, the initial value from the field form is used.
    """
    global _registered_forms

    cache_values = {}
    data = dict(models.Config.objects.all().values_list('key', 'value'))

    for form_class in _registered_forms:
        form = form_class(data=data)
        form.is_valid()

        initial = {prefixer(field_name): field.initial
                   for field_name, field in form.fields.items()}
        cache_values.update(initial)

        cleaned_data = {prefixer(field_name): value
                        for field_name, value in form.cleaned_data.items()
                        if field_name in data}
        cache_values.update(cleaned_data)

    cache_values[prefixer('_updated_at')] = data.get('_updated_at')
    cache = get_cache(BACKEND)
    cache.set_many(cache_values)


def _check_backend():
    if django_settings.CACHES[BACKEND]['BACKEND'].endswith(".LocMemCache") and \
            "djconfig.middleware.DjConfigLocMemMiddleware" not in django_settings.MIDDLEWARE_CLASSES:
        raise ValueError("LocMemCache requires DjConfigLocMemMiddleware "
                         "but it was not found in MIDDLEWARE_CLASSES")

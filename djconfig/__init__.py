#-*- coding: utf-8 -*-

from django.core.cache import get_cache
from django.db import connection
from django.conf import settings as django_settings

from djconfig.forms import ConfigForm
from djconfig.config import config, prefixer
from djconfig.models import Config as ConfigModel
from djconfig.settings import BACKEND, PREFIX

__version__ = "0.1.6"
__all__ = ['config', 'register']

_registered_forms = set()


def register(form_class):
    """
    Register config forms

    :param form_class: The form to be registered.
    :type form_class: ConfigForm.
    """
    global _registered_forms

    assert issubclass(form_class, ConfigForm), \
        "The form does not inherit from ConfigForm"

    _registered_forms.add(form_class)
    _check_backend()
    _load()


def load():
    """
    Loads every registered form into the cache.
    If a field name is found in the db, it will load it from there.
    Otherwise, the initial value from the field form is used.
    """
    global _registered_forms

    cache_values = {}
    data = dict(ConfigModel.objects.all().values_list('key', 'value'))

    for form_class in _registered_forms:
        form = form_class(data=data)
        form.is_valid()

        initial = {prefixer(field_name): field.initial
                   for field_name, field in form.fields.iteritems()}
        cache_values.update(initial)

        cleaned_data = {prefixer(field_name): value
                        for field_name, value in form.cleaned_data.iteritems()
                        if field_name in data}
        cache_values.update(cleaned_data)

    cache_values[prefixer('_updated_at')] = data.get('_updated_at')
    cache = get_cache(BACKEND)
    cache.set_many(cache_values)


def _load():
    """
    Avoids loading if the Config table does not exists.
    ie: when running syncdb for the first time.
    """
    if not ConfigModel._meta.db_table in connection.introspection.table_names():
        return

    load()


def _check_backend():
    if django_settings.CACHES[BACKEND]['BACKEND'].endswith(".LocMemCache") and \
            "djconfig.middleware.DjConfigLocMemMiddleware" not in django_settings.MIDDLEWARE_CLASSES:
        raise ValueError("LocMemCache requires DjConfigLocMemMiddleware "
                         "but it was not found in MIDDLEWARE_CLASSES")
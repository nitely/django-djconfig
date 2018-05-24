# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json

from django.apps import apps
from django import forms
from django.db import models
from django.conf import settings

__all__ = [
    "Config",
    "config",
    "register",
    "register"]


class _ConfigFormBase(forms.Form):
    def save(self):
        raise NotImplementedError()


def _check_backend():
    """
    Check :py:class:`djconfig.middleware.DjConfigMiddleware`\
    is registered into ``settings.MIDDLEWARE_CLASSES``
    """
    # Django 1.10 does not allow
    # both settings to be set
    middleware = set(
        getattr(settings, 'MIDDLEWARE', None) or
        getattr(settings, 'MIDDLEWARE_CLASSES', None) or
        [])

    # Deprecated alias
    if "djconfig.middleware.DjConfigLocMemMiddleware" in middleware:
        return

    if "djconfig.middleware.DjConfigMiddleware" in middleware:
        return

    raise ValueError(
        "djconfig.middleware.DjConfigMiddleware "
        "is required but it was not found in "
        "MIDDLEWARE_CLASSES nor in MIDDLEWARE")

def _deserialize(value, field):
    assert isinstance(field, forms.Field)
    if isinstance(field, forms.ModelMultipleChoiceField):
        return json.loads(value, encoding='utf8')
    return value

def _unlazify(value):
    if isinstance(value, models.QuerySet):
        return list(value)
    return value

class Config(object):
    """
    Contain registry of config forms and\
    cache of key-value matching the forms field-value.

    All methods are private to avoid clashing\
    with the dynamic attributes.

    This should be usually accessed through :py:data:`config`
    """
    def __init__(self):
        self._registry = set()
        self._cache = {}

    def __getattr__(self, key):
        """
        Map cache data to config attributes

        :return: The cache value for the accessed key/attribute
        """
        try:
            return self._cache[key]
        except KeyError:
            raise AttributeError('Attribute "%s" not found in config.' % key)

    def _register(self, form_class, check_middleware=True):
        """
        Register a config form into the registry

        :param object form_class: The form class to register.\
        Must be an instance of :py:class:`djconfig.forms.ConfigForm`
        :param bool check_middleware: Check\
        :py:class:`djconfig.middleware.DjConfigMiddleware`\
        is registered into ``settings.MIDDLEWARE_CLASSES``. Default True
        """
        if not issubclass(form_class, _ConfigFormBase):
            raise ValueError(
                "The form does not inherit from `forms.ConfigForm`")

        self._registry.add(form_class)

        if check_middleware:
            _check_backend()

    def _reload(self):
        """
        Gets every registered form's field value.\
        If a field name is found in the db, it will load it from there.\
        Otherwise, the initial value from the field form is used
        """
        ConfigModel = apps.get_model('djconfig.Config')
        cache = {}
        data = dict(
            ConfigModel.objects
                .all()
                .values_list('key', 'value'))

        # populate cache with initial form values,
        # then with cleaned database values,
        # then with raw database file/image paths
        for form_class in self._registry:
            empty_form = form_class()
            cache.update({
                name: field.initial
                for name, field in empty_form.fields.items()})
            form = form_class(data={
                name: _deserialize(data[name], field)
                for name, field in empty_form.fields.items()
                if name in data and not isinstance(field, forms.FileField)})
            form.is_valid()
            cache.update({
                name: _unlazify(value)
                for name, value in form.cleaned_data.items()
                if name in data})
            # files are special because they don't have an initial value
            # and the POSTED data must contain the file. So, we keep
            # the stored path as is
            # TODO: see if serialize/deserialize/unlazify can be used for this instead
            cache.update({
                name: data[name]
                for name, field in empty_form.fields.items()
                if name in data and isinstance(field, forms.FileField)})

        cache['_updated_at'] = data.get('_updated_at')
        self._cache = cache

    def _reload_maybe(self):
        """
        Reload the config if the config\
        model has been updated. This is called\
        once on every request by the middleware.\
        Should not be called directly.
        """
        ConfigModel = apps.get_model('djconfig.Config')

        data = dict(
            ConfigModel.objects
                .filter(key='_updated_at')
                .values_list('key', 'value'))

        if (not hasattr(self, '_updated_at') or
                self._updated_at != data.get('_updated_at')):
            self._reload()

    # Unit test helpers
    def _reset(self):
        self._registry = set()
        self._cache = {}

    def _set(self, key, value):
        self._cache[key] = value

    def _set_many(self, items):
        self._cache.update({
            key: value
            for key, value in items.items()})


config = Config()

# Public methods
register = config._register
reload_maybe = config._reload_maybe

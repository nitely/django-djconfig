# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import apps


class Config(object):
    """
    Contain registry of config forms and\
    cache of key-value matching the forms field-value.

    All methods must be private to avoid clashing\
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
        * Public

        Register a config form into the registry

        :param object form_class:\
        The form class to register, instance of :py:class:`djconfig.forms.ConfigForm`
        :param bool check_middleware: Check if\
        :py:class:`djconfig.middleware.DjConfigMiddleware`\
        is registered into ``settings.MIDDLEWARE_CLASSES``. Default True
        """
        from . import forms  # avoids circular dependency

        assert issubclass(form_class, forms.ConfigForm), \
            "The form does not inherit from ConfigForm"

        self._registry.add(form_class)

        if check_middleware:
            self._check_backend()

    @staticmethod
    def _check_backend():
        """
        * Private

        Check if :py:class:`djconfig.middleware.DjConfigMiddleware`\
        is registered into ``settings.MIDDLEWARE_CLASSES``
        """
        from django.conf import settings

        middlewares = set(settings.MIDDLEWARE_CLASSES)

        # Deprecated alias
        if "djconfig.middleware.DjConfigLocMemMiddleware" in middlewares:
            return

        if "djconfig.middleware.DjConfigMiddleware" in middlewares:
            return

        raise ValueError(
            "djconfig.middleware.DjConfigMiddleware is required "
            "but it was not found in MIDDLEWARE_CLASSES"
        )

    def _reload(self):
        """
        * Private

        Gets every registered form's field value.\
        If a field name is found in the db, it will load it from there.\
        Otherwise, the initial value from the field form is used
        """
        ConfigModel = apps.get_model('djconfig.Config')
        cache = {}
        data = dict(
            ConfigModel.objects
                .all()
                .values_list('key', 'value')
        )

        for form_class in self._registry:
            form = form_class(data=data)
            form.is_valid()

            initial = {
                field_name: field.initial
                for field_name, field in form.fields.items()
            }
            cache.update(initial)

            cleaned_data = {
                field_name: value
                for field_name, value in form.cleaned_data.items()
                if field_name in data
            }
            cache.update(cleaned_data)

        cache['_updated_at'] = data.get('_updated_at')
        self._cache = cache

    def _reload_maybe(self):
        """
        * Public

        Reload the config if the config\
        model has been updated. This is called\
        once on every request by the middleware.\
        Should not be called directly.
        """
        ConfigModel = apps.get_model('djconfig.Config')

        data = dict(
            ConfigModel.objects
                .filter(key='_updated_at')
                .values_list('key', 'value')
        )

        # Load for the first time
        if not hasattr(self, '_updated_at'):
            self._reload()

        if data.get('_updated_at') != self._updated_at:
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
            for key, value in items.items()
        })


config = Config()

# Public methods
register = config._register
reload_maybe = config._reload_maybe

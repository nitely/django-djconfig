#-*- coding: utf-8 -*-

from django.test import TestCase
from django.core.cache import cache as _cache
from django import forms
from django.core.cache import get_cache
from django.conf import settings

import djconfig
from djconfig.forms import ConfigForm
from djconfig.models import Config
from djconfig.config import Config as ConfigCache
from djconfig.middleware import DjConfigLocMemMiddleware


class FooForm(ConfigForm):

    boolean = forms.BooleanField(initial=True, required=False)
    boolean_false = forms.BooleanField(initial=False, required=False)
    char = forms.CharField(initial="foo")
    email = forms.EmailField(initial="foo@bar.com")
    float_number = forms.FloatField(initial=1.23)
    integer = forms.IntegerField(initial=123)
    url = forms.URLField(initial="foo.com")


class DjConfigTest(TestCase):

    def setUp(self):
        _cache.clear()
        djconfig._registered_forms.clear()

    def test_register(self):
        """
        register forms
        """
        djconfig.register(FooForm)
        self.assertSetEqual(djconfig._registered_forms, {FooForm, })

    def test_register_invalid_form(self):
        """
        register invalid forms
        """
        class BadForm(forms.Form):
            """"""

        self.assertRaises(AssertionError, djconfig.register, BadForm)

    def test_load(self):
        """
        Load initial configuration into the cache
        """
        djconfig.register(FooForm)
        cache = get_cache(djconfig.BACKEND)
        values = cache.get_many(['boolean', 'boolean_false', 'char', 'email',
                                 'float_number', 'integer', 'url'])
        self.assertDictEqual(values, {'boolean': True,
                                      'boolean_false': False,
                                      'char': "foo",
                                      'email': "foo@bar.com",
                                      'float_number': 1.23,
                                      'integer': 123,
                                      'url': "foo.com"})

    def test_load_from_database(self):
        """
        Load configuration into the cache
        """
        data = [Config(key='boolean', value=False),
                Config(key='boolean_false', value=True),
                Config(key='float_number', value=2.1),
                Config(key='char', value="foo2"),
                Config(key='email', value="foo2@bar.com"),
                Config(key='integer', value=321),
                Config(key='url', value="foo2.com")]
        Config.objects.bulk_create(data)

        djconfig.register(FooForm)
        cache = get_cache(djconfig.BACKEND)

        values = cache.get_many(['boolean', 'boolean_false', 'float_number',
                                 'char', 'email', 'integer', 'url'])
        self.assertDictEqual(values, {'boolean': False,
                                      'boolean_false': True,
                                      'float_number': 2.1,
                                      'char': "foo2",
                                      'email': "foo2@bar.com",
                                      'integer': 321,
                                      'url': "http://foo2.com/"})

        # use initial if the field is not found in the db
        Config.objects.get(key='char').delete()
        djconfig.load()
        self.assertEqual(cache.get('char'), "foo")

    def test_load_unicode(self):
        """
        Load configuration into the cache
        """
        Config.objects.create(key='char', value=u"áéíóú")
        djconfig.register(FooForm)
        cache = get_cache(djconfig.BACKEND)
        self.assertEqual(cache.get('char'), u"áéíóú")

    def test_load_from_database_invalid(self):
        """
        Load initial if the db value is invalid
        """
        Config.objects.create(key='integer', value="string")
        djconfig.register(FooForm)
        cache = get_cache(djconfig.BACKEND)
        self.assertEqual(cache.get('integer'), 123)


class BarForm(ConfigForm):

    char = forms.CharField(initial="foo")


class DjConfigFormsTest(TestCase):

    def setUp(self):
        _cache.clear()
        djconfig._registered_forms.clear()

    def test_config_form(self):
        """
        config form
        """
        form = BarForm(data={"char": "foo2", })
        self.assertTrue(form.is_valid())
        form.save()
        config = Config.objects.get(key="char")
        self.assertEqual(config.value, "foo2")

    def test_config_form_update(self):
        """
        config form
        """
        Config.objects.create(key="char", value="bar")

        form = BarForm(data={"char": "foo2", })
        self.assertTrue(form.is_valid())
        form.save()
        config = Config.objects.get(key="char")
        self.assertEqual(config.value, "foo2")

    def test_config_form_cache_update(self):
        """
        config form, update cache on form save
        """
        djconfig.register(BarForm)

        form = BarForm(data={"char": "foo2", })
        self.assertTrue(form.is_valid())
        form.save()

        cache = get_cache(djconfig.BACKEND)
        self.assertEqual(cache.get("char"), "foo2")


class DjConfigConfTest(TestCase):

    def setUp(self):
        _cache.clear()
        djconfig._registered_forms.clear()

    def test_config(self):
        """
        config wrapper
        """
        cache = get_cache(djconfig.BACKEND)
        cache.set("key", "value")
        config = ConfigCache()
        self.assertEqual(config.key, "value")


class DjConfigMiddlewareTest(TestCase):

    def setUp(self):
        _cache.clear()
        djconfig._registered_forms.clear()

    def test_config_middleware_process_request(self):
        """
        config middleware, reload cache
        """
        djconfig.register(BarForm)
        cache = get_cache(djconfig.BACKEND)
        self.assertEqual(cache.get('char'), None)

        middleware = DjConfigLocMemMiddleware()
        middleware.process_request(request=None)
        self.assertEqual(cache.get('char'), "foo")
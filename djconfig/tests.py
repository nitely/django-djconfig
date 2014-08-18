#-*- coding: utf-8 -*-

import datetime

from django.test import TestCase
from django.core.cache import cache as _cache
from django import forms
from django.core.cache import get_cache
from django.conf import settings

import djconfig
from djconfig import prefixer
from djconfig.forms import ConfigForm
from djconfig.models import Config as ConfigModel
from djconfig.config import Config as ConfigCache
from djconfig.middleware import DjConfigLocMemMiddleware
from djconfig import forms as djconfig_forms


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

        self.cache = get_cache(djconfig.BACKEND)

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
        keys = ['boolean', 'boolean_false', 'char', 'email', 'float_number', 'integer', 'url']
        values = self.cache.get_many([prefixer(k) for k in keys])
        self.assertDictEqual(values, {prefixer('boolean'): True,
                                      prefixer('boolean_false'): False,
                                      prefixer('char'): "foo",
                                      prefixer('email'): "foo@bar.com",
                                      prefixer('float_number'): 1.23,
                                      prefixer('integer'): 123,
                                      prefixer('url'): "foo.com"})

    def test_load_from_database(self):
        """
        Load configuration into the cache
        """
        data = [ConfigModel(key='boolean', value=False),
                ConfigModel(key='boolean_false', value=True),
                ConfigModel(key='float_number', value=2.1),
                ConfigModel(key='char', value="foo2"),
                ConfigModel(key='email', value="foo2@bar.com"),
                ConfigModel(key='integer', value=321),
                ConfigModel(key='url', value="foo2.com")]
        ConfigModel.objects.bulk_create(data)

        djconfig.register(FooForm)

        keys = ['boolean', 'boolean_false', 'char', 'email', 'float_number', 'integer', 'url']
        values = self.cache.get_many([prefixer(k) for k in keys])
        self.assertDictEqual(values, {prefixer('boolean'): False,
                                      prefixer('boolean_false'): True,
                                      prefixer('float_number'): 2.1,
                                      prefixer('char'): "foo2",
                                      prefixer('email'): "foo2@bar.com",
                                      prefixer('integer'): 321,
                                      prefixer('url'): "http://foo2.com/"})

        # use initial if the field is not found in the db
        ConfigModel.objects.get(key='char').delete()
        djconfig.load()
        self.assertEqual(self.cache.get(prefixer('char')), "foo")

    def test_load_unicode(self):
        """
        Load configuration into the cache
        """
        ConfigModel.objects.create(key='char', value=u"áéíóú")
        djconfig.register(FooForm)
        self.assertEqual(self.cache.get(prefixer('char')), u"áéíóú")

    def test_load_from_database_invalid(self):
        """
        Load initial if the db value is invalid
        """
        ConfigModel.objects.create(key='integer', value="string")
        djconfig.register(FooForm)
        self.assertEqual(self.cache.get(prefixer('integer')), 123)

    def test_load_updated_at(self):
        """
        Load updated_at
        """
        djconfig.register(FooForm)
        value = self.cache.get(prefixer("_updated_at"))
        self.assertIsNone(value)

        ConfigModel.objects.create(key="_updated_at", value="string")
        djconfig.load()
        value = self.cache.get(prefixer("_updated_at"))
        self.assertEqual(value, "string")


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
        config = ConfigModel.objects.get(key="char")
        self.assertEqual(config.value, "foo2")

    def test_config_form_update(self):
        """
        config form
        """
        ConfigModel.objects.create(key="char", value="bar")

        form = BarForm(data={"char": "foo2", })
        self.assertTrue(form.is_valid())
        form.save()
        config = ConfigModel.objects.get(key="char")
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
        self.assertEqual(cache.get(prefixer('char')), "foo2")

    def test_config_form_updated_at(self):
        """
        updated_at should get update on every save() call
        """
        now = djconfig_forms.timezone.now()

        class TZMock:
            @classmethod
            def now(self):
                return now

        orig_djconfig_forms_timezone, djconfig_forms.timezone = djconfig_forms.timezone, TZMock
        try:
            form = BarForm(data={"char": "foo2", })
            self.assertTrue(form.is_valid())
            form.save()
            updated_at_a = ConfigModel.objects.get(key="_updated_at").value

            now += datetime.timedelta(seconds=1)

            form = BarForm(data={"char": "foo2", })
            self.assertTrue(form.is_valid())
            form.save()
            updated_at_b = ConfigModel.objects.get(key="_updated_at").value

            self.assertNotEqual(updated_at_a, updated_at_b)
        finally:
            djconfig_forms.timezone = orig_djconfig_forms_timezone


class DjConfigConfTest(TestCase):

    def setUp(self):
        _cache.clear()
        djconfig._registered_forms.clear()

    def test_config(self):
        """
        config wrapper
        """
        cache = get_cache(djconfig.BACKEND)
        cache.set(prefixer("key"), "value")
        config = ConfigCache()
        self.assertEqual(config.key, "value")


TEST_CACHES = {
    'good': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'bad': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


class DjConfigMiddlewareTest(TestCase):

    def setUp(self):
        _cache.clear()
        djconfig._registered_forms.clear()

    def test_config_middleware_process_request(self):
        """
        config middleware, reload cache
        """
        ConfigModel.objects.create(key="char", value="foo")
        djconfig.register(BarForm)
        cache = get_cache(djconfig.BACKEND)

        cache.set(prefixer('char'), None)
        self.assertIsNone(cache.get(prefixer('char')))

        # Should not reload since _updated_at does not exists (form was not saved)
        middleware = DjConfigLocMemMiddleware()
        middleware.process_request(request=None)
        self.assertIsNone(cache.get(prefixer('char')))

        # Changing _updated_at should make it reload
        ConfigModel.objects.create(key="_updated_at", value="111")
        middleware.process_request(request=None)
        self.assertEqual(cache.get(prefixer('char')), "foo")
        self.assertEqual(cache.get(prefixer("_updated_at")), "111")

        # It does not update again, since _updated_at has not changed
        ConfigModel.objects.filter(key="char").update(value="bar")
        middleware.process_request(request=None)
        self.assertNotEqual(cache.get(prefixer('char')), "bar")
        self.assertEqual(cache.get(prefixer("_updated_at")), "111")

        # Changing _updated_at should make it reload
        ConfigModel.objects.filter(key="_updated_at").update(value="222")
        middleware.process_request(request=None)
        self.assertEqual(cache.get(prefixer('char')), "bar")
        self.assertEqual(cache.get(prefixer("_updated_at")), "222")

    def test_config_middleware_check_backend(self):
        """
        only LocMemCache should be allowed
        """
        org_cache, org_djbackend = settings.CACHES, djconfig.BACKEND
        try:
            settings.CACHES = TEST_CACHES

            djconfig.BACKEND = 'good'
            middleware = DjConfigLocMemMiddleware()
            self.assertIsNone(middleware.check_backend())

            djconfig.BACKEND = 'bad'
            self.assertRaises(ValueError, middleware.check_backend)
        finally:
            settings.CACHES, djconfig.BACKEND = org_cache, org_djbackend
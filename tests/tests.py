# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime

from django.test import TestCase, override_settings
from django import forms
from django.conf import settings

from djconfig import registry
from djconfig import forms as djconfig_forms
from djconfig.utils import override_djconfig
from djconfig.conf import Config, config
from djconfig.forms import ConfigForm
from djconfig.models import Config as ConfigModel
from djconfig.middleware import DjConfigMiddleware, DjConfigLocMemMiddleware


class FooForm(ConfigForm):

    boolean = forms.BooleanField(initial=True, required=False)
    boolean_false = forms.BooleanField(initial=False, required=False)
    char = forms.CharField(initial="foo")
    email = forms.EmailField(initial="foo@bar.com")
    float_number = forms.FloatField(initial=1.23)
    integer = forms.IntegerField(initial=123)
    url = forms.URLField(initial="foo.com/")


class DjConfigTest(TestCase):

    def setUp(self):
        config._reset()
        registry._registered_forms.clear()

    def test_register(self):
        """
        register forms
        """
        registry.register(FooForm)
        self.assertSetEqual(registry._registered_forms, {FooForm, })

    def test_register_invalid_form(self):
        """
        register invalid forms
        """
        class BadForm(forms.Form):
            """"""

        self.assertRaises(AssertionError, registry.register, BadForm)


    @override_settings(MIDDLEWARE_CLASSES=settings.MIDDLEWARE_CLASSES[:-1])
    def test_register_check_backend(self):
        """
        Raises valueError if middleware is missing
        """
        self.assertRaises(ValueError, registry.register, FooForm)


class BarForm(ConfigForm):

    char = forms.CharField(initial="foo")


class DjConfigFormsTest(TestCase):

    def setUp(self):
        config._reset()
        registry._registered_forms.clear()

    def test_config_form_populate_if_loaded(self):
        """
        config form, populate initial data only if the config is loaded
        """
        registry.register(BarForm)
        config._set("char", "foo2")

        form = BarForm()
        self.assertTrue('char' not in form.initial)

        config._is_loaded = True
        form = BarForm()
        self.assertEqual(form.initial['char'], 'foo2')

    def test_config_form_allow_initial_overwrite(self):
        """
        config form, allow user to pass initial data
        """
        registry.register(BarForm)
        config._set("char", "foo2")
        config._is_loaded = True

        form = BarForm(initial={'char': 'bar', })
        self.assertEqual(form.initial['char'], 'bar')

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
        registry.register(BarForm)

        form = BarForm(data={"char": "foo2", })
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(config.char, "foo2")

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
        config._reset()
        registry._registered_forms.clear()

    def test_config_attr_error(self):
        """
        config attribute error when it's not in keys
        """
        config = Config()

        def wrapper():
            return config.foo

        self.assertRaises(AttributeError, wrapper)

        config._set('foo', 'bar')
        self.assertEqual(wrapper(), 'bar')

    def test_config_set(self):
        """
        config set adds the item
        """
        config._set('foo', 'bar')
        self.assertTrue('foo' in config._cache)
        self.assertEqual(config.foo, 'bar')

    def test_config_set_many(self):
        """
        config set adds the key
        """
        config._set_many({'foo': 'bar', })
        self.assertTrue('foo' in config._cache)
        self.assertEqual(config.foo, 'bar')

    def test_config_load(self):
        """
        Load initial configuration into the cache
        """
        registry.register(FooForm)
        keys = ['boolean', 'boolean_false', 'char', 'email', 'float_number', 'integer', 'url']
        values = {k: getattr(config, k) for k in keys}
        self.assertDictEqual(values, {'boolean': True,
                                      'boolean_false': False,
                                      'char': "foo",
                                      'email': "foo@bar.com",
                                      'float_number': 1.23,
                                      'integer': 123,
                                      'url': "foo.com/"})

    def test_config_load_from_database(self):
        """
        Load configuration into the cache
        """
        data = [ConfigModel(key='boolean', value=False),
                ConfigModel(key='boolean_false', value=True),
                ConfigModel(key='float_number', value=2.1),
                ConfigModel(key='char', value="foo2"),
                ConfigModel(key='email', value="foo2@bar.com"),
                ConfigModel(key='integer', value=321),
                ConfigModel(key='url', value="foo2.com/")]
        ConfigModel.objects.bulk_create(data)

        registry.register(FooForm)

        keys = ['boolean', 'boolean_false', 'char', 'email', 'float_number', 'integer', 'url']
        values = {k: getattr(config, k) for k in keys}
        self.assertDictEqual(values, {'boolean': False,
                                      'boolean_false': True,
                                      'float_number': 2.1,
                                      'char': "foo2",
                                      'email': "foo2@bar.com",
                                      'integer': 321,
                                      'url': "http://foo2.com/"})

        # use initial if the field is not found in the db
        ConfigModel.objects.get(key='char').delete()
        config._reset()
        config._lazy_load()
        self.assertEqual(config.char, "foo")

    def test_config_load_unicode(self):
        """
        Load configuration into the cache
        """
        ConfigModel.objects.create(key='char', value=u"áéíóú")
        registry.register(FooForm)
        self.assertEqual(config.char, u"áéíóú")

    def test_config_load_from_database_invalid(self):
        """
        Load initial if the db value is invalid
        """
        ConfigModel.objects.create(key='integer', value="string")
        registry.register(FooForm)
        self.assertEqual(config.integer, 123)

    def test_config_load_updated_at(self):
        """
        Load updated_at
        """
        registry.register(FooForm)
        self.assertIsNone(config._updated_at)

        ConfigModel.objects.create(key="_updated_at", value="string")
        config._reset()
        self.assertEqual(config._updated_at, "string")

    def test_config_lazy_load(self):
        """
        Load the config the first time you access an attribute
        """
        self.assertRaises(AttributeError, lambda: config.char)
        registry.register(FooForm)
        self.assertRaises(AttributeError, lambda: config.char)
        config._reset()
        self.assertEqual(config.char, "foo")

    def test_config_lazy_load_race_condition(self):
        """
        It sets is_loaded *after* the reload.
        """
        class ConfigMock(Config):
            def _reload(self):
                raise ValueError

        config = ConfigMock()
        self.assertFalse(config._is_loaded)
        self.assertRaises(ValueError, config._lazy_load)
        self.assertFalse(config._is_loaded)

    def test_config_lazy_load_once(self):
        """
        Reload is not called if already loaded
        """
        class ConfigMock(Config):
            def _reload(self):
                raise ValueError

        config = ConfigMock()
        config._is_loaded = True
        self.assertIsNone(config._lazy_load())

    def test_config_lazy_load_ok(self):
        """
        It sets is_loaded *after* the reload.
        """
        self.assertFalse(config._is_loaded)
        config._lazy_load()
        self.assertTrue(config._is_loaded)

    def test_config_reload_in_keys(self):
        """
        Load the config the first time you access an attribute
        """
        registry.register(FooForm)
        self.assertTrue('char' in config._cache)
        self.assertEqual(config.char, "foo")

    def test_config_reset(self):
        """
        Reset turn is_loaded to False
        """
        config._is_loaded = True
        config._reset()
        self.assertFalse(config._is_loaded)


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
        config._reset()
        registry._registered_forms.clear()

    def test_config_middleware_process_request(self):
        """
        config middleware, reload cache
        """
        ConfigModel.objects.create(key="char", value="foo")
        registry.register(BarForm)
        config._lazy_load()
        config._set('char', None)
        cache = config._cache

        # Should not reload since _updated_at does not exists (form was not saved)
        middleware = DjConfigMiddleware()
        middleware.process_request(request=None)
        self.assertIsNone(cache.get('char'))

        # Changing _updated_at should make it reload
        ConfigModel.objects.create(key="_updated_at", value="111")
        middleware.process_request(request=None)
        self.assertEqual(cache.get('char'), "foo")
        self.assertEqual(cache.get("_updated_at"), "111")

        # It does not update again, since _updated_at has not changed
        ConfigModel.objects.filter(key="char").update(value="bar")
        middleware.process_request(request=None)
        self.assertNotEqual(cache.get('char'), "bar")
        self.assertEqual(cache.get("_updated_at"), "111")

        # Changing _updated_at should make it reload
        ConfigModel.objects.filter(key="_updated_at").update(value="222")
        middleware.process_request(request=None)
        self.assertEqual(cache.get('char'), "bar")
        self.assertEqual(cache.get("_updated_at"), "222")

    def test_config_middleware_old(self):
        """
        Regression test for the old LocMem Middleware
        """
        self.assertEqual(DjConfigLocMemMiddleware, DjConfigMiddleware)


class DjConfigUtilsTest(TestCase):

    def setUp(self):
        config._reset()
        registry._registered_forms.clear()

    def test_override_djconfig(self):
        """
        Sets config variables temporarily
        """
        @override_djconfig(foo='bar', foo2='bar2')
        def my_test(my_var):
            return my_var, config.foo, config.foo2

        config._set('foo', 'org')
        config._set('foo2', 'org2')

        res = my_test("stuff")
        self.assertEqual(res, ("stuff", 'bar', 'bar2'))
        self.assertEqual((config.foo, config.foo2), ("org", 'org2'))

    def test_override_djconfig_except(self):
        """
        Sets config variables temporarily, even on exceptions
        """
        @override_djconfig(foo='bar')
        def my_test():
            raise AssertionError

        config._set('foo', 'org')

        try:
            my_test()
        except AssertionError:
            pass

        self.assertEqual(config.foo, "org")

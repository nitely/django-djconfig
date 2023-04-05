# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime
from unittest import skipIf

from django.test import TestCase, override_settings
from django import forms
from django.conf import settings
from django import get_version
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.contrib.auth import get_user_model

import djconfig
from djconfig import forms as djconfig_forms
from djconfig.utils import override_djconfig
from djconfig.conf import Config, config
from djconfig.forms import ConfigForm
from djconfig.models import Config as ConfigModel
from djconfig.middleware import DjConfigMiddleware, DjConfigLocMemMiddleware
from djconfig import utils
from .models import ChoiceModel


def make_dummy_image():
    return SimpleUploadedFile(
        'image.gif',
        (b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
         b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'),
        content_type='image/gif')


class FooForm(ConfigForm):

    boolean = forms.BooleanField(initial=True, required=False)
    boolean_false = forms.BooleanField(initial=False, required=False)
    char = forms.CharField(initial="foo")
    email = forms.EmailField(initial="foo@bar.com")
    float_number = forms.FloatField(initial=1.23)
    integer = forms.IntegerField(initial=123)
    url = forms.URLField(initial="foo.com/")
    choices = forms.ChoiceField(initial=None, choices=[('1', 'label_a'), ('2', 'label_b')])
    model_choices = forms.ModelChoiceField(initial=None, queryset=ChoiceModel.objects.all())
    model_m_choices = forms.ModelMultipleChoiceField(initial=None, queryset=ChoiceModel.objects.all())
    image = forms.ImageField(initial=None, required=False)
    file = forms.FileField(initial=None, required=False)


class DjConfigTest(TestCase):

    def setUp(self):
        config._reset()

    def test_register(self):
        """
        register forms
        """
        djconfig.register(FooForm)
        self.assertSetEqual(config._registry, {FooForm, })

    def test_register_invalid_form(self):
        """
        register invalid forms
        """
        class BadForm(forms.Form):
            """"""

        self.assertRaises(ValueError, djconfig.register, BadForm)

    def test_config_check_backend_new_middleware(self):
        """
        Should try both MIDDLEWARE and MIDDLEWARE_CLASS
        """
        mids = settings.MIDDLEWARE_CLASSES

        with override_settings(MIDDLEWARE_CLASSES=mids[:-1], MIDDLEWARE=[]):
            self.assertRaises(ValueError, djconfig.register, FooForm)

        with override_settings(MIDDLEWARE_CLASSES=[], MIDDLEWARE=mids[:-1]):
            self.assertRaises(ValueError, djconfig.register, FooForm)

        with override_settings(MIDDLEWARE_CLASSES=mids, MIDDLEWARE=[]):
            self.assertIsNone(djconfig.register(FooForm))

        with override_settings(MIDDLEWARE_CLASSES=[], MIDDLEWARE=mids):
            self.assertIsNone(djconfig.register(FooForm))


class BarForm(ConfigForm):

    char = forms.CharField(initial="foo")


class ModelChoiceForm(ConfigForm):

    model_choice = forms.ModelChoiceField(initial=None, queryset=ChoiceModel.objects.all())


class ModelChoicePKForm(ConfigForm):

    model_choice = forms.ModelChoiceField(initial=None, queryset=ChoiceModel.objects.all())

    def clean_model_choice(self):
        return self.cleaned_data['model_choice'].pk


class ModelMultipleChoiceForm(ConfigForm):

    model_choices = forms.ModelMultipleChoiceField(initial=None, queryset=ChoiceModel.objects.all())


class ImageForm(ConfigForm):

    image = forms.ImageField(initial=None, required=False)

    def save_image(self):
        image = self.cleaned_data.get('image')
        if image:
            image.name = 'foo_saved.gif'


class FileForm(ConfigForm):

    file = forms.FileField(initial=None, required=False)


class DjConfigFormsTest(TestCase):

    def setUp(self):
        config._reset()

    def test_config_form_initial(self):
        """
        config form, populate initial data
        """
        djconfig.register(BarForm)
        djconfig.reload_maybe()
        form = BarForm()
        self.assertEqual(form.initial['char'], 'foo')

    def test_config_form_auto_populate(self):
        """
        config form, populate initial data,
        load the config if it's not loaded
        """
        ConfigModel.objects.create(key="char", value="foo2")
        djconfig.register(BarForm)
        djconfig.reload_maybe()

        form = BarForm()
        self.assertEqual(form.initial['char'], 'foo2')

    def test_config_form_allow_initial_overwrite(self):
        """
        config form, allow user to pass initial data
        """
        djconfig.register(BarForm)
        djconfig.reload_maybe()
        config._set("char", "foo2")

        form = BarForm(initial={'char': 'bar', 'email': 'new_initial@mail.com'})
        self.assertEqual(form.initial['char'], 'foo2')
        self.assertEqual(form.initial['email'], 'new_initial@mail.com')

    def test_config_form(self):
        """
        config form
        """
        djconfig.register(BarForm)
        form = BarForm(data={"char": "foo2", })
        self.assertTrue(form.is_valid())
        form.save()

        qs = ConfigModel.objects.get(key="char")
        self.assertEqual(qs.value, "foo2")

    def test_config_save_unregistered_form(self):
        """
        Should raise an exception if form is not registered
        """
        form = BarForm(data={"char": "foo2", })
        self.assertTrue(form.is_valid())
        self.assertRaises(AssertionError, form.save)

    def test_config_form_model_choice(self):
        """
        Saves ModelChoiceField
        """
        model_choice = ChoiceModel.objects.create(name='foo')

        djconfig.register(ModelChoiceForm)
        form = ModelChoiceForm(data={"model_choice": str(model_choice.pk), })
        self.assertTrue(form.is_valid())
        form.save()

        qs = ConfigModel.objects.get(key="model_choice")
        self.assertEqual(qs.value, str(model_choice.pk))

    def test_config_form_model_choice_pk(self):
        """
        Saves ModelChoiceField
        """
        djconfig.register(ModelChoicePKForm)
        model_choice = ChoiceModel.objects.create(name='foo')
        form = ModelChoicePKForm(data={"model_choice": str(model_choice.pk), })
        self.assertTrue(form.is_valid())
        form.save()

        qs = ConfigModel.objects.get(key="model_choice")
        self.assertEqual(qs.value, str(model_choice.pk))

    def test_config_form_model_multi_choice(self):
        """
        Saves ModelMultipleChoiceField
        """
        djconfig.register(ModelMultipleChoiceForm)
        model_choice_a = ChoiceModel.objects.create(name='foo')
        model_choice_b = ChoiceModel.objects.create(name='bar')
        form = ModelMultipleChoiceForm(data={
            "model_choices": [
                str(model_choice_a.pk),
                str(model_choice_b.pk)]})
        self.assertTrue(form.is_valid())
        form.save()

        qs = ConfigModel.objects.get(key="model_choices")
        self.assertEqual(qs.value, '[1, 2]')
        self.assertEqual(list(config.model_choices), [model_choice_a, model_choice_b])

    def test_config_form_update(self):
        """
        Should update the form with the supplied data when saving
        """
        ConfigModel.objects.create(key="char", value="bar")

        djconfig.register(BarForm)
        form = BarForm(data={"char": "foo2", })
        self.assertTrue(form.is_valid())
        form.save()

        qs = ConfigModel.objects.get(key="char")
        self.assertEqual(qs.value, "foo2")

    def test_config_form_cache_update(self):
        """
        config form, update cache on form save
        """
        djconfig.register(BarForm)

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
            def now(cls):
                return now

        orig_djconfig_forms_timezone, djconfig_forms.timezone = djconfig_forms.timezone, TZMock
        try:
            djconfig.register(BarForm)
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

    def test_image_form_conf(self):
        """
        Should save the image path
        """
        djconfig.register(ImageForm)
        djconfig.reload_maybe()
        self.assertFalse(ConfigModel.objects.filter(key="image").exists())
        form = ImageForm(files={'image': make_dummy_image()})
        self.assertTrue(form.is_valid())
        form.save()
        qs = ConfigModel.objects.get(key="image")
        self.assertEqual(qs.value, "image.gif")
        form = ImageForm(files={'image': None})
        self.assertTrue(form.is_valid())
        qs = ConfigModel.objects.get(key="image")
        self.assertEqual(qs.value, "image.gif")

    def test_image_save_form_conf(self):
        """
        Should save the path after storing the image
        """
        djconfig.register(ImageForm)
        djconfig.reload_maybe()
        self.assertFalse(ConfigModel.objects.filter(key="image").exists())
        form = ImageForm(files={'image': make_dummy_image()})
        self.assertTrue(form.is_valid())
        form.save_image()
        form.save()
        qs = ConfigModel.objects.get(key="image")
        self.assertEqual(qs.value, "foo_saved.gif")

    def test_file_form_conf(self):
        """
        Should save the file path
        """
        djconfig.register(FileForm)
        djconfig.reload_maybe()
        self.assertFalse(ConfigModel.objects.filter(key="file").exists())
        form = FileForm(files={'file': make_dummy_image()})
        self.assertTrue(form.is_valid())
        form.save()
        qs = ConfigModel.objects.get(key="file")
        self.assertEqual(qs.value, "image.gif")
        form = FileForm(files={'file': None})
        self.assertTrue(form.is_valid())
        qs = ConfigModel.objects.get(key="file")
        self.assertEqual(qs.value, "image.gif")


class DjConfigConfTest(TestCase):

    def setUp(self):
        config._reset()

    def test_config_attr_error(self):
        """
        config attribute error when it's not in keys
        """
        config_ = Config()
        self.assertRaises(AttributeError, lambda: config_.foo)
        config_._set('foo', 'bar')
        self.assertEqual(config_.foo, 'bar')

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
        djconfig.register(FooForm)
        djconfig.reload_maybe()
        keys = ['boolean', 'boolean_false', 'char', 'email', 'float_number',
                'integer', 'url', 'choices', 'model_choices', 'model_m_choices',
                'image', 'file']
        values = {k: getattr(config, k) for k in keys}
        self.assertDictEqual(
            values,
            {
                'boolean': True,
                'boolean_false': False,
                'char': "foo",
                'email': "foo@bar.com",
                'float_number': 1.23,
                'integer': 123,
                'url': "foo.com/",
                'choices': None,
                'model_choices': None,
                'model_m_choices': None,
                'image': None,
                'file': None
            }
        )

    def test_config_load_from_database(self):
        """
        Load configuration into the cache
        """
        model_choice = ChoiceModel.objects.create(name='A')
        model_choice_b = ChoiceModel.objects.create(name='B')
        data = [
            ConfigModel(key='boolean', value=False),
            ConfigModel(key='boolean_false', value=True),
            ConfigModel(key='float_number', value=2.1),
            ConfigModel(key='char', value="foo2"),
            ConfigModel(key='email', value="foo2@bar.com"),
            ConfigModel(key='integer', value=321),
            ConfigModel(key='url', value="foo2.com/"),
            ConfigModel(key='choices', value='1'),
            ConfigModel(key='model_choices', value=model_choice.pk),
            ConfigModel(key='model_m_choices', value=utils.serialize(
                ChoiceModel.objects.filter(pk=model_choice_b.pk),
                forms.ModelMultipleChoiceField(None))),
            ConfigModel(key='image', value='path/image.gif'),
            ConfigModel(key='file', value='path/file.zip')
        ]
        ConfigModel.objects.bulk_create(data)

        djconfig.register(FooForm)
        djconfig.reload_maybe()
        keys = ['boolean', 'boolean_false', 'char', 'email', 'float_number',
                'integer', 'url', 'choices', 'model_choices', 'model_m_choices',
                'image', 'file']
        values = {k: getattr(config, k) for k in keys}
        self.assertDictEqual(
            values,
            {
                'boolean': False,
                'boolean_false': True,
                'float_number': 2.1,
                'char': "foo2",
                'email': "foo2@bar.com",
                'integer': 321,
                'url': "http://foo2.com/",
                'choices': '1',
                'model_choices': model_choice,
                'model_m_choices': [model_choice_b],
                'image': 'path/image.gif',
                'file': 'path/file.zip'
            }
        )

        # use initial if the field is not found in the db
        ConfigModel.objects.get(key='char').delete()
        config._reset()
        djconfig.register(FooForm)
        djconfig.reload_maybe()
        self.assertEqual(config.char, "foo")

    def test_config_load_unicode(self):
        """
        Load configuration into the cache
        """
        ConfigModel.objects.create(key='char', value=u"áéíóú")
        djconfig.register(FooForm)
        djconfig.reload_maybe()
        self.assertEqual(config.char, u"áéíóú")

    def test_config_load_from_database_invalid(self):
        """
        Load initial if the db value is invalid
        """
        ConfigModel.objects.create(key='integer', value="string")
        djconfig.register(FooForm)
        djconfig.reload_maybe()
        self.assertEqual(config.integer, 123)

    def test_config_load_updated_at(self):
        """
        Load updated_at
        """
        djconfig.register(FooForm)
        djconfig.reload_maybe()
        self.assertIsNone(config._updated_at)

        ConfigModel.objects.create(key="_updated_at", value="string")
        config._reset()

        djconfig.register(FooForm)
        djconfig.reload_maybe()
        self.assertEqual(config._updated_at, "string")

    def test_config_reload_maybe(self):
        """
        Reload if not loaded
        """
        self.assertRaises(AttributeError, lambda: config.char)
        djconfig.register(FooForm)
        self.assertRaises(AttributeError, lambda: config.char)
        djconfig.reload_maybe()
        self.assertEqual(config.char, "foo")


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

    def test_config_middleware_process_request(self):
        """
        config middleware, reload cache
        """
        ConfigModel.objects.create(key="char", value="foo")
        djconfig.register(BarForm)
        djconfig.reload_maybe()
        config._set('char', None)

        # Should not reload since _updated_at does not exists (form was not saved)
        middleware = DjConfigMiddleware(get_response=lambda req: None)
        middleware.process_request(request=None)
        self.assertIsNone(config._cache.get('char'))

        # Changing _updated_at should make it reload
        ConfigModel.objects.create(key="_updated_at", value="111")
        middleware.process_request(request=None)
        self.assertEqual(config._cache.get('char'), "foo")
        self.assertEqual(config._cache.get("_updated_at"), "111")

        # It does not update again, since _updated_at has not changed
        ConfigModel.objects.filter(key="char").update(value="bar")
        middleware.process_request(request=None)
        self.assertNotEqual(config._cache.get('char'), "bar")
        self.assertEqual(config._cache.get("_updated_at"), "111")

        # Changing _updated_at should make it reload
        ConfigModel.objects.filter(key="_updated_at").update(value="222")
        middleware.process_request(request=None)
        self.assertEqual(config._cache.get('char'), "bar")
        self.assertEqual(config._cache.get("_updated_at"), "222")

    def test_config_middleware_old(self):
        """
        Regression test for the old LocMem Middleware
        """
        self.assertEqual(DjConfigLocMemMiddleware, DjConfigMiddleware)

    @skipIf(get_version().startswith(('1.8.', '1.9.')), 'Django>=1.10 is required')
    def test_config_middleware_new_style(self):
        """
        Should behave like a middleware factory
        """
        def request_handler(req):
            return req

        mid = DjConfigMiddleware(request_handler)
        self.assertEqual(mid('foo'), 'foo')


class DjConfigUtilsTest(TestCase):

    def setUp(self):
        config._reset()

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

    def test_serialize(self):
        """
        Serializes complex objects
        """
        model_choice = ChoiceModel.objects.create(name='foo')
        self.assertEqual(
            utils.serialize(
                model_choice,
                forms.ModelChoiceField(None)),
            model_choice.pk)
        self.assertEqual(
            utils.serialize(
                ChoiceModel.objects.all(),
                forms.ModelMultipleChoiceField(None)),
            str([model_choice.pk]))

def login(test_case_instance, user=None, password=None):
    user = user or test_case_instance.user
    password = password or "bar"
    login_successful = test_case_instance.client.login(
        username=user.username,
        password=password)
    test_case_instance.assertTrue(login_successful)


User = get_user_model()


class BarConfigAdminForm(ConfigForm):

    bar_config_char = forms.CharField(initial="unique_BarConfigAdminForm")


class BazConfigAdminForm(ConfigForm):

    baz_config_char = forms.CharField(initial="unique_BazConfigAdminForm")


class DjConfigAdminTest(TestCase):

    def setUp(self):
        config._reset()
        djconfig.register(BarConfigAdminForm)
        djconfig.register(BazConfigAdminForm)
        self.user = User.objects.create_superuser(
            'foo', 'foo@bar.com', 'bar')

    def test_admin_change_list(self):
        login(self)
        response = self.client.get(
            reverse('admin:tests_barconfig_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], BarConfigAdminForm)
        self.assertEqual(response.context['app_label'], 'tests')
        self.assertContains(response, 'value="unique_BarConfigAdminForm"')

    def test_admin_change_list_post(self):
        login(self)
        response = self.client.post(
            reverse('admin:tests_barconfig_changelist'),
            {'bar_config_char': 'foobar'})
        expected_url = reverse('admin:tests_barconfig_changelist')
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEqual(config.bar_config_char, 'foobar')

    def test_admin_add(self):
        login(self)
        response = self.client.get(
            reverse('admin:tests_barconfig_add'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], BarConfigAdminForm)
        self.assertContains(response, 'value="unique_BarConfigAdminForm"')

    def test_admin_change_list_djconfig_foobar(self):
        login(self)
        response = self.client.get(
            reverse('admin:djconfig_foobarconfig_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], BarConfigAdminForm)
        self.assertEqual(response.context['app_label'], 'djconfig')
        self.assertContains(response, 'value="unique_BarConfigAdminForm"')

    def test_admin_change_list_baz(self):
        login(self)
        response = self.client.get(
            reverse('admin:tests_bazconfig_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], BazConfigAdminForm)
        self.assertEqual(response.context['app_label'], 'tests')
        self.assertContains(response, 'value="unique_BazConfigAdminForm"')

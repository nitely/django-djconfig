# -*- coding: utf-8 -*-

"""
This module allows to register a config into django's admin.

Usage::

    class FooConfigAdmin(djconfig.admin.ConfigAdmin):
        change_list_form = FooConfigForm


    class FooConfig(djconfig.admin.Config):
        app_label = 'djconfig'
        verbose_name_plural = 'foo config'
        slug = 'fooconfig'

    djconfig.admin.register(FooConfig, FooConfigAdmin)
"""

import re

from django.contrib import admin
from django.apps import apps
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.contrib.admin.options import csrf_protect_m
from django.contrib.admin import helpers
from django.core.exceptions import PermissionDenied
from django.conf.urls import url

from .forms import ConfigForm

__all__ = [
    'ConfigAdmin',
    'Config',
    'register']


class ConfigAdmin(admin.ModelAdmin):
    """
    A ``ConfigAdmin`` is subclass of \
    ``django.contrib.admin.ModelAdmin``.

    ``change_list_form`` class var must be set to a valid \
    ``djconfig.forms.ConfigForm`` subclass
    """
    change_list_template = 'admin/djconfig/change_list.html'
    change_list_form = None

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.module_name
        return [
            url(r'^$',
                self.admin_site.admin_view(self.changelist_view),
                name='%s_%s_changelist' % info),
            url(r'^$',
                self.admin_site.admin_view(self.changelist_view),
                name='%s_%s_add' % info),
        ]

    def get_changelist_form(self, request, **kwargs):
        return self.change_list_form

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        if not self.has_change_permission(request, None):
            raise PermissionDenied
        form_cls = self.get_changelist_form(request)
        form = form_cls()
        if request.method == 'POST':
            form = form_cls(data=request.POST, files=request.FILES)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('.')
        context = dict(
            self.admin_site.each_context(request),
            config_values=[],
            title=self.model._meta.verbose_name_plural,
            app_label=self.model._meta.app_label,
            opts=self.model._meta,
            form=form,
            media=self.media + form.media,
            icon_type='svg',
            adminform=helpers.AdminForm(
                form=form,
                fieldsets=[(None, {'fields': form.base_fields})],
                prepopulated_fields=self.get_prepopulated_fields(request))
        )
        request.current_app = self.admin_site.name
        return TemplateResponse(request, self.change_list_template, context)


class _ConfigMeta(object):
    app_label = ''
    object_name = ''
    model_name = module_name = ''
    verbose_name_plural = ''
    abstract = False
    swapped = False

    def get_ordered_objects(self):
        return False

    def get_change_permission(self):
        return 'change_djconfig_config'

    @property
    def app_config(self):
        return apps.get_app_config(self.app_label)


class Config(object):
    """
    A ``Config`` is akin to django's model ``Meta`` class.

    ``app_label`` must be a valid installed app, ``'djconfig'`` \
    may be used for every registered form, if they don't belong \
    in a particular app. ``verbose_name_plural`` is the title of \
    the admin's section link, it can be anything. The \
    (``app_label``, ``verbose_name_plural``, ``name``) must be \
    unique together across registered forms. \
    ``name`` is used as the link slug, and it \
    might be used in other places, valid chars are ``[a-zA-Z_]``
    """
    app_label = ''
    verbose_name_plural = ''
    name = ''


def register(conf, conf_admin, **options):
    """
    Register a new admin section.

    :param conf: A subclass of ``djconfig.admin.Config``
    :param conf_admin: A subclass of ``djconfig.admin.ConfigAdmin``
    :param options: Extra options passed to ``django.contrib.admin.site.register``
    """
    assert issubclass(conf_admin, ConfigAdmin), (
        'conf_admin is not a ConfigAdmin subclass')
    assert issubclass(
        getattr(conf_admin, 'change_list_form', None),
        ConfigForm), 'No change_list_form set'
    assert issubclass(conf, Config), (
        'conf is not a Config subclass')
    assert conf.app_label, 'No app_label set'
    assert conf.verbose_name_plural, 'No verbose_name_plural set'
    assert not conf.name or re.match(r"^[a-zA-Z_]+$", conf.name), (
        'Not a valid name. Valid chars are [a-zA-Z_]')
    config_class = type("Config", (), {})
    config_class._meta = type("Meta", (_ConfigMeta,), {
        'app_label': conf.app_label,
        'verbose_name_plural': conf.verbose_name_plural,
        'object_name': 'Config',
        'model_name': conf.name,
        'module_name': conf.name})
    admin.site.register([config_class], conf_admin, **options)

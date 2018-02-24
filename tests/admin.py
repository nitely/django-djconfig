# -*- coding: utf-8 -*-

from django.contrib import admin
from django.apps import apps
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.contrib.admin.options import csrf_protect_m
from django.contrib.admin import helpers
from django.core.exceptions import PermissionDenied
from django.conf.urls import url

from .tests import FooForm


class FooAdmin(admin.ModelAdmin):
    change_list_template = 'admin/djconfig/change_list.html'
    change_list_form = FooForm

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
            title=self.model._meta.app_config.verbose_name,
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


class Config(object):
    class Meta(object):
        app_label = 'djconfig'
        object_name = 'Config'
        model_name = module_name = 'config'
        verbose_name_plural = 'config'
        abstract = False
        swapped = False

        def get_ordered_objects(self):
            return False

        def get_change_permission(self):
            return 'change_%s' % self.model_name

        @property
        def app_config(self):
            return apps.get_app_config(self.app_label)

    _meta = Meta()


admin.site.register([Config], FooAdmin)

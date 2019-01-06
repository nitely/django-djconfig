# -*- coding: utf-8 -*-

from django.contrib import admin
import djconfig

from .tests import FooForm, BarForm, ChoiceModel


class FooAdmin(djconfig.admin.ConfigAdmin):
    change_list_form = FooForm


class FooConfig(djconfig.admin.Config):
    app_label = 'djconfig'
    verbose_name_plural = 'foo config'
    name = 'fooconfig'


class BarAdmin(djconfig.admin.ConfigAdmin):
    change_list_form = BarForm


class BarConfig(djconfig.admin.Config):
    app_label = 'tests'
    verbose_name_plural = 'bar config'
    name = 'barconfig'


class BazConfig(djconfig.admin.Config):
    app_label = 'tests'
    verbose_name_plural = 'baz config'
    name = 'bazconfig'


djconfig.admin.register(FooConfig, FooAdmin)
djconfig.admin.register(BarConfig, BarAdmin)
djconfig.admin.register(BazConfig, FooAdmin)
djconfig.register(FooForm)
djconfig.register(BarForm)


class ChoiceAdmin(admin.ModelAdmin):
    pass
admin.site.register(ChoiceModel, ChoiceAdmin)

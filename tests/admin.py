# -*- coding: utf-8 -*-

from django.contrib import admin
import djconfig

from .tests import (
    BarConfigAdminForm,
    BazConfigAdminForm,
    ChoiceModel)


class FooBarAdmin(djconfig.admin.ConfigAdmin):
    change_list_form = BarConfigAdminForm


class FooBarConfig(djconfig.admin.Config):
    app_label = 'djconfig'
    verbose_name_plural = 'foo bar config'
    name = 'foobarconfig'


class BarAdmin(djconfig.admin.ConfigAdmin):
    change_list_form = BarConfigAdminForm


class BarConfig(djconfig.admin.Config):
    app_label = 'tests'
    verbose_name_plural = 'bar config'
    name = 'barconfig'


class BazAdmin(djconfig.admin.ConfigAdmin):
    change_list_form = BazConfigAdminForm


class BazConfig(djconfig.admin.Config):
    app_label = 'tests'
    verbose_name_plural = 'baz config'
    name = 'bazconfig'


djconfig.admin.register(FooBarConfig, FooBarAdmin)
djconfig.admin.register(BarConfig, BarAdmin)
djconfig.admin.register(BazConfig, BazAdmin)


class ChoiceAdmin(admin.ModelAdmin):
    pass
admin.site.register(ChoiceModel, ChoiceAdmin)

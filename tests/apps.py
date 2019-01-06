# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig
import djconfig

class Tests(AppConfig):

    name = 'tests'
    verbose_name = "Tests"
    label = 'tests'

    def ready(self):
        # needed for using Admin in runserver
        from .tests import BarConfigAdminForm, BazConfigAdminForm
        djconfig.register(BarConfigAdminForm)
        djconfig.register(BazConfigAdminForm)

# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig


class DjConfig(AppConfig):

    default_auto_field = 'django.db.models.AutoField'
    name = 'djconfig'
    verbose_name = "Config"
    label = 'djconfig'

# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils import timezone
from django.apps import apps
from django.conf import settings

from . import conf
from .settings import DJCONFIG_CONFIG_MODEL

CONFIG_MODEL = getattr(settings, 'DJCONFIG_CONFIG_MODEL', DJCONFIG_CONFIG_MODEL)


class ConfigForm(forms.Form):
    """
    Base class for every registered config form.
    """
    def __init__(self, *args, **kwargs):
        pre_load_config = kwargs.pop('pre_load_config', True)
        super(ConfigForm, self).__init__(*args, **kwargs)

        if pre_load_config:  # Do not pre-load when reloading the config, to avoid infinite recursion
            self.initial.update({
                field_name: getattr(conf.config, field_name)
                for field_name in self.fields
                if hasattr(conf.config, field_name)
            })

    def save(self):
        data = self.cleaned_data
        data['_updated_at'] = timezone.now()
        ConfigModel = apps.get_model(CONFIG_MODEL)

        for field_name, value in data.items():
            # TODO: use update_or_create
            count = ConfigModel.objects\
                .filter(key=field_name)\
                .update(value=value)

            if not count:
                ConfigModel.objects.create(key=field_name, value=value)

        conf.config._reload()

# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils import timezone
from django.apps import apps

from . import conf


class ConfigForm(forms.Form):
    """
    Base class for every registered config form.
    """
    def __init__(self, *args, **kwargs):
        super(ConfigForm, self).__init__(*args, **kwargs)

        self.initial.update({
            field_name: getattr(conf.config, field_name)
            for field_name in self.fields
            if hasattr(conf.config, field_name)
        })

    def save(self):
        data = self.cleaned_data
        data['_updated_at'] = timezone.now()
        ConfigModel = apps.get_model('djconfig.Config')

        for field_name, value in data.items():
            # TODO: use update_or_create
            count = ConfigModel.objects\
                .filter(key=field_name)\
                .update(value=value)

            if not count:
                ConfigModel.objects.create(key=field_name, value=value)

        conf.config._reload()

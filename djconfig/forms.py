# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils import timezone

from . import conf
from . import models


class ConfigForm(forms.Form):
    """
    Base class for every registered config form.
    """
    def __init__(self, *args, **kwargs):
        super(ConfigForm, self).__init__(*args, **kwargs)

        if conf.config._is_loaded:
            initial_config = {field_name: getattr(conf.config, field_name)
                              for field_name in self.fields}
            initial_config.update(self.initial)
            self.initial = initial_config


    def save(self):
        data = self.cleaned_data
        data['_updated_at'] = timezone.now()

        for field_name, value in data.items():
            # TODO: use update_or_create
            count = models.Config.objects\
                .filter(key=field_name)\
                .update(value=value)

            if not count:
                models.Config.objects.create(key=field_name, value=value)

        conf.config._reload()

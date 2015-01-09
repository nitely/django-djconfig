#-*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils import timezone

from . import conf
from . import registry
from . import models


class ConfigForm(forms.Form):
    """
    Base class for every registered config form.

    :param initial: This parameter will be ignored. The cache is used to populate it.
    :type initial: dict.
    """
    def __init__(self, *args, **kwargs):
        super(ConfigForm, self).__init__(*args, **kwargs)

        self.initial = {field_name: getattr(conf.config, field_name)
                        for field_name in self.fields}

    def save(self):
        data = self.cleaned_data
        data['_updated_at'] = timezone.now()

        for field_name, value in data.items():
            count = models.Config.objects.filter(key=field_name).update(value=value)

            if not count:
                models.Config.objects.create(key=field_name, value=value)

        registry.load()

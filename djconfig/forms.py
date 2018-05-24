# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils import timezone
from django.apps import apps

from . import conf
from . import utils


class ConfigForm(conf._ConfigFormBase):
    """
    Base class for every registered config form.\
    It behaves like a regular form.

    Inherits from :py:class:`django.forms.Form`.\
    The :py:attr:`initial` attr will be updated with the\
    config values if any.

    All form fields implementing this, should have a unique\
    name to avoid clashing with other registered forms,\
    prefixing them with the app name is a good practice.

    :param args: Positional parameters passed to parent class
    :param kwargs: Keyword parameters passed to parent class
    """
    def __init__(self, *args, **kwargs):
        super(ConfigForm, self).__init__(*args, **kwargs)

        self.initial.update({
            name: getattr(conf.config, name)
            for name in self.fields
            if hasattr(conf.config, name)})

    def save(self):
        """
        Save the config with the cleaned data,\
        update the last modified date so\
        the config is reloaded on other process/nodes.\
        Reload the config so it can be called right away.
        """
        assert self.__class__ in conf.config._registry,\
            '%(class_name)s is not registered' % {
                'class_name': self.__class__.__name__
            }

        ConfigModel = apps.get_model('djconfig.Config')

        for field_name, value in self.cleaned_data.items():
            value = utils.serialize(
                value=value,
                field=self.fields.get(field_name, None))
            # TODO: use update_or_create
            count = (ConfigModel.objects
                .filter(key=field_name)
                .update(value=value))
            if not count:
                ConfigModel.objects.create(
                    key=field_name,
                    value=value)

        count = (ConfigModel.objects
            .filter(key='_updated_at')
            .update(value=str(timezone.now())))
        if not count:
            ConfigModel.objects.create(
                key='_updated_at',
                value=str(timezone.now()))

        conf.config._reload()

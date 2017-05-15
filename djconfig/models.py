# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

__all__ = ['Config', ]


class Config(models.Model):

    key = models.CharField(max_length=75, unique=True)
    value = models.TextField(null=True, blank=True)

    @classmethod
    def updated_at(cls):
        return (dict(
            cls.objects
                .filter(key='_updated_at')
                .values_list('key', 'value'))
            .get('_updated_at'))

    @classmethod
    def as_dict(cls):
        return dict(
            cls.objects
                .all()
                .values_list('key', 'value'))

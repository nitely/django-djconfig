# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

__all__ = ['Config', ]


class Config(models.Model):

    key = models.CharField(max_length=75, unique=True)
    value = models.TextField(null=True, blank=True)

    @classmethod
    def updated_at(cls):
        query = (
            cls.objects
                .filter(key='_updated_at')
                .values_list('key', 'value'))

        return dict(query).get('_updated_at')

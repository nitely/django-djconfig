# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

__all__ = ['Config']


class Config(models.Model):

    key = models.CharField(max_length=75, unique=True)
    value = models.TextField(null=True, blank=True)

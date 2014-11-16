#-*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings


BACKEND = getattr(settings, 'DJC_BACKEND', 'default')
PREFIX = getattr(settings, 'DJC_PREFIX', 'djc')
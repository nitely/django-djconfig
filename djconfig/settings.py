#-*- coding: utf-8 -*-

from django.conf import settings


BACKEND = getattr(settings, 'DJC_BACKEND', 'default')
PREFIX = getattr(settings, 'DJC_PREFIX', 'djc')
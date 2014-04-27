#-*- coding: utf-8 -*-

from django.conf import settings


BACKEND = getattr(settings, 'DJC_BACKEND', 'default')
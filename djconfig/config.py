#-*- coding: utf-8 -*-

from django.core.cache import get_cache
from django.conf import settings

from djconfig.settings import DJC_BACKEND

BACKEND = getattr(settings, 'DJC_BACKEND', DJC_BACKEND)


class Config(object):

    def __init__(self):
        self._cache = get_cache(BACKEND)

    def __getattr__(self, key):
        return self._cache.get(key)
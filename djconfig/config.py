#-*- coding: utf-8 -*-

from django.core.cache import get_cache

from djconfig.settings import BACKEND


class Config(object):

    def __init__(self):
        self._cache = get_cache(BACKEND)

    def __getattr__(self, key):
        return self._cache.get(key)
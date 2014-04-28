#-*- coding: utf-8 -*-

from django.core.cache import get_cache

from djconfig.settings import BACKEND, PREFIX


class Config(object):

    def __init__(self):
        self._cache = get_cache(BACKEND)

    def __getattr__(self, key):
        key = u"%s:%s" % (PREFIX, key)
        return self._cache.get(key)
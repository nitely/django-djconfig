#-*- coding: utf-8 -*-

from django.core.cache import get_cache

import djconfig


class Config(object):

    def __init__(self):
        self._cache = get_cache(djconfig.BACKEND)

    def __getattr__(self, key):
        return self._cache.get(djconfig.prefixer(key))
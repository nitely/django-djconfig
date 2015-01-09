#-*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.cache import get_cache

from . import registry
from . import settings
from .utils import prefixer


class Config(object):

    def __init__(self):
        self._cache = get_cache(settings.BACKEND)
        self._is_loaded = False

    def __getattr__(self, key):
        self._lazy_load()
        return self._cache.get(prefixer(key))

    def _set(self, key, value):
        self._lazy_load()
        self._cache.set(prefixer(key), value)

    def _reset(self):
        self._is_loaded = False

    def _lazy_load(self):
        if self._is_loaded:
            return

        self._is_loaded = True
        registry.load()


config = Config()

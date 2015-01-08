#-*- coding: utf-8 -*-

from django.core.cache.backends.locmem import LocMemCache


class TestingCache(LocMemCache):

    def clear(self):
        pass

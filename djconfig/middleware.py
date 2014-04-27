#-*- coding: utf-8 -*-

from django.conf import settings

import djconfig
from djconfig.settings import DJC_BACKEND

__all__ = ['DjConfigLocMemMiddleware', ]


BACKEND = getattr(settings, 'DJC_BACKEND', DJC_BACKEND)


class DjConfigLocMemMiddleware(object):
    """
    Populates the cache using the database
    required by the LocalMem backend
    """
    def process_request(self, request):
        self.check_backend()
        djconfig.load()

    def check_backend(self):
        backend = settings.CACHES[BACKEND]

        if not backend['BACKEND'].endswith(".LocMemCache"):
            raise ValueError("DjConfigLocMemMiddleware requires LocMemCache as cache")
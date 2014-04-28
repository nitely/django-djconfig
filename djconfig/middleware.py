#-*- coding: utf-8 -*-

from django.conf import settings

import djconfig

__all__ = ['DjConfigLocMemMiddleware', ]


class DjConfigLocMemMiddleware(object):
    """
    Populates the cache using the database
    required by the LocalMem backend
    """
    def process_request(self, request):
        self.check_backend()
        djconfig.load()

    def check_backend(self):
        backend = settings.CACHES[djconfig.BACKEND]

        if not backend['BACKEND'].endswith(".LocMemCache"):
            raise ValueError("DjConfigLocMemMiddleware requires LocMemCache as cache")
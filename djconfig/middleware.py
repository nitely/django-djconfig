#-*- coding: utf-8 -*-

import djconfig

__all__ = ['DjConfigMiddleware', ]


class DjConfigMiddleware(object):
    """
    Populates the cache using the database
    required by the LocalMem backend
    """
    def process_request(self, request):
        djconfig.load()
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from . import conf

__all__ = ['DjConfigMiddleware', ]


class DjConfigMiddleware(object):
    """
    Populate the cache using the database.
    Reload the cache *only* if the database has changed.
    """
    def process_request(self, request):
        conf.reload_maybe()


# Backward compatibility
DjConfigLocMemMiddleware = DjConfigMiddleware

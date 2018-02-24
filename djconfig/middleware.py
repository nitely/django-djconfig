# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from . import conf

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:  # Django < 1.10
    MiddlewareMixin = object


__all__ = ['DjConfigMiddleware']


class DjConfigMiddleware(MiddlewareMixin):
    """
    Populate the cache using the database.\
    Reload the cache *only* if it is not up\
    to date with the config model
    """
    def process_request(self, request):
        conf.reload_maybe()


# Backward compatibility
DjConfigLocMemMiddleware = DjConfigMiddleware

#-*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings as django_settings

from . import conf
from . import registry
from . import models
from . import settings

__all__ = ['DjConfigLocMemMiddleware', ]


class DjConfigLocMemMiddleware(object):
    """
    Populates the cache using the database
    required by the LocalMem backend
    """
    def process_request(self, request):
        self.check_backend()
        self.reload()

    def check_backend(self):
        backend = django_settings.CACHES[settings.BACKEND]

        if not backend['BACKEND'].endswith((".LocMemCache", ".TestingCache")):
            raise ValueError("DjConfigLocMemMiddleware requires LocMemCache as cache")

    def reload(self):
        """
        This reloads the cache *only* if the database has changed.
        """
        data = dict(models.Config.objects.filter(key="_updated_at").values_list('key', 'value'))

        if data.get('_updated_at') != conf.config._updated_at:
            registry.load()

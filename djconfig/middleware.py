#-*- coding: utf-8 -*-

from django.conf import settings

import djconfig
from djconfig.models import Config as ConfigModel

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
        backend = settings.CACHES[djconfig.BACKEND]

        if not backend['BACKEND'].endswith(".LocMemCache"):
            raise ValueError("DjConfigLocMemMiddleware requires LocMemCache as cache")

    def reload(self):
        """
        This reloads the cache *only* if the database has changed.
        """
        data = dict(ConfigModel.objects.filter(key="_updated_at").values_list('key', 'value'))

        if data.get('_updated_at') != djconfig.config._updated_at:
            djconfig.load()
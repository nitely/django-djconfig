# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from . import conf
from . import models

__all__ = ['DjConfigMiddleware', ]


class DjConfigMiddleware(object):
    """
    Populates the cache using the database.
    """
    def process_request(self, request):
        self.reload()

    def reload(self):
        """
        Reload the cache *only* if the database has changed.
        """
        data = dict(models.Config.objects
                    .filter(key='_updated_at')
                    .values_list('key', 'value'))

        if data.get('_updated_at') != conf.config._updated_at:
            conf.config._reload()


# Backward compatibility
DjConfigLocMemMiddleware = DjConfigMiddleware
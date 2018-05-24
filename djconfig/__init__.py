# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from . import conf


default_app_config = 'djconfig.apps.DjConfig'

config = conf.config
register = conf.register
reload_maybe = conf.reload_maybe

__version__ = "0.7.0"
__all__ = ['config', 'register', 'reload_maybe']

# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from . import conf
from . import admin

config = conf.config
register = conf.register
reload_maybe = conf.reload_maybe

__version__ = "0.11.0"
__all__ = ['config', 'register', 'reload_maybe', 'admin']

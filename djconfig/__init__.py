#-*- coding: utf-8 -*-

from __future__ import unicode_literals

from djconfig.config import config
from djconfig.registry import register, load
from djconfig.settings import BACKEND

__version__ = "0.1.8"
__all__ = ['config', 'register', 'load', 'BACKEND']

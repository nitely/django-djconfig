#-*- coding: utf-8 -*-

from __future__ import unicode_literals

from .conf import config
from .registry import register
from .settings import BACKEND

__version__ = "0.1.8"
__all__ = ['config', 'register', 'BACKEND']
